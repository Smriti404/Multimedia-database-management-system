from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import sqlite3
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'multimedia_db_secret'

# Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {
    'image': {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'},
    'audio': {'mp3', 'wav', 'ogg', 'flac'},
    'video': {'mp4', 'avi', 'mov', 'mkv', 'webm'},
    'text':  {'txt', 'pdf', 'doc', 'docx'}
}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB limit

DB_PATH = 'database/multimedia.db'

# ─── Database Setup ───────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs('database', exist_ok=True)
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS media (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name   TEXT    NOT NULL,
            file_type   TEXT    NOT NULL,
            file_path   TEXT    NOT NULL,
            file_size   INTEGER,
            tags        TEXT,
            description TEXT,
            upload_date TEXT    NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_media_type(filename):
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    for mtype, exts in ALLOWED_EXTENSIONS.items():
        if ext in exts:
            return mtype
    return None

def allowed_file(filename):
    return get_media_type(filename) is not None

def human_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes/1024:.1f} KB"
    else:
        return f"{size_bytes/(1024**2):.1f} MB"

app.jinja_env.filters['human_size'] = human_size

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    conn = get_db()
    stats = {
        'total':  conn.execute("SELECT COUNT(*) FROM media").fetchone()[0],
        'image':  conn.execute("SELECT COUNT(*) FROM media WHERE file_type='image'").fetchone()[0],
        'audio':  conn.execute("SELECT COUNT(*) FROM media WHERE file_type='audio'").fetchone()[0],
        'video':  conn.execute("SELECT COUNT(*) FROM media WHERE file_type='video'").fetchone()[0],
        'text':   conn.execute("SELECT COUNT(*) FROM media WHERE file_type='text'").fetchone()[0],
    }
    recent = conn.execute("SELECT * FROM media ORDER BY id DESC LIMIT 6").fetchall()
    conn.close()
    return render_template('index.html', stats=stats, recent=recent)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected.', 'error')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected.', 'error')
            return redirect(request.url)
        if not allowed_file(file.filename):
            flash('File type not supported. Allowed: images, audio, video, text/docs.', 'error')
            return redirect(request.url)

        media_type = get_media_type(file.filename)
        filename   = secure_filename(file.filename)
        # Avoid overwrites
        base, ext = os.path.splitext(filename)
        timestamp  = datetime.now().strftime('%Y%m%d%H%M%S')
        filename   = f"{base}_{timestamp}{ext}"

        save_dir  = os.path.join(app.config['UPLOAD_FOLDER'], f"{media_type}s")
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, filename)
        file.save(save_path)

        file_size   = os.path.getsize(save_path)
        tags        = request.form.get('tags', '').strip()
        description = request.form.get('description', '').strip()
        upload_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db_path     = f"static/uploads/{media_type}s/{filename}"

        conn = get_db()
        conn.execute(
            "INSERT INTO media (file_name, file_type, file_path, file_size, tags, description, upload_date) VALUES (?,?,?,?,?,?,?)",
            (filename, media_type, db_path, file_size, tags, description, upload_date)
        )
        conn.commit()
        conn.close()

        flash(f'File "{filename}" uploaded successfully!', 'success')
        return redirect(url_for('browse'))

    return render_template('upload.html')


@app.route('/browse')
def browse():
    file_type   = request.args.get('type', 'all')
    search      = request.args.get('search', '').strip()
    sort        = request.args.get('sort', 'newest')

    conn  = get_db()
    query = "SELECT * FROM media WHERE 1=1"
    params = []

    if file_type != 'all':
        query  += " AND file_type = ?"
        params.append(file_type)

    if search:
        query  += " AND (file_name LIKE ? OR tags LIKE ? OR description LIKE ?)"
        params += [f'%{search}%', f'%{search}%', f'%{search}%']

    if sort == 'oldest':
        query += " ORDER BY id ASC"
    elif sort == 'name':
        query += " ORDER BY file_name ASC"
    elif sort == 'size':
        query += " ORDER BY file_size DESC"
    else:
        query += " ORDER BY id DESC"

    files = conn.execute(query, params).fetchall()
    conn.close()
    return render_template('browse.html', files=files, file_type=file_type,
                           search=search, sort=sort, count=len(files))


@app.route('/delete/<int:file_id>', methods=['POST'])
def delete_file(file_id):
    conn = get_db()
    row  = conn.execute("SELECT * FROM media WHERE id=?", (file_id,)).fetchone()
    if row:
        full_path = row['file_path']
        if os.path.exists(full_path):
            os.remove(full_path)
        conn.execute("DELETE FROM media WHERE id=?", (file_id,))
        conn.commit()
        flash('File deleted successfully.', 'success')
    conn.close()
    return redirect(url_for('browse'))


@app.route('/view/<int:file_id>')
def view_file(file_id):
    conn = get_db()
    f    = conn.execute("SELECT * FROM media WHERE id=?", (file_id,)).fetchone()
    conn.close()
    if not f:
        flash('File not found.', 'error')
        return redirect(url_for('browse'))
    return render_template('view_file.html', f=f)


@app.route('/query', methods=['GET', 'POST'])
def query_page():
    results = []
    sql     = ''
    error   = ''
    if request.method == 'POST':
        raw = request.form.get('sql', '').strip()
        sql = raw
        # Only allow SELECT queries for safety
        if not raw.lower().startswith('select'):
            error = 'Only SELECT queries are allowed.'
        else:
            try:
                conn    = get_db()
                cursor  = conn.execute(raw)
                results = cursor.fetchall()
                conn.close()
            except Exception as e:
                error = str(e)
    return render_template('query.html', results=results, sql=sql, error=error)


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)

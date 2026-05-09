"""
Run this script once to initialize the database and add sample data for testing.
Usage: python init_db.py
"""
import sqlite3, os

os.makedirs('database', exist_ok=True)
os.makedirs('static/uploads/images', exist_ok=True)
os.makedirs('static/uploads/audios', exist_ok=True)
os.makedirs('static/uploads/videos', exist_ok=True)
os.makedirs('static/uploads/texts', exist_ok=True)

conn = sqlite3.connect('database/multimedia.db')
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

sample_data = [
    ('sunset_photo.jpg',   'image', 'static/uploads/images/sunset_photo.jpg',   204800, 'nature,sunset,sky',     'A beautiful sunset photo',            '2025-03-01 10:00:00'),
    ('background.png',     'image', 'static/uploads/images/background.png',     102400, 'wallpaper,abstract',    'Desktop background image',            '2025-03-02 11:00:00'),
    ('lecture_notes.txt',  'text',  'static/uploads/texts/lecture_notes.txt',   5120,   'lecture,notes,dbms',    'DBMS lecture notes',                  '2025-03-03 09:30:00'),
    ('song_sample.mp3',    'audio', 'static/uploads/audios/song_sample.mp3',    3145728,'music,sample,audio',    'A sample music track',                '2025-03-04 14:00:00'),
    ('demo_video.mp4',     'video', 'static/uploads/videos/demo_video.mp4',     10485760,'demo,tutorial,video',  'A short demo video',                  '2025-03-05 16:00:00'),
    ('project_report.pdf', 'text',  'static/uploads/texts/project_report.pdf',  512000, 'report,pdf,academic',   'Sample project report document',      '2025-03-06 08:00:00'),
    ('forest_image.jpg',   'image', 'static/uploads/images/forest_image.jpg',   307200, 'nature,forest,trees',   'Forest landscape image',              '2025-03-07 12:00:00'),
    ('podcast.mp3',        'audio', 'static/uploads/audios/podcast.mp3',        5242880,'podcast,talk,english',  'An English podcast episode',          '2025-03-08 15:00:00'),
]

c.executemany(
    "INSERT INTO media (file_name, file_type, file_path, file_size, tags, description, upload_date) VALUES (?,?,?,?,?,?,?)",
    sample_data
)
conn.commit()
conn.close()
print("Database initialized with sample records.")
print("Now run: python app.py")

# Multimedia Database System
### DBMS Lab Project — IIT Kharagpur
**Group Members:**
- Smriti — 23CS30053
- Sangeeta — 23CS30047

---

## About
A web-based Multimedia Database that stores, manages, and queries text, images, audio, and video files using SQLite and Flask.

## Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Initialize the database (run once)
python init_db.py

# 3. Start the app
python app.py

# 4. Open in browser
http://localhost:5000
```

## Features
- Upload images, audio, video, and text/document files
- Browse all media with filter by type, search by name/tag
- View individual files (preview for images, playback for audio/video)
- Delete files
- Run raw SELECT SQL queries via the Query Console
- Stats dashboard on home page

## Project Structure
```
multimedia_db/
├── app.py              # Main Flask application
├── init_db.py          # Database initialization script
├── requirements.txt    # Python dependencies
├── database/           # SQLite database file (auto-created)
├── static/
│   ├── css/style.css   # Stylesheet
│   └── uploads/        # Uploaded files stored here
│       ├── images/
│       ├── audios/
│       ├── videos/
│       └── texts/
└── templates/          # HTML templates
    ├── base.html
    ├── index.html
    ├── upload.html
    ├── browse.html
    ├── view_file.html
    └── query.html
```

## Database Schema
```sql
CREATE TABLE media (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    file_name   TEXT    NOT NULL,
    file_type   TEXT    NOT NULL,   -- image / audio / video / text
    file_path   TEXT    NOT NULL,
    file_size   INTEGER,
    tags        TEXT,
    description TEXT,
    upload_date TEXT    NOT NULL
);
```

## Sample SQL Queries
```sql
-- Get all files
SELECT * FROM media;

-- Filter by type
SELECT * FROM media WHERE file_type = 'image';

-- Search by tag
SELECT * FROM media WHERE tags LIKE '%music%';

-- Count by type
SELECT file_type, COUNT(*) as count FROM media GROUP BY file_type;

-- Largest files
SELECT * FROM media ORDER BY file_size DESC LIMIT 5;
```

import os
import sqlite3
from dotenv import load_dotenv
from database import engine, Base, SessionLocal
import models

load_dotenv()

def migrate():
    print("Connecting to target database and ensuring tables exist...")
    Base.metadata.create_all(bind=engine)
    
    sqlite_file = os.path.join(os.path.dirname(__file__), "music_app.db")
    if not os.path.exists(sqlite_file):
        print(f"Error: {sqlite_file} not found!")
        return

    print("Reading songs from local SQLite database...")
    conn = sqlite3.connect(sqlite_file)
    cursor = conn.cursor()
    cursor.execute("SELECT id, song_name, artist, thumbnail_url, audio_url, hex_code FROM songs")
    rows = cursor.fetchall()
    conn.close()

    print(f"Found {len(rows)} songs to migrate.")
    
    db = SessionLocal()
    try:
        migrated_count = 0
        for row in rows:
            song_id, song_name, artist, thumbnail_url, audio_url, hex_code = row
            existing = db.query(models.Song).filter(models.Song.id == song_id).first()
            if not existing:
                new_song = models.Song(
                    id=song_id,
                    song_name=song_name,
                    artist=artist,
                    thumbnail_url=thumbnail_url,
                    audio_url=audio_url,
                    hex_code=hex_code
                )
                db.add(new_song)
                migrated_count += 1
        
        db.commit()
        print(f"Successfully migrated {migrated_count} songs into your Supabase database!")
    except Exception as e:
        db.rollback()
        print(f"Migration failed with error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate()

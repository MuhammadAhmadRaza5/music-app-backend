import os
import yt_dlp
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from database import SessionLocal
import models
import uuid

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

def populate_top_bollywood_songs():
    db = SessionLocal()
    
    songs_to_download = [
        "Tujh Mein Rab Dikhta Hai audio",
        "Kabira Yeh Jawaani Hai Deewani audio",
        "Gerua Dilwale audio",
        "Agar Tum Saath Ho audio",
        "Zaalima Raees audio",
        "Kal Ho Naa Ho Title Track audio",
        "Hawayein Jab Harry Met Sejal audio",
        "Tera Ban Jaunga Kabir Singh audio",
        "Subhanallah Yeh Jawaani Hai Deewani audio",
        "Jeene Laga Hoon Ramaiya Vastavaiya audio"
    ]
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(id)s.%(ext)s',
        'quiet': True,
        'noplaylist': True,
        'extract_flat': False,
        'match_filter': yt_dlp.utils.match_filter_func("duration < 400"),
    }
    
    for search_query in songs_to_download:
        print(f"Searching YouTube for '{search_query}'...")
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                search_results = ydl.extract_info(f"ytsearch1:{search_query}", download=False)
                
                if 'entries' not in search_results or not search_results['entries']:
                    print(f"No results found for {search_query}.")
                    continue

                entry = search_results['entries'][0]
                if entry is None:
                    continue
                    
                song_name = entry.get('title', 'Unknown Title')
                artist = entry.get('uploader', 'Unknown Artist')
                thumbnail_url = entry.get('thumbnail', '')
                video_url = entry.get('webpage_url', '')
                
                safe_song_name = song_name.encode('ascii', 'ignore').decode('ascii')
                safe_artist = artist.encode('ascii', 'ignore').decode('ascii')
                print(f"\nProcessing: {safe_song_name} by {safe_artist}")
                
                # Check if song already exists in DB
                existing_song = db.query(models.Song).filter(models.Song.song_name == song_name).first()
                if existing_song:
                    print(f"Song '{safe_song_name}' already exists in database. Skipping.")
                    continue
                    
                print("Downloading audio...")
                info = ydl.extract_info(video_url, download=True)
                file_path = ydl.prepare_filename(info)
                
                print(f"Uploading {file_path} to Cloudinary...")
                audio_result = cloudinary.uploader.upload(
                    file_path,
                    resource_type="auto",
                    folder="music_app/songs",
                )
                
                print("Uploading thumbnail...")
                # We can pass the remote thumbnail URL directly to Cloudinary
                thumb_result = cloudinary.uploader.upload(
                    thumbnail_url,
                    resource_type="image",
                    folder="music_app/thumbnails",
                )
                
                print("Saving to database...")
                new_song = models.Song(
                    song_name=song_name,
                    artist=artist,
                    thumbnail_url=thumb_result["secure_url"],
                    audio_url=audio_result["secure_url"],
                    hex_code="111111", # Default dark theme color
                )
                db.add(new_song)
                db.commit()
                print("Success!")
                
                # Clean up local file
                if os.path.exists(file_path):
                    os.remove(file_path)
                    
        except Exception as e:
            print(f"Error searching or processing {search_query}: {e}")
                
    db.close()
    print("\nFinished populating songs!")

if __name__ == "__main__":
    populate_top_bollywood_songs()

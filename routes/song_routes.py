import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from schemas import SongResponse, FavoriteResponse
from database import get_db
import models
import auth

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

router = APIRouter()


def get_current_user(token: str, db: Session):
    user_id = auth.decode_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


@router.post("/upload", response_model=SongResponse, status_code=status.HTTP_201_CREATED)
async def upload_song(
    song: UploadFile = File(...),
    thumbnail: UploadFile = File(...),
    artist: str = Form(...),
    song_name: str = Form(...),
    hex_code: str = Form(...),
    token: str = Form(...),
    db: Session = Depends(get_db),
):
    current_user = get_current_user(token, db)

    # Upload audio to Cloudinary
    audio_result = cloudinary.uploader.upload(
        song.file,
        resource_type="auto",
        folder="music_app/songs",
    )

    # Upload thumbnail to Cloudinary
    thumbnail_result = cloudinary.uploader.upload(
        thumbnail.file,
        resource_type="image",
        folder="music_app/thumbnails",
    )

    new_song = models.Song(
        song_name=song_name,
        artist=artist,
        thumbnail_url=thumbnail_result["secure_url"],
        audio_url=audio_result["secure_url"],
        hex_code=hex_code,
    )
    db.add(new_song)
    db.commit()
    db.refresh(new_song)
    return new_song


@router.get("/list", response_model=list[SongResponse])
def list_songs(token: str, db: Session = Depends(get_db)):
    get_current_user(token, db)
    songs = db.query(models.Song).all()
    return songs


@router.post("/favorite", response_model=FavoriteResponse)
def favorite_song(song_id: str, token: str, db: Session = Depends(get_db)):
    current_user = get_current_user(token, db)

    song = db.query(models.Song).filter(models.Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    existing = (
        db.query(models.Favorite)
        .filter(models.Favorite.user_id == current_user.id, models.Favorite.song_id == song_id)
        .first()
    )
    if existing:
        # Un-favorite
        db.delete(existing)
        db.commit()
        return FavoriteResponse(message="Removed from favorites")
    else:
        # Favorite
        fav = models.Favorite(user_id=current_user.id, song_id=song_id)
        db.add(fav)
        db.commit()
        db.refresh(fav)
        return FavoriteResponse(message="Added to favorites", id=fav.id)


@router.get("/search", response_model=list[SongResponse])
def search_songs(query: str, token: str, db: Session = Depends(get_db)):
    get_current_user(token, db)
    search_query = f"%{query}%"
    songs = db.query(models.Song).filter(
        models.Song.song_name.ilike(search_query) | models.Song.artist.ilike(search_query)
    ).all()
    return songs

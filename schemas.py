from pydantic import BaseModel, EmailStr
from typing import List, Optional


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class FavoriteSongResponse(BaseModel):
    id: str
    song_id: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    token: str
    favorites: List[FavoriteSongResponse] = []

    class Config:
        from_attributes = True


class SongCreate(BaseModel):
    song_name: str
    artist: str
    hex_code: str


class SongResponse(BaseModel):
    id: str
    song_name: str
    artist: str
    thumbnail_url: str
    audio_url: str
    hex_code: str

    class Config:
        from_attributes = True


class FavoriteResponse(BaseModel):
    message: str
    id: Optional[str] = None

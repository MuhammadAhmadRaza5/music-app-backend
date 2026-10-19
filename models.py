from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
import uuid
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    favorites = relationship("Favorite", back_populates="user")


class Song(Base):
    __tablename__ = "songs"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    song_name = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    thumbnail_url = Column(String, nullable=False)
    audio_url = Column(String, nullable=False)
    hex_code = Column(String, nullable=False)

    favorited_by = relationship("Favorite", back_populates="song")


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    song_id = Column(String, ForeignKey("songs.id"), nullable=False)

    user = relationship("User", back_populates="favorites")
    song = relationship("Song", back_populates="favorited_by")

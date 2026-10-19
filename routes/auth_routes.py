from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas import UserCreate, UserLogin, UserResponse, FavoriteSongResponse
from database import get_db
import models
import auth
from datetime import timedelta

router = APIRouter()


def _build_user_response(db_user, token: str) -> dict:
    favorites = [
        FavoriteSongResponse(id=fav.id, song_id=fav.song_id)
        for fav in db_user.favorites
    ]
    return {
        "id": db_user.id,
        "name": db_user.name,
        "email": db_user.email,
        "token": token,
        "favorites": favorites,
    }


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(name=user.name, email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = auth.create_access_token(
        data={"sub": new_user.id},
        expires_delta=timedelta(days=30),
    )
    return _build_user_response(new_user, token)


@router.post("/login", response_model=UserResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not auth.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    token = auth.create_access_token(
        data={"sub": db_user.id},
        expires_delta=timedelta(days=30),
    )
    return _build_user_response(db_user, token)


@router.get("/tokenIsValid")
def token_is_valid(token: str, db: Session = Depends(get_db)):
    user_id = auth.decode_token(token)
    if user_id is None:
        return {"isValid": False}
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return {"isValid": False}

    new_token = auth.create_access_token(
        data={"sub": db_user.id},
        expires_delta=timedelta(days=30),
    )
    return {
        "isValid": True,
        "user": _build_user_response(db_user, new_token),
    }

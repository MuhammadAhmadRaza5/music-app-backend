import sys
sys.modules['antigravity'] = None

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes import auth_routes, song_routes

# Create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Music App API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])
app.include_router(song_routes.router, prefix="/song", tags=["Songs"])


@app.get("/")
def read_root():
    return {"message": "Welcome to the Music App API"}

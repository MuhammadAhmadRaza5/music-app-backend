# Music App Backend API

FastAPI backend with PostgreSQL and Cloudinary for the Music Streaming Flutter application.

## Features
- **FastAPI** high-performance REST API
- **SQLAlchemy** ORM with PostgreSQL (Supabase) and SQLite support
- **JWT Authentication** (Sign up, Log in, Current user session)
- **Songs & Favorites** management
- **Cloudinary** integration for audio streaming and album artwork

## Setup & Local Development
1. Create a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate   # Windows
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the development server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

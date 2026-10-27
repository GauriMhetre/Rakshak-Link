"""Vercel serverless entrypoint for FastAPI backend."""
from app.main import app

# Vercel requires the ASGI app to be exported as 'app'

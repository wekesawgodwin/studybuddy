import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"PORT environment variable: {os.environ.get('PORT', 'NOT SET')}")

app = FastAPI(
    title="StudyBuddy API",
    description="Backend API for the StudyBuddy learning platform",
    version="1.0.0",
)

allowed_origins_raw = os.environ.get(
    "ALLOWED_ORIGINS",
    "http://localhost:5173"
)
allowed_origins = [origin.strip() for origin in allowed_origins_raw.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}

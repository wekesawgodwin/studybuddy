import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth    # import the auth router

# Configure logging so we can see startup information in Railway logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log the PORT at startup so we can verify Railway is injecting it correctly.
# If this prints "NOT SET" in Railway logs, the PORT variable is missing.
logger.info(f"PORT environment variable: {os.environ.get('PORT', 'NOT SET')}")

app = FastAPI(
    title="StudyBuddy API",
    description="Backend API for the StudyBuddy learning platform",
    version="1.0.0",
)

# CORS — controls which frontend origins are allowed to call this API.
# The frontend URL must be listed here exactly as it appears in the browser.
# Read allowed origins from environment so we never hardcode the Railway URL.
allowed_origins_raw = os.environ.get(
    "ALLOWED_ORIGINS",
    "http://localhost:5173"     # default for local development
)
allowed_origins = [origin.strip() for origin in allowed_origins_raw.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
# Every new feature's router must be added here
app.include_router(auth.router)


@app.get("/health", tags=["health"])
def health_check():
    """
    Health check endpoint used by Railway to verify the service is running.
    Returns 200 OK when the app is up.
    """
    return {"status": "ok"}

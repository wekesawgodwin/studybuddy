import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173").split(",")



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"PORT environment variable is: {os.environ.get('PORT', 'NOT SET')}")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/hello")
def hello_world():
    return {"message": "Hey Group 13!! We are live"}
from fastapi import FastAPI, Depends, File, UploadFile, HTTPException
from pydantic import BaseModel, Field
import motor.motor_asyncio
import os
from dotenv import load_dotenv
from mangum import Mangum

# Load environment variables (like MONGO_URI) from the .env file
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI not set in environment variables.")

# MongoDB Dependency Injection using FastAPI's Depends:
# Creates a new asynchronous MongoDB client for each requset and ensures it is closed afterward.
async def get_db():
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    try:
        yield client["multimedia_db"]
    finally:
        client.close()

# Initialize the FastAPI app
app = FastAPI()

# Data model for player score using Pydantic.
# This model is used to validate incoming daat for player scores.
class PlayerScore(BaseModel):
    player_name: str = Field(..., min_length=1, max_length=50)  # Player's name (1–50 characters)
    score: int = Field(..., ge=0, le=999999)  # Score must be between 0 and 999999

# Endpoint: /upload_sprite
# Method: POST
# Description:
#   Accepts an image (sprite) file upload.
#   Stores the file in the MongoDB "sprites" colelction with its filename and binary content.
@app.post("/upload_sprite")
async def upload_sprite(file: UploadFile = File(...), db=Depends(get_db)):
    content = await file.read()
    sprite_doc = {"filename": file.filename, "content": content}
    result = await db.sprites.insert_one(sprite_doc)
    return {"message": "Sprite uploaded", "id": str(result.inserted_id)}

# Endpoint: /upload_audio
# Method: POST
# Description:
#   Accepts an audio file upload.
#   Stores the file in the MongoDB "audio" collection with its fileanme and binary content.
@app.post("/upload_audio")
async def upload_audio(file: UploadFile = File(...), db=Depends(get_db)):
    content = await file.read()
    audio_doc = {"filename": file.filename, "content": content}
    result = await db.audio.insert_one(audio_doc)
    return {"message": "Audio file uploaded", "id": str(result.inserted_id)}

# Endpoint: /player_score
# Method: POST
# Description:
#   Accepts a JSON palyoad with a player's name and score.
#   Uses Pydantic for validation and sanitization to prevent NoSQL injection attacks.
#   Stores the data in the MongoDB "scores" collection.
@app.post("/player_score")
async def add_score(score: PlayerScore, db=Depends(get_db)):
    score_doc = score.dict()
    result = await db.scores.insert_one(score_doc)
    return {"message": "Score recorded", "id": str(result.inserted_id)}

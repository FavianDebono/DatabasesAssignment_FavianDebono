from fastapi import FastAPI, Depends, File, UploadFile, HTTPException
from pydantic import BaseModel
import motor.motor_asyncio
import os
from dotenv import load_dotenv
from mangum import Mangum

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI not set in environment variables.")

async def get_db():
    # Create a new MongoDB client connection for each request.
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    try:
        yield client["multimedia_db"]
    finally:
        client.close()  # Ensures the client is closed after the request

app = FastAPI()

class PlayerScore(BaseModel):
    player_name: str
    score: int

@app.post("/upload_sprite")
async def upload_sprite(file: UploadFile = File(...), db=Depends(get_db)):
    content = await file.read()
    sprite_doc = {"filename": file.filename, "content": content}
    result = await db.sprites.insert_one(sprite_doc)
    return {"message": "Sprite uploaded", "id": str(result.inserted_id)}

@app.post("/upload_audio")
async def upload_audio(file: UploadFile = File(...), db=Depends(get_db)):
    content = await file.read()
    audio_doc = {"filename": file.filename, "content": content}
    result = await db.audio.insert_one(audio_doc)
    return {"message": "Audio file uploaded", "id": str(result.inserted_id)}

@app.post("/player_score")
async def add_score(score: PlayerScore, db=Depends(get_db)):
    score_doc = score.dict()
    result = await db.scores.insert_one(score_doc)
    return {"message": "Score recorded", "id": str(result.inserted_id)}

#handler = Mangum(app)
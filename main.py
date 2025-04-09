from fastapi import FastAPI, Depends, File, UploadFile, HTTPException
from pydantic import BaseModel, Field
import motor.motor_asyncio
import os
from dotenv import load_dotenv
from bson import ObjectId
from mangum import Mangum

# Load environment variables (like MONGO_URI) from the .env file
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI not set in environment variables.")

# MongoDB Dependency Injection using FastAPI's Depends:
# Creates a new asynchronous MongoDB client for each request and ensures it is closed afterward.
async def get_db():
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    try:
        yield client["multimedia_db"]
    finally:
        client.close()

# Initialize the FastAPI app
app = FastAPI()

# Data model for player score using Pydantic.
# This model is used to validate incoming data for player scores.
class PlayerScore(BaseModel):
    player_name: str = Field(..., min_length=1, max_length=50)  # Player's name (1–50 characters)
    score: int = Field(..., ge=0, le=999999)  # Score must be between 0 and 999999

# Endpoint: /upload_sprite
# Method: POST
# Description:
#   Accepts an image (sprite) file upload.
#   Stores the file in the MongoDB "sprites" collection with its filename and binary content.
@app.post("/upload_sprite")
async def upload_sprite(file: UploadFile = File(...), db=Depends(get_db)):
    content = await file.read() # Read the file content
    sprite_doc = {"filename": file.filename, "content": content} # Create a document with filename and content
    result = await db.sprites.insert_one(sprite_doc) # Insert the document into the MongoDB collection
    return {"message": "Sprite uploaded", "id": str(result.inserted_id)} # Return the ID of the inserted document as a response

# Endpoint: /sprites/{id}
# Method: GET
# Description:
#   Fetches a sprite document by ID.
@app.get("/sprites/{id}") 
async def get_sprite(id: str, db=Depends(get_db)):
    sprite = await db.sprites.find_one({"_id": ObjectId(id)}) # Fetch the sprite document from the database using its ID
    if not sprite: # If the sprite is not found, raise a 404 error
        raise HTTPException(status_code=404, detail="Sprite not found") 
    return {"filename": sprite["filename"]} # Return the filename of the sprite if found

# Endpoint: /sprites/{id}
# Method: PUT
# Description:
#   Updates the sprite's file.
@app.put("/sprites/{id}")
async def update_sprite(id: str, file: UploadFile = File(...), db=Depends(get_db)):
    content = await file.read() # Read the new file content
    result = await db.sprites.update_one( # Update the existing sprite document in the database
        {"_id": ObjectId(id)},
        {"$set": {"filename": file.filename, "content": content}}
    )
    if result.matched_count == 0: # If no document was matched, raise a 404 error
        raise HTTPException(status_code=404, detail="Sprite not found")
    return {"message": "Sprite updated"} # Return a success message

# Endpoint: /sprites/{id}
# Method: DELETE
# Description:
#   Deletes a sprite document by ID.
@app.delete("/sprites/{id}")
async def delete_sprite(id: str, db=Depends(get_db)): 
    result = await db.sprites.delete_one({"_id": ObjectId(id)}) # Delete the sprite document from the database using its ID
    if result.deleted_count == 0: # If no document was deleted, raise a 404 error
        raise HTTPException(status_code=404, detail="Sprite not found")
    return {"message": "Sprite deleted"} # Return a success message

# Endpoint: /upload_audio
# Method: POST
# Description:
#   Accepts an audio file upload.
#   Stores the file in the MongoDB "audio" collection with its filename and binary content.
@app.post("/upload_audio")
async def upload_audio(file: UploadFile = File(...), db=Depends(get_db)):
    content = await file.read()
    audio_doc = {"filename": file.filename, "content": content}
    result = await db.audio.insert_one(audio_doc)
    return {"message": "Audio file uploaded", "id": str(result.inserted_id)}

# Endpoint: /audio/{id}
# Method: GET
# Description:
#   Fetches an audio document by ID.
@app.get("/audio/{id}")
async def get_audio(id: str, db=Depends(get_db)):
    audio = await db.audio.find_one({"_id": ObjectId(id)})
    if not audio:
        raise HTTPException(status_code=404, detail="Audio not found")
    return {"filename": audio["filename"]}

# Endpoint: /audio/{id}
# Method: PUT
# Description:
#   Updates an audio file.
@app.put("/audio/{id}")
async def update_audio(id: str, file: UploadFile = File(...), db=Depends(get_db)):
    content = await file.read()
    result = await db.audio.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"filename": file.filename, "content": content}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Audio not found")
    return {"message": "Audio updated"}

# Endpoint: /audio/{id}
# Method: DELETE
# Description:
#   Deletes an audio document by ID.
@app.delete("/audio/{id}")
async def delete_audio(id: str, db=Depends(get_db)):
    result = await db.audio.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Audio not found")
    return {"message": "Audio deleted"}

# Endpoint: /player_score
# Method: POST
# Description:
#   Accepts a JSON payload with a player's name and score.
#   Uses Pydantic for validation and sanitization to prevent NoSQL injection attacks.
#   Stores the data in the MongoDB "scores" collection.
@app.post("/player_score")
async def add_score(score: PlayerScore, db=Depends(get_db)):
    score_doc = score.dict()
    result = await db.scores.insert_one(score_doc)
    return {"message": "Score recorded", "id": str(result.inserted_id)}

# Endpoint: /player_score/{id}
# Method: GET
# Description:
#   Fetches a player score document by ID.
@app.get("/player_score/{id}")
async def get_score(id: str, db=Depends(get_db)):
    score = await db.scores.find_one({"_id": ObjectId(id)})
    if not score:
        raise HTTPException(status_code=404, detail="Score not found")
    return {"player_name": score["player_name"], "score": score["score"]}

# Endpoint: /player_score/{id}
# Method: PUT
# Description:
#   Updates a player score document.
@app.put("/player_score/{id}")
async def update_score(id: str, score: PlayerScore, db=Depends(get_db)):
    result = await db.scores.update_one(
        {"_id": ObjectId(id)},
        {"$set": score.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Score not found")
    return {"message": "Score updated"}

# Endpoint: /player_score/{id}
# Method: DELETE
# Description:
#   Deletes a player score document by ID.
@app.delete("/player_score/{id}")
async def delete_score(id: str, db=Depends(get_db)):
    result = await db.scores.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Score not found")
    return {"message": "Score deleted"}

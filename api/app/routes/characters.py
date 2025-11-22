from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from bson import ObjectId
from datetime import datetime
from app.database import get_database
from app.models.character import (
    Character,
    CharacterCreate,
    CharacterUpdate,
    DesireUpdate,
    ActionLogEntry,
    MemoryLogEntry,
    Needs
)
from app.services.llm_service import get_llm_service
from pydantic import BaseModel

router = APIRouter(prefix="/characters", tags=["characters"])


def character_helper(character) -> dict:
    """Convert MongoDB document to dict."""
    if character:
        character["_id"] = str(character["_id"])
        return character
    return None


@router.get("/", response_model=List[Character])
async def list_characters():
    """List all characters."""
    db = get_database()
    characters = []
    
    async for character in db.characters.find():
        characters.append(character_helper(character))
    
    return characters


@router.get("/{character_id}", response_model=Character)
async def get_character(character_id: str):
    """Get a specific character by ID."""
    db = get_database()
    
    if not ObjectId.is_valid(character_id):
        raise HTTPException(status_code=400, detail="Invalid character ID format")
    
    character = await db.characters.find_one({"_id": ObjectId(character_id)})
    
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    return character_helper(character)


class ObjectUseResponse(BaseModel):
    """Response from using an object."""
    character_name: str
    object_name: str
    flavor_text: str
    timestamp: datetime


@router.post("/{character_id}/use/{object_name}", response_model=ObjectUseResponse)
async def use_object(character_id: str, object_name: str, space_id: Optional[str] = None):
    """
    Character interacts with an object.
    LLM generates contextual flavor text based on character personality and object.
    """
    db = get_database()
    
    if not ObjectId.is_valid(character_id):
        raise HTTPException(status_code=400, detail="Invalid character ID format")
    
    # Get character
    character = await db.characters.find_one({"_id": ObjectId(character_id)})
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Get space info if provided
    space_info = None
    if space_id:
        if ObjectId.is_valid(space_id):
            space_info = await db.spaces.find_one({"_id": ObjectId(space_id)})
    
    # Generate flavor text using LLM
    llm = get_llm_service()
    
    try:
        flavor_text = await llm.generate_object_interaction(
            character=character,
            object_name=object_name,
            space_info=space_info
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM generation failed: {str(e)}")
    
    # Add to action log
    timestamp = datetime.utcnow()
    action_entry = {
        "timestamp": timestamp,
        "action": "use_object",
        "details": f"Used {object_name}: {flavor_text}"
    }
    
    await db.characters.update_one(
        {"_id": ObjectId(character_id)},
        {"$push": {"action_log": action_entry}}
    )
    
    # Return response
    return ObjectUseResponse(
        character_name=character["name"],
        object_name=object_name,
        flavor_text=flavor_text,
        timestamp=timestamp
    )


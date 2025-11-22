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


@router.post("/", response_model=Character, status_code=status.HTTP_201_CREATED)
async def create_character(character: CharacterCreate):
    """Create a new character."""
    db = get_database()
    
    character_dict = character.model_dump()
    
    # Set default needs if not provided
    if "needs" not in character_dict or character_dict["needs"] is None:
        character_dict["needs"] = Needs().model_dump()
    
    # Initialize empty lists
    character_dict["action_log"] = []
    character_dict["memory_log"] = []
    character_dict["relationships"] = []
    
    result = await db.characters.insert_one(character_dict)
    new_character = await db.characters.find_one({"_id": result.inserted_id})
    
    return character_helper(new_character)


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


@router.put("/{character_id}", response_model=Character)
async def update_character(character_id: str, update: CharacterUpdate):
    """Update a character's state."""
    db = get_database()
    
    if not ObjectId.is_valid(character_id):
        raise HTTPException(status_code=400, detail="Invalid character ID format")
    
    # Only update fields that are provided
    update_data = {k: v for k, v in update.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No update data provided")
    
    result = await db.characters.update_one(
        {"_id": ObjectId(character_id)},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Character not found")
    
    character = await db.characters.find_one({"_id": ObjectId(character_id)})
    return character_helper(character)


@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character(character_id: str):
    """Delete a character."""
    db = get_database()
    
    if not ObjectId.is_valid(character_id):
        raise HTTPException(status_code=400, detail="Invalid character ID format")
    
    result = await db.characters.delete_one({"_id": ObjectId(character_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Character not found")
    
    return None


@router.put("/{character_id}/desire", response_model=Character)
async def update_desire(character_id: str, desire_update: DesireUpdate):
    """Update a character's current desire/intention."""
    db = get_database()
    
    if not ObjectId.is_valid(character_id):
        raise HTTPException(status_code=400, detail="Invalid character ID format")
    
    result = await db.characters.update_one(
        {"_id": ObjectId(character_id)},
        {"$set": {"current_desire": desire_update.current_desire}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Character not found")
    
    character = await db.characters.find_one({"_id": ObjectId(character_id)})
    return character_helper(character)


@router.post("/{character_id}/action-log", response_model=Character)
async def add_action_log(character_id: str, action: ActionLogEntry):
    """Add an action to a character's action log."""
    db = get_database()
    
    if not ObjectId.is_valid(character_id):
        raise HTTPException(status_code=400, detail="Invalid character ID format")
    
    result = await db.characters.update_one(
        {"_id": ObjectId(character_id)},
        {"$push": {"action_log": action.model_dump()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Character not found")
    
    character = await db.characters.find_one({"_id": ObjectId(character_id)})
    return character_helper(character)


@router.post("/{character_id}/memory-log", response_model=Character)
async def add_memory_log(character_id: str, memory: MemoryLogEntry):
    """Add a memory to a character's memory log."""
    db = get_database()
    
    if not ObjectId.is_valid(character_id):
        raise HTTPException(status_code=400, detail="Invalid character ID format")
    
    result = await db.characters.update_one(
        {"_id": ObjectId(character_id)},
        {"$push": {"memory_log": memory.model_dump()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Character not found")
    
    character = await db.characters.find_one({"_id": ObjectId(character_id)})
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


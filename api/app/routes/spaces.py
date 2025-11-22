from fastapi import APIRouter, HTTPException, status
from typing import List
from bson import ObjectId
from app.database import get_database
from app.models.space import (
    Space,
    SpaceCreate,
    SpaceUpdate,
    CharactersPresentUpdate,
    ActivitiesUpdate
)
from app.services.llm_service import get_llm_service
from pydantic import BaseModel

router = APIRouter(prefix="/spaces", tags=["spaces"])


def space_helper(space) -> dict:
    """Convert MongoDB document to dict."""
    if space:
        space["_id"] = str(space["_id"])
        return space
    return None


@router.get("/", response_model=List[Space])
async def list_spaces():
    """List all spaces."""
    db = get_database()
    spaces = []
    
    async for space in db.spaces.find():
        spaces.append(space_helper(space))
    
    return spaces


@router.get("/{space_id}", response_model=Space)
async def get_space(space_id: str):
    """Get a specific space by ID."""
    db = get_database()
    
    if not ObjectId.is_valid(space_id):
        raise HTTPException(status_code=400, detail="Invalid space ID format")
    
    space = await db.spaces.find_one({"_id": ObjectId(space_id)})
    
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")
    
    return space_helper(space)


@router.put("/{space_id}/characters", response_model=Space)
async def update_characters_present(space_id: str, update: CharactersPresentUpdate):
    """Update the list of characters present in a space."""
    db = get_database()
    
    if not ObjectId.is_valid(space_id):
        raise HTTPException(status_code=400, detail="Invalid space ID format")
    
    # Validate all character IDs exist
    for char_id in update.characters_present:
        if not ObjectId.is_valid(char_id):
            raise HTTPException(status_code=400, detail=f"Invalid character ID format: {char_id}")
        
        character = await db.characters.find_one({"_id": ObjectId(char_id)})
        if not character:
            raise HTTPException(status_code=404, detail=f"Character not found: {char_id}")
    
    result = await db.spaces.update_one(
        {"_id": ObjectId(space_id)},
        {"$set": {"characters_present": update.characters_present}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Space not found")
    
    space = await db.spaces.find_one({"_id": ObjectId(space_id)})
    return space_helper(space)


class GeneratedActivities(BaseModel):
    """Response from generating space activities."""
    space_name: str
    activities_description: str
    characters_count: int


@router.put("/{space_id}/generate-activities", response_model=GeneratedActivities)
async def generate_space_activities(space_id: str):
    """
    AI-generated: Generate a description of what's happening in the space.
    Based on all characters present and their current actions/desires.
    """
    db = get_database()
    
    if not ObjectId.is_valid(space_id):
        raise HTTPException(status_code=400, detail="Invalid space ID format")
    
    # Get space
    space = await db.spaces.find_one({"_id": ObjectId(space_id)})
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")
    
    # Get all characters in this space
    characters_in_space = []
    if space.get("characters_present"):
        for char_id in space["characters_present"]:
            if ObjectId.is_valid(char_id):
                char = await db.characters.find_one({"_id": ObjectId(char_id)})
                if char:
                    characters_in_space.append(char)
    
    # Generate activities description using LLM
    llm = get_llm_service()
    
    try:
        activities_description = await llm.generate_space_activities(
            space=space,
            characters=characters_in_space
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM generation failed: {str(e)}")
    
    # Update space
    await db.spaces.update_one(
        {"_id": ObjectId(space_id)},
        {"$set": {"activities_description": activities_description}}
    )
    
    return GeneratedActivities(
        space_name=space["name"],
        activities_description=activities_description,
        characters_count=len(characters_in_space)
    )


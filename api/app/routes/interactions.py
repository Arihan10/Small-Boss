from fastapi import APIRouter, HTTPException, status
from typing import List
from bson import ObjectId
from app.database import get_database
from app.models.interaction import Interaction, InteractionCreate

router = APIRouter(prefix="/interactions", tags=["interactions"])


def interaction_helper(interaction) -> dict:
    """Convert MongoDB document to dict."""
    if interaction:
        interaction["_id"] = str(interaction["_id"])
        return interaction
    return None


@router.post("/", response_model=Interaction, status_code=status.HTTP_201_CREATED)
async def create_interaction(interaction: InteractionCreate):
    """Log a new interaction."""
    db = get_database()
    
    # Validate all participant IDs exist
    for char_id in interaction.participants:
        if not ObjectId.is_valid(char_id):
            raise HTTPException(status_code=400, detail=f"Invalid character ID format: {char_id}")
        
        character = await db.characters.find_one({"_id": ObjectId(char_id)})
        if not character:
            raise HTTPException(status_code=404, detail=f"Character not found: {char_id}")
    
    interaction_dict = interaction.model_dump()
    
    result = await db.interactions.insert_one(interaction_dict)
    new_interaction = await db.interactions.find_one({"_id": result.inserted_id})
    
    return interaction_helper(new_interaction)


@router.get("/", response_model=List[Interaction])
async def list_interactions():
    """List all interactions."""
    db = get_database()
    interactions = []
    
    async for interaction in db.interactions.find().sort("timestamp", -1):
        interactions.append(interaction_helper(interaction))
    
    return interactions


@router.get("/character/{character_id}", response_model=List[Interaction])
async def get_character_interactions(character_id: str):
    """Get all interactions for a specific character."""
    db = get_database()
    
    if not ObjectId.is_valid(character_id):
        raise HTTPException(status_code=400, detail="Invalid character ID format")
    
    # Check if character exists
    character = await db.characters.find_one({"_id": ObjectId(character_id)})
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    interactions = []
    async for interaction in db.interactions.find({
        "participants": character_id
    }).sort("timestamp", -1):
        interactions.append(interaction_helper(interaction))
    
    return interactions


from fastapi import APIRouter, HTTPException, status
from typing import List
from bson import ObjectId
from app.database import get_database
from app.models.relationship import (
    Relationship,
    RelationshipCreate,
    RelationshipUpdate,
    InteractionAdd,
    InteractionSummary
)

router = APIRouter(prefix="/relationships", tags=["relationships"])


def relationship_helper(relationship) -> dict:
    """Convert MongoDB document to dict."""
    if relationship:
        relationship["_id"] = str(relationship["_id"])
        return relationship
    return None


@router.get("/character/{character_id}", response_model=List[Relationship])
async def get_character_relationships(character_id: str):
    """Get all relationships FROM a specific character (how they feel about others)."""
    db = get_database()
    
    if not ObjectId.is_valid(character_id):
        raise HTTPException(status_code=400, detail="Invalid character ID format")
    
    # Check if character exists
    character = await db.characters.find_one({"_id": ObjectId(character_id)})
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    relationships = []
    async for relationship in db.relationships.find({
        "from_character_id": character_id
    }):
        relationships.append(relationship_helper(relationship))
    
    return relationships


@router.get("/character/{character_id}/incoming", response_model=List[Relationship])
async def get_incoming_relationships(character_id: str):
    """Get all relationships TO a specific character (how others feel about them)."""
    db = get_database()
    
    if not ObjectId.is_valid(character_id):
        raise HTTPException(status_code=400, detail="Invalid character ID format")
    
    # Check if character exists
    character = await db.characters.find_one({"_id": ObjectId(character_id)})
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    relationships = []
    async for relationship in db.relationships.find({
        "to_character_id": character_id
    }):
        relationships.append(relationship_helper(relationship))
    
    return relationships




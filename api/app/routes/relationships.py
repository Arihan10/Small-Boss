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


@router.post("/", response_model=Relationship, status_code=status.HTTP_201_CREATED)
async def create_relationship(relationship: RelationshipCreate):
    """Create a new one-way relationship from one character to another.
    
    Note: Relationships are directional. To create a mutual relationship,
    call this endpoint twice with reversed from/to characters.
    """
    db = get_database()
    
    # Validate that both characters exist
    char_from = await db.characters.find_one({"_id": ObjectId(relationship.from_character_id)})
    char_to = await db.characters.find_one({"_id": ObjectId(relationship.to_character_id)})
    
    if not char_from or not char_to:
        raise HTTPException(status_code=404, detail="One or both characters not found")
    
    # Check if this specific directional relationship already exists
    existing = await db.relationships.find_one({
        "from_character_id": relationship.from_character_id,
        "to_character_id": relationship.to_character_id
    })
    
    if existing:
        raise HTTPException(status_code=400, detail="This directional relationship already exists")
    
    relationship_dict = relationship.model_dump()
    relationship_dict["interaction_history"] = []
    relationship_dict["current_interaction_state"] = "none"
    
    result = await db.relationships.insert_one(relationship_dict)
    new_relationship = await db.relationships.find_one({"_id": result.inserted_id})
    
    # Update from_character's relationship list
    await db.characters.update_one(
        {"_id": ObjectId(relationship.from_character_id)},
        {"$addToSet": {"relationships": relationship.to_character_id}}
    )
    
    return relationship_helper(new_relationship)


@router.get("/", response_model=List[Relationship])
async def list_relationships():
    """List all relationships."""
    db = get_database()
    relationships = []
    
    async for relationship in db.relationships.find():
        relationships.append(relationship_helper(relationship))
    
    return relationships


@router.get("/{relationship_id}", response_model=Relationship)
async def get_relationship(relationship_id: str):
    """Get a specific relationship by ID."""
    db = get_database()
    
    if not ObjectId.is_valid(relationship_id):
        raise HTTPException(status_code=400, detail="Invalid relationship ID format")
    
    relationship = await db.relationships.find_one({"_id": ObjectId(relationship_id)})
    
    if not relationship:
        raise HTTPException(status_code=404, detail="Relationship not found")
    
    return relationship_helper(relationship)


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


@router.put("/{relationship_id}", response_model=Relationship)
async def update_relationship(relationship_id: str, update: RelationshipUpdate):
    """Update a relationship (score, summary, state)."""
    db = get_database()
    
    if not ObjectId.is_valid(relationship_id):
        raise HTTPException(status_code=400, detail="Invalid relationship ID format")
    
    # Only update fields that are provided
    update_data = {k: v for k, v in update.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No update data provided")
    
    result = await db.relationships.update_one(
        {"_id": ObjectId(relationship_id)},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Relationship not found")
    
    relationship = await db.relationships.find_one({"_id": ObjectId(relationship_id)})
    return relationship_helper(relationship)


@router.post("/{relationship_id}/interactions", response_model=Relationship)
async def add_interaction_summary(relationship_id: str, interaction: InteractionAdd):
    """Add an interaction summary to a relationship's history."""
    db = get_database()
    
    if not ObjectId.is_valid(relationship_id):
        raise HTTPException(status_code=400, detail="Invalid relationship ID format")
    
    # Create interaction summary
    summary = InteractionSummary(**interaction.model_dump())
    
    # Update relationship score if specified
    update_ops = {"$push": {"interaction_history": summary.model_dump()}}
    
    if interaction.relationship_score_change is not None:
        # Get current score
        relationship = await db.relationships.find_one({"_id": ObjectId(relationship_id)})
        if not relationship:
            raise HTTPException(status_code=404, detail="Relationship not found")
        
        new_score = max(-100, min(100, relationship.get("relationship_score", 0) + interaction.relationship_score_change))
        update_ops["$set"] = {"relationship_score": new_score}
    
    result = await db.relationships.update_one(
        {"_id": ObjectId(relationship_id)},
        update_ops
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Relationship not found")
    
    relationship = await db.relationships.find_one({"_id": ObjectId(relationship_id)})
    return relationship_helper(relationship)


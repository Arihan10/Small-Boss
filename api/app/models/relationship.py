from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.enums import InteractionState


class InteractionSummary(BaseModel):
    """Summary of an interaction between characters."""
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    action_type: str  # "dialog", "fight", "romance", etc.
    summary: str  # LLM-generated summary
    emotional_impact: Optional[str] = None
    relationship_score_change: Optional[int] = None


class Relationship(BaseModel):
    """One-way relationship from one character to another.
    
    Note: Relationships are directional. For a mutual relationship,
    create two Relationship objects (one for each direction).
    """
    
    id: Optional[str] = Field(alias="_id", default=None)
    
    # One-way relationship: from_character -> to_character
    from_character_id: str
    to_character_id: str
    
    # Relationship metadata
    relationship_type: str  # "Friendly", "Romantic", "Antagonistic", "Professional", "Family", etc.
    relationship_summary: str  # LLM-generated narrative description
    relationship_score: int = Field(default=0, ge=-100, le=100)
    
    # Interaction history
    interaction_history: List[InteractionSummary] = Field(default_factory=list)
    
    # Current interaction state
    current_interaction_state: InteractionState = InteractionState.NONE
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "from_character_id": "507f1f77bcf86cd799439011",
                "to_character_id": "507f1f77bcf86cd799439012",
                "relationship_type": "Romantic",
                "relationship_summary": "Sarah feels deeply connected to Mike and admires his dedication",
                "relationship_score": 75,
                "current_interaction_state": "none"
            }
        }


class RelationshipCreate(BaseModel):
    """Schema for creating a new one-way relationship."""
    
    from_character_id: str
    to_character_id: str
    relationship_type: str
    relationship_summary: str
    relationship_score: int = Field(default=0, ge=-100, le=100)


class RelationshipUpdate(BaseModel):
    """Schema for updating a relationship."""
    
    relationship_type: Optional[str] = None
    relationship_summary: Optional[str] = None
    relationship_score: Optional[int] = Field(default=None, ge=-100, le=100)
    current_interaction_state: Optional[InteractionState] = None


class InteractionAdd(BaseModel):
    """Schema for adding an interaction summary to a relationship."""
    
    action_type: str
    summary: str
    emotional_impact: Optional[str] = None
    relationship_score_change: Optional[int] = None


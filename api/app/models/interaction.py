from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class Interaction(BaseModel):
    """Interaction model for logging interactions between characters."""
    
    id: Optional[str] = Field(alias="_id", default=None)
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    participants: List[str]  # Character IDs involved
    action_type: str  # "dialog", "fight", "romance", "use_object", etc.
    summary: str  # LLM-generated summary after interaction ends
    emotional_impact: Optional[Dict[str, Any]] = None  # Optional metadata about emotional changes
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "participants": ["507f1f77bcf86cd799439011", "507f1f77bcf86cd799439012"],
                "action_type": "dialog",
                "summary": "Sarah and Mike had a heated debate about the best programming language. Despite disagreeing, they both laughed it off.",
                "emotional_impact": {
                    "Sarah": "slightly_annoyed_but_amused",
                    "Mike": "defensive_but_friendly"
                }
            }
        }


class InteractionCreate(BaseModel):
    """Schema for creating/logging a new interaction."""
    
    participants: List[str]
    action_type: str
    summary: str
    emotional_impact: Optional[Dict[str, Any]] = None


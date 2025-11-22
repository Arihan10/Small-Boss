from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class Space(BaseModel):
    """Space model representing a location in the simulation."""
    
    id: Optional[str] = Field(alias="_id", default=None)
    
    # Static properties
    name: str  # Identifier for Unity to reference
    available_objects: List[str] = Field(default_factory=list)  # Interactable objects
    
    # Dynamic state
    characters_present: List[str] = Field(default_factory=list)  # Character IDs
    activities_description: Optional[str] = None  # LLM-generated summary
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "name": "Town Square",
                "available_objects": ["bench", "fountain", "street_lamp"],
                "characters_present": [],
                "activities_description": "The square is quiet in the early morning light."
            }
        }


class SpaceCreate(BaseModel):
    """Schema for creating a new space."""
    
    name: str
    available_objects: List[str] = Field(default_factory=list)


class SpaceUpdate(BaseModel):
    """Schema for updating a space's state."""
    
    activities_description: Optional[str] = None


class CharactersPresentUpdate(BaseModel):
    """Schema for updating characters present in a space."""
    
    characters_present: List[str]


class ActivitiesUpdate(BaseModel):
    """Schema for updating the activities description."""
    
    activities_description: str


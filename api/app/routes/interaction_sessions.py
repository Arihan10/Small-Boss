from fastapi import APIRouter, HTTPException, status
from typing import List
from bson import ObjectId
from datetime import datetime
from app.database import get_database
from app.models.interaction_session import (
    InteractionSession,
    StartInteractionRequest,
    InteractionActionRequest,
    Message
)
from app.models.enums import InteractionState
from app.services.llm_service import get_llm_service

router = APIRouter(prefix="/interaction-sessions", tags=["interaction-sessions"])


def session_helper(session) -> dict:
    """Convert MongoDB document to dict."""
    if session:
        session["_id"] = str(session["_id"])
        return session
    return None


@router.post("/", response_model=InteractionSession, status_code=status.HTTP_201_CREATED)
async def start_interaction(request: StartInteractionRequest):
    """Start a new interaction session between characters."""
    db = get_database()
    
    # Validate all participants exist
    if len(request.character_ids) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 characters")
    
    participants_data = []
    for char_id in request.character_ids:
        if not ObjectId.is_valid(char_id):
            raise HTTPException(status_code=400, detail=f"Invalid character ID: {char_id}")
        
        char = await db.characters.find_one({"_id": ObjectId(char_id)})
        if not char:
            raise HTTPException(status_code=404, detail=f"Character not found: {char_id}")
        participants_data.append(char)
    
    # Check if any participant is already in an active session
    for char_id in request.character_ids:
        existing_session = await db.interaction_sessions.find_one({
            "participants": char_id,
            "is_active": True
        })
        if existing_session:
            raise HTTPException(
                status_code=400,
                detail=f"Character {char_id} is already in an active interaction"
            )
    
    # Create session
    session_data = {
        "participants": request.character_ids,
        "participant_names": [char["name"] for char in participants_data],
        "interaction_type": request.interaction_type,
        "messages": [],
        "current_turn": request.character_ids[0],  # First character starts
        "started_at": datetime.utcnow(),
        "ended_at": None,
        "is_active": True
    }
    
    result = await db.interaction_sessions.insert_one(session_data)
    
    # Update character relationship states to show they're interacting
    for char_id in request.character_ids:
        await db.characters.update_one(
            {"_id": ObjectId(char_id)},
            {"$set": {"is_interacting": True}}
        )
    
    # Update relationships to set interaction state
    for i, char_id_1 in enumerate(request.character_ids):
        for char_id_2 in request.character_ids[i+1:]:
            # Update both directions
            await db.relationships.update_one(
                {"from_character_id": char_id_1, "to_character_id": char_id_2},
                {"$set": {"current_interaction_state": request.interaction_type}}
            )
            await db.relationships.update_one(
                {"from_character_id": char_id_2, "to_character_id": char_id_1},
                {"$set": {"current_interaction_state": request.interaction_type}}
            )
    
    new_session = await db.interaction_sessions.find_one({"_id": result.inserted_id})
    return session_helper(new_session)


@router.get("/{session_id}", response_model=InteractionSession)
async def get_session(session_id: str):
    """Get a specific interaction session."""
    db = get_database()
    
    if not ObjectId.is_valid(session_id):
        raise HTTPException(status_code=400, detail="Invalid session ID")
    
    session = await db.interaction_sessions.find_one({"_id": ObjectId(session_id)})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session_helper(session)


@router.post("/{session_id}/end", response_model=InteractionSession)
async def end_session(session_id: str):
    """Manually end an interaction session."""
    db = get_database()
    
    if not ObjectId.is_valid(session_id):
        raise HTTPException(status_code=400, detail="Invalid session ID")
    
    await end_interaction(session_id, db)
    
    session = await db.interaction_sessions.find_one({"_id": ObjectId(session_id)})
    return session_helper(session)


@router.post("/{session_id}/advance", response_model=InteractionSession)
async def advance_conversation(session_id: str):
    """
    AI-generated: Advance the conversation by having the current character speak.
    Uses LLM to generate realistic dialogue based on full context.
    """
    db = get_database()
    
    if not ObjectId.is_valid(session_id):
        raise HTTPException(status_code=400, detail="Invalid session ID")
    
    session = await db.interaction_sessions.find_one({"_id": ObjectId(session_id)})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not session.get("is_active"):
        raise HTTPException(status_code=400, detail="Session is not active")
    
    # Get current character
    current_char_id = session["current_turn"]
    current_char = await db.characters.find_one({"_id": ObjectId(current_char_id)})
    if not current_char:
        raise HTTPException(status_code=404, detail="Current character not found")
    
    # Get other participants
    other_participants = []
    for char_id in session["participants"]:
        if char_id != current_char_id:
            char = await db.characters.find_one({"_id": ObjectId(char_id)})
            if char:
                other_participants.append(char)
    
    # Get relationships with other participants
    relationships = []
    async for rel in db.relationships.find({
        "from_character_id": current_char_id,
        "to_character_id": {"$in": [c["_id"] for c in other_participants]}
    }):
        relationships.append(rel)
    
    # Get space info if characters are in a space
    space_info = None
    # For now, we could look up space by checking which space has these characters
    # Or Unity would tell us. For prototype, we'll skip this.
    
    # Generate dialogue using LLM
    llm = get_llm_service()
    
    try:
        dialogue = await llm.generate_dialogue(
            character=current_char,
            other_characters=other_participants,
            conversation_history=session.get("messages", []),
            space_info=space_info,
            relationships=relationships
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM generation failed: {str(e)}")
    
    # Create message
    message = Message(
        character_id=current_char_id,
        character_name=current_char["name"],
        action="talk",
        content=dialogue
    )
    
    # Add message to session
    await db.interaction_sessions.update_one(
        {"_id": ObjectId(session_id)},
        {"$push": {"messages": message.model_dump()}}
    )
    
    # Add to character's action log
    await db.characters.update_one(
        {"_id": ObjectId(current_char_id)},
        {"$push": {"action_log": {
            "timestamp": datetime.utcnow(),
            "action": "spoke",
            "details": f"In conversation: {dialogue[:50]}..."
        }}}
    )
    
    # Switch turn to next participant
    current_idx = session["participants"].index(current_char_id)
    next_idx = (current_idx + 1) % len(session["participants"])
    next_turn = session["participants"][next_idx]
    
    await db.interaction_sessions.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"current_turn": next_turn}}
    )
    
    # Get updated session
    updated_session = await db.interaction_sessions.find_one({"_id": ObjectId(session_id)})
    return session_helper(updated_session)


async def end_interaction(session_id: str, db):
    """Helper function to end an interaction."""
    session = await db.interaction_sessions.find_one({"_id": ObjectId(session_id)})
    if not session:
        return
    
    # Mark session as ended
    await db.interaction_sessions.update_one(
        {"_id": ObjectId(session_id)},
        {
            "$set": {
                "is_active": False,
                "ended_at": datetime.utcnow()
            }
        }
    )
    
    # Update characters - no longer interacting
    for char_id in session["participants"]:
        await db.characters.update_one(
            {"_id": ObjectId(char_id)},
            {"$set": {"is_interacting": False}}
        )
    
    # Reset relationship interaction states
    for i, char_id_1 in enumerate(session["participants"]):
        for char_id_2 in session["participants"][i+1:]:
            await db.relationships.update_one(
                {"from_character_id": char_id_1, "to_character_id": char_id_2},
                {"$set": {"current_interaction_state": "none"}}
            )
            await db.relationships.update_one(
                {"from_character_id": char_id_2, "to_character_id": char_id_1},
                {"$set": {"current_interaction_state": "none"}}
            )
    
    # Generate LLM summary
    if session.get("messages"):
        # Get participant characters
        participants = []
        for char_id in session["participants"]:
            char = await db.characters.find_one({"_id": ObjectId(char_id)})
            if char:
                participants.append(char)
        
        # Generate summary using LLM
        llm = get_llm_service()
        try:
            summary_data = await llm.generate_interaction_summary(
                participants=participants,
                messages=session["messages"],
                interaction_type=session["interaction_type"]
            )
            
            summary = summary_data["summary"]
            emotional_impact = summary_data["emotional_impact"]
            relationship_change = summary_data["relationship_change"]
        except Exception as e:
            print(f"Failed to generate LLM summary: {e}")
            summary = f"Had a {session['interaction_type']} with {len(session['messages'])} exchanges"
            emotional_impact = {}
            relationship_change = 0
        
        # Add to interaction history for all participant pairs
        for i, char_id_1 in enumerate(session["participants"]):
            for char_id_2 in session["participants"][i+1:]:
                interaction_summary = {
                    "timestamp": datetime.utcnow(),
                    "action_type": session["interaction_type"],
                    "summary": summary,
                    "emotional_impact": str(emotional_impact),
                    "relationship_score_change": relationship_change
                }
                
                # Update relationships with score changes
                await db.relationships.update_one(
                    {"from_character_id": char_id_1, "to_character_id": char_id_2},
                    {
                        "$push": {"interaction_history": interaction_summary},
                        "$inc": {"relationship_score": relationship_change}
                    }
                )
                await db.relationships.update_one(
                    {"from_character_id": char_id_2, "to_character_id": char_id_1},
                    {
                        "$push": {"interaction_history": interaction_summary},
                        "$inc": {"relationship_score": relationship_change}
                    }
                )
                
                # Ensure scores stay within bounds
                await db.relationships.update_many(
                    {"relationship_score": {"$gt": 100}},
                    {"$set": {"relationship_score": 100}}
                )
                await db.relationships.update_many(
                    {"relationship_score": {"$lt": -100}},
                    {"$set": {"relationship_score": -100}}
                )


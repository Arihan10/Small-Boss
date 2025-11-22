"""
Load generated characters from JSON into MongoDB.
Clears existing data and creates characters with relationships.
"""

import asyncio
import json
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_DB_URI = os.getenv("MONGO_DB_URI", "mongodb://localhost:27017/ai_life_sim")
DATABASE_NAME = "ai_life_sim"
INPUT_FILE = "generated_characters.json"


async def load_characters_to_mongo():
    """Load characters from JSON file into MongoDB."""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_DB_URI)
    db = client[DATABASE_NAME]
    
    print(f"Connected to MongoDB: {MONGO_DB_URI}")
    
    # Load JSON file
    print(f"\nLoading characters from {INPUT_FILE}...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    characters = data['characters']
    metadata = data.get('metadata', {})
    
    print(f"Found {len(characters)} characters")
    print(f"Generated at: {metadata.get('generated_at', 'unknown')}")
    print(f"Setting: {metadata.get('setting', 'unknown')}")
    
    # Clear existing data
    print("\n=== Clearing existing data ===")
    chars_deleted = await db.characters.delete_many({})
    rels_deleted = await db.relationships.delete_many({})
    spaces_deleted = await db.spaces.delete_many({})
    interactions_deleted = await db.interactions.delete_many({})
    
    print(f"Deleted: {chars_deleted.deleted_count} characters, "
          f"{rels_deleted.deleted_count} relationships, "
          f"{spaces_deleted.deleted_count} spaces, "
          f"{interactions_deleted.deleted_count} interactions")
    
    # Insert characters
    print("\n=== Inserting characters ===")
    
    # Prepare character documents
    char_docs = []
    name_to_id = {}  # Map names to IDs for relationship creation
    
    for char in characters:
        doc = {
            "name": char["name"],
            "age": char["age"],
            "appearance": char["appearance"],
            "race": char["race"],
            "gender": char["gender"],
            "occupation": char["occupation"],
            "background": char["background"],
            "personality_traits": char.get("personality_traits", []),
            "needs": char.get("needs", {
                "happiness": 50,
                "energy": 50,
                "hunger": 50,
                "hygiene": 50
            }),
            "current_desire": None,
            "action_log": [],
            "memory_log": [],
            "relationships": []  # Will populate with IDs after relationship creation
        }
        char_docs.append(doc)
    
    # Insert all characters
    result = await db.characters.insert_many(char_docs)
    inserted_ids = result.inserted_ids
    
    # Create name to ID mapping
    for i, char in enumerate(characters):
        name_to_id[char["name"]] = str(inserted_ids[i])
    
    print(f"Inserted {len(inserted_ids)} characters")
    
    # Create relationships
    print("\n=== Creating relationships ===")
    
    relationships_to_insert = []
    character_relationship_map = {}  # Track which characters each character knows
    
    for i, char in enumerate(characters):
        from_char_id = str(inserted_ids[i])
        from_char_name = char["name"]
        
        if from_char_id not in character_relationship_map:
            character_relationship_map[from_char_id] = []
        
        for rel in char.get("relationships", []):
            target_name = rel["target_name"]
            
            # Find target character ID
            if target_name not in name_to_id:
                print(f"Warning: Relationship target '{target_name}' not found for {from_char_name}")
                continue
            
            to_char_id = name_to_id[target_name]
            
            # Check if this exact directional relationship already exists
            existing = any(
                r["from_character_id"] == from_char_id and r["to_character_id"] == to_char_id
                for r in relationships_to_insert
            )
            
            if not existing:
                relationship_doc = {
                    "from_character_id": from_char_id,
                    "to_character_id": to_char_id,
                    "relationship_type": rel.get("relationship_type", "Friend"),
                    "relationship_summary": rel.get("relationship_summary", ""),
                    "relationship_score": rel.get("relationship_score", 50),
                    "interaction_history": [],
                    "current_interaction_state": "none"
                }
                relationships_to_insert.append(relationship_doc)
                
                # Track that from_char knows to_char
                if to_char_id not in character_relationship_map[from_char_id]:
                    character_relationship_map[from_char_id].append(to_char_id)
    
    if relationships_to_insert:
        rel_result = await db.relationships.insert_many(relationships_to_insert)
        print(f"Inserted {len(rel_result.inserted_ids)} relationships")
    else:
        print("No relationships to insert")
    
    # Update character relationship lists
    print("\n=== Updating character relationship lists ===")
    for char_id, related_ids in character_relationship_map.items():
        await db.characters.update_one(
            {"_id": inserted_ids[int([i for i, id in enumerate(inserted_ids) if str(id) == char_id][0])]},
            {"$set": {"relationships": related_ids}}
        )
    
    print(f"Updated relationship lists for {len(character_relationship_map)} characters")
    
    # Close connection
    client.close()
    
    print("\n=== Load Complete ===")
    print(f"Database: {DATABASE_NAME}")
    print(f"Characters: {len(inserted_ids)}")
    print(f"Relationships: {len(relationships_to_insert)}")
    print(f"\nYou can now start the API server with: uvicorn app.main:app --reload")


if __name__ == "__main__":
    asyncio.run(load_characters_to_mongo())


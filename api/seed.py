"""
Seed script to populate the database with example data.
Run this script to initialize the database with sample characters, spaces, and relationships.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_DB_URI = os.getenv("MONGO_DB_URI", "mongodb://localhost:27017/ai_life_sim")
DATABASE_NAME = "ai_life_sim"


async def seed_database():
    """Seed the database with example data."""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_DB_URI)
    db = client[DATABASE_NAME]
    
    print("Starting database seeding...")
    
    # Clear existing data
    print("Clearing existing data...")
    await db.characters.delete_many({})
    await db.relationships.delete_many({})
    await db.spaces.delete_many({})
    await db.interactions.delete_many({})
    
    # Create characters
    print("Creating characters...")
    
    characters = [
        {
            "name": "Sarah Chen",
            "age": 28,
            "appearance": {"hair": 12, "shoes": 1, "bottom": 3, "top": 8},  # bun, running shoes, jeans, green hoodie
            "race": "Asian",
            "gender": "Female",
            "occupation": "Software Engineer",
            "background": "Grew up in a small town, moved to the city for college. Passionate about AI and gaming.",
            "personality_traits": ["ambitious", "creative", "driven", "introverted", "analytical"],
            "needs": {
                "happiness": 70,
                "energy": 60,
                "hunger": 40,
                "hygiene": 80
            },
            "current_desire": "Wants to grab coffee and work on side projects",
            "action_log": [
                {
                    "timestamp": datetime.utcnow(),
                    "action": "woke_up",
                    "details": "Started the day feeling energized"
                }
            ],
            "memory_log": [
                {
                    "timestamp": datetime.utcnow(),
                    "event": "Had a great conversation about machine learning at the coffee shop yesterday",
                    "emotional_impact": "positive"
                }
            ],
            "relationships": []
        },
        {
            "name": "Mike Rodriguez",
            "age": 32,
            "appearance": {"hair": 3, "shoes": 1, "bottom": 1, "top": 0},  # buzzcut, running shoes, shorts, gym shirt
            "race": "Hispanic",
            "gender": "Male",
            "occupation": "Fitness Trainer",
            "background": "Former college athlete, now runs his own gym. Loves helping people achieve their goals.",
            "personality_traits": ["outgoing", "energetic", "competitive", "supportive", "disciplined"],
            "needs": {
                "happiness": 80,
                "energy": 90,
                "hunger": 60,
                "hygiene": 70
            },
            "current_desire": "Wants to organize a group workout session",
            "action_log": [
                {
                    "timestamp": datetime.utcnow(),
                    "action": "morning_run",
                    "details": "Completed 5-mile run around the park"
                }
            ],
            "memory_log": [],
            "relationships": []
        },
        {
            "name": "Emma Thompson",
            "age": 25,
            "appearance": {"hair": 13, "shoes": 0, "bottom": 2, "top": 6},  # ponytail, girly boots, skirt, crop top with jacket
            "race": "White",
            "gender": "Female",
            "occupation": "Graphic Designer",
            "background": "Art school graduate with a passion for visual storytelling. Introverted but deeply creative.",
            "personality_traits": ["creative", "introverted", "sensitive", "perfectionist", "dreamy"],
            "needs": {
                "happiness": 65,
                "energy": 50,
                "hunger": 30,
                "hygiene": 60
            },
            "current_desire": "Wants to find inspiration at the park",
            "action_log": [],
            "memory_log": [
                {
                    "timestamp": datetime.utcnow(),
                    "event": "Saw a beautiful sunset that inspired new color palette ideas",
                    "emotional_impact": "inspired"
                }
            ],
            "relationships": []
        },
        {
            "name": "David Park",
            "age": 35,
            "appearance": {"hair": 11, "shoes": 5, "bottom": 0, "top": 9},  # short 4, sketchers, black pants, shirt with tie
            "race": "Asian",
            "gender": "Male",
            "occupation": "High School Teacher",
            "background": "Dedicated educator who believes in making a difference. Married with one child.",
            "personality_traits": ["patient", "nurturing", "responsible", "traditional", "wise"],
            "needs": {
                "happiness": 75,
                "energy": 55,
                "hunger": 50,
                "hygiene": 85
            },
            "current_desire": "Wants to spend quality time with family",
            "action_log": [
                {
                    "timestamp": datetime.utcnow(),
                    "action": "graded_papers",
                    "details": "Finished grading last week's assignments"
                }
            ],
            "memory_log": [],
            "relationships": []
        }
    ]
    
    char_results = await db.characters.insert_many(characters)
    char_ids = [str(id) for id in char_results.inserted_ids]
    print(f"Created {len(char_ids)} characters")
    
    # Create spaces
    print("Creating spaces...")
    
    spaces = [
        {
            "name": "Town Square",
            "available_objects": ["bench", "fountain", "street_lamp", "bulletin_board"],
            "characters_present": [],
            "activities_description": "The square is bustling with morning activity. Birds chirping near the fountain."
        },
        {
            "name": "Coffee Shop",
            "available_objects": ["coffee_machine", "table", "chair", "menu_board", "laptop"],
            "characters_present": [],
            "activities_description": "The aroma of freshly brewed coffee fills the air. Quiet jazz music plays softly."
        },
        {
            "name": "City Park",
            "available_objects": ["swing", "basketball_court", "picnic_table", "walking_trail"],
            "characters_present": [],
            "activities_description": "Peaceful morning in the park. A few joggers pass by on the trail."
        }
    ]
    
    space_results = await db.spaces.insert_many(spaces)
    space_ids = [str(id) for id in space_results.inserted_ids]
    print(f"Created {len(space_ids)} spaces")
    
    # Create relationships (one-way, so we create 2 for each pair)
    print("Creating relationships...")
    
    relationships = [
        # Sarah -> Mike
        {
            "from_character_id": char_ids[0],  # Sarah
            "to_character_id": char_ids[1],    # Mike
            "relationship_type": "Friendly",
            "relationship_summary": "Sarah appreciates Mike's positive energy and enthusiasm. She enjoys their conversations about balancing work and fitness.",
            "relationship_score": 45,
            "interaction_history": [
                {
                    "timestamp": datetime.utcnow(),
                    "action_type": "dialog",
                    "summary": "Had a friendly conversation about programming and fitness routines",
                    "emotional_impact": "Sarah felt encouraged and motivated",
                    "relationship_score_change": 5
                }
            ],
            "current_interaction_state": "none"
        },
        # Mike -> Sarah
        {
            "from_character_id": char_ids[1],  # Mike
            "to_character_id": char_ids[0],    # Sarah
            "relationship_type": "Friendly",
            "relationship_summary": "Mike finds Sarah interesting and admires her technical skills. He wants to help her achieve her fitness goals.",
            "relationship_score": 50,
            "interaction_history": [
                {
                    "timestamp": datetime.utcnow(),
                    "action_type": "dialog",
                    "summary": "Had a friendly conversation about programming and fitness routines",
                    "emotional_impact": "Mike felt happy to share his knowledge",
                    "relationship_score_change": 5
                }
            ],
            "current_interaction_state": "none"
        },
        # Sarah -> Emma
        {
            "from_character_id": char_ids[0],  # Sarah
            "to_character_id": char_ids[2],    # Emma
            "relationship_type": "Professional",
            "relationship_summary": "Sarah respects Emma's artistic talent and is impressed by her design work. She hopes they can become friends.",
            "relationship_score": 30,
            "interaction_history": [],
            "current_interaction_state": "none"
        },
        # Emma -> Sarah
        {
            "from_character_id": char_ids[2],  # Emma
            "to_character_id": char_ids[0],    # Sarah
            "relationship_type": "Professional",
            "relationship_summary": "Emma appreciates Sarah's clear communication and creative project ideas. She feels a bit intimidated by Sarah's technical expertise.",
            "relationship_score": 25,
            "interaction_history": [],
            "current_interaction_state": "none"
        }
    ]
    
    rel_results = await db.relationships.insert_many(relationships)
    print(f"Created {len(rel_results.inserted_ids)} relationships (one-way)")
    
    # Update character relationships
    await db.characters.update_one(
        {"_id": char_results.inserted_ids[0]},  # Sarah
        {"$set": {"relationships": [char_ids[1], char_ids[2]]}}
    )
    await db.characters.update_one(
        {"_id": char_results.inserted_ids[1]},  # Mike
        {"$set": {"relationships": [char_ids[0]]}}
    )
    await db.characters.update_one(
        {"_id": char_results.inserted_ids[2]},  # Emma
        {"$set": {"relationships": [char_ids[0]]}}
    )
    
    # Create sample interaction
    print("Creating sample interaction...")
    
    interaction = {
        "timestamp": datetime.utcnow(),
        "participants": [char_ids[0], char_ids[1]],
        "action_type": "dialog",
        "summary": "Sarah and Mike bumped into each other at the coffee shop. They discussed their weekend plans and Mike invited Sarah to try a new workout class.",
        "emotional_impact": {
            "Sarah": "happy and motivated",
            "Mike": "friendly and enthusiastic"
        }
    }
    
    await db.interactions.insert_one(interaction)
    print("Created 1 sample interaction")
    
    # Close connection
    client.close()
    
    print("\nDatabase seeding completed successfully!")
    print(f"\nSummary:")
    print(f"  - Characters: {len(char_ids)}")
    print(f"  - Spaces: {len(space_ids)}")
    print(f"  - Relationships: {len(rel_results.inserted_ids)} (one-way)")
    print(f"  - Interactions: 1")
    print(f"\nYou can now start the API server with: uvicorn app.main:app --reload")


if __name__ == "__main__":
    asyncio.run(seed_database())


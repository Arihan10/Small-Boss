"""
Space Seeding Script
Generates appropriate spaces based on existing characters in the database.
Creates medieval town locations that match character occupations.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_DB_URI = os.getenv("MONGO_DB_URI", "mongodb://localhost:27017/ai_life_sim")
DATABASE_NAME = "ai_life_sim"


async def seed_spaces():
    """Create spaces based on existing characters."""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_DB_URI)
    db = client[DATABASE_NAME]
    
    print("=== Space Seeding Script ===\n")
    
    # Get all characters to understand the town
    characters = []
    async for char in db.characters.find():
        characters.append(char)
    
    print(f"Found {len(characters)} characters in the database")
    
    # Analyze character occupations
    occupations = {}
    for char in characters:
        occ = char.get('occupation', 'Unknown')
        if occ not in occupations:
            occupations[occ] = []
        occupations[occ].append(char['name'])
    
    print(f"\nOccupations found:")
    for occ, names in occupations.items():
        print(f"  - {occ}: {len(names)} ({', '.join(names)})")
    
    # Clear existing spaces
    print("\nClearing existing spaces...")
    deleted = await db.spaces.delete_many({})
    print(f"Deleted {deleted.deleted_count} existing spaces")
    
    # Define spaces based on medieval town + character occupations
    spaces = []
    
    # 1. The Sleeping Dragon Inn (Margery's inn)
    if 'Innkeeper' in occupations:
        innkeeper_name = occupations['Innkeeper'][0]
        spaces.append({
            "name": "The Sleeping Dragon Inn",
            "available_objects": [
                "bar_counter", "tables", "chairs", "fireplace", 
                "beds", "mugs", "barrel", "cooking_pot"
            ],
            "characters_present": [],
            "activities_description": f"{innkeeper_name} tends the bar while patrons chat by the fireplace. The warm scent of stew fills the air."
        })
    
    # 2. Blacksmith's Forge (Thomas's forge)
    if 'Blacksmith' in occupations:
        blacksmith_name = occupations['Blacksmith'][0]
        spaces.append({
            "name": "Blackwood Forge",
            "available_objects": [
                "anvil", "hammer", "forge", "bellows", 
                "workbench", "water_trough", "tools"
            ],
            "characters_present": [],
            "activities_description": f"The forge glows hot as {blacksmith_name} hammers steel. Sparks fly with each strike."
        })
    
    # 3. Bakery (Yuki's bakery)
    if 'Baker' in occupations:
        baker_name = occupations['Baker'][0]
        spaces.append({
            "name": "Tanaka's Bakery",
            "available_objects": [
                "oven", "counter", "shelves", "flour_sacks", 
                "rolling_pin", "bread_baskets", "mixing_bowl"
            ],
            "characters_present": [],
            "activities_description": f"Fresh bread bakes in the oven. {baker_name} kneads dough at the counter."
        })
    
    # 4. School/Classroom (Mei's school)
    if 'Teacher' in occupations:
        teacher_name = occupations['Teacher'][0]
        spaces.append({
            "name": "Millbrook School",
            "available_objects": [
                "desks", "chalkboard", "books", "globe", 
                "teacher_desk", "bookshelf", "maps"
            ],
            "characters_present": [],
            "activities_description": f"{teacher_name} prepares lessons at her desk. Student desks are arranged in neat rows."
        })
    
    # 5. Church (Father Dmitri's church)
    if 'Priest' in occupations:
        priest_name = occupations['Priest'][0]
        spaces.append({
            "name": "Sacred Heart Chapel",
            "available_objects": [
                "altar", "pews", "candles", "bible", 
                "confession_booth", "stained_glass", "pulpit"
            ],
            "characters_present": [],
            "activities_description": f"{priest_name} tends to the chapel. Candlelight flickers on stone walls."
        })
    
    # 6. Tailor Shop (Elena's shop)
    if 'Tailor' in occupations:
        tailor_name = occupations['Tailor'][0]
        spaces.append({
            "name": "Blackwood Tailoring",
            "available_objects": [
                "sewing_machine", "fabric_rolls", "mannequin", 
                "scissors", "thread", "measuring_tape", "table"
            ],
            "characters_present": [],
            "activities_description": f"{tailor_name} carefully stitches fabric. Colorful cloth drapes everywhere."
        })
    
    # 7. Merchant's Trading Post (Rafael & Isabella)
    if 'Merchant' in occupations:
        merchant_name = occupations['Merchant'][0]
        spaces.append({
            "name": "Cortez Trading Company",
            "available_objects": [
                "counter", "shelves", "crates", "scales", 
                "ledger", "coins", "goods", "storage"
            ],
            "characters_present": [],
            "activities_description": f"{merchant_name} organizes inventory. Various goods line the shelves."
        })
    
    # 8. Guard Post
    if 'Guard' in occupations:
        guard_name = occupations['Guard'][0]
        spaces.append({
            "name": "Town Guard Post",
            "available_objects": [
                "weapons_rack", "armor_stand", "desk", "map", 
                "bench", "torch", "training_dummy"
            ],
            "characters_present": [],
            "activities_description": f"{guard_name} keeps watch over the town. Weapons are ready and maintained."
        })
    
    # 9. Herbalist's Garden (Sarai's place)
    if 'Herbalist' in occupations:
        herbalist_name = occupations['Herbalist'][0]
        spaces.append({
            "name": "Garden of Remedies",
            "available_objects": [
                "herb_garden", "mortar_pestle", "shelves", 
                "bottles", "drying_herbs", "workbench", "cauldron"
            ],
            "characters_present": [],
            "activities_description": f"{herbalist_name} tends to medicinal plants. The scent of herbs fills the air."
        })
    
    # 10. Carpenter's Workshop (Wilhelm's workshop)
    if 'Carpenter' in occupations:
        carpenter_name = occupations['Carpenter'][0]
        spaces.append({
            "name": "Adler's Carpentry",
            "available_objects": [
                "workbench", "saw", "hammer", "wood_planks", 
                "nails", "chisel", "measuring_tools"
            ],
            "characters_present": [],
            "activities_description": f"{carpenter_name} shapes wood with precision. Sawdust covers the floor."
        })
    
    # 11. Mill (Hiroshi's mill)
    if 'Miller' in occupations:
        miller_name = occupations['Miller'][0]
        spaces.append({
            "name": "Nakamura's Mill",
            "available_objects": [
                "millstone", "grain_sacks", "wheel", "hopper", 
                "flour_barrels", "scale", "shovel"
            ],
            "characters_present": [],
            "activities_description": f"{miller_name} operates the mill. The great wheel turns steadily."
        })
    
    # 12. Farm (Amara's farm)
    if 'Farmer' in occupations:
        farmer_name = occupations['Farmer'][0]
        spaces.append({
            "name": "Okafor Family Farm",
            "available_objects": [
                "crops", "barn", "tools", "well", 
                "fence", "scarecrow", "wheelbarrow", "livestock"
            ],
            "characters_present": [],
            "activities_description": f"{farmer_name} tends the fields. Crops grow in neat rows."
        })
    
    # 13. Lumberyard (Nadya's workplace)
    if 'Lumberjack' in occupations:
        lumberjack_name = occupations['Lumberjack'][0]
        spaces.append({
            "name": "Forest Lumber Yard",
            "available_objects": [
                "logs", "axe", "saw", "cart", 
                "rope", "horses", "stump", "cabin"
            ],
            "characters_present": [],
            "activities_description": f"{lumberjack_name} splits logs with powerful swings. Horses wait patiently nearby."
        })
    
    # 14. Fishing Dock (Theodore's spot)
    if 'Fisherman' in occupations:
        fisherman_name = occupations['Fisherman'][0]
        spaces.append({
            "name": "River Dock",
            "available_objects": [
                "fishing_rod", "boat", "nets", "bucket", 
                "dock", "pier", "fish_barrel"
            ],
            "characters_present": [],
            "activities_description": f"{fisherman_name} casts his line into calm waters. Fish jump occasionally."
        })
    
    # 15. Common/Shared Spaces
    # Town Square - central gathering place
    spaces.append({
        "name": "Town Square",
        "available_objects": [
            "fountain", "benches", "notice_board", "statue", 
            "market_stalls", "street_lamp", "well"
        ],
        "characters_present": [],
        "activities_description": "The heart of Millbrook bustles with daily life. Townspeople gather to chat and trade."
    })
    
    # Forest Path - for adventurers
    spaces.append({
        "name": "Forest Path",
        "available_objects": [
            "trees", "path", "stones", "bushes", 
            "wildflowers", "stream", "wildlife"
        ],
        "characters_present": [],
        "activities_description": "A quiet path winds through tall trees. Birds sing in the canopy above."
    })
    
    # Riverbank - peaceful spot
    spaces.append({
        "name": "Riverbank",
        "available_objects": [
            "river", "rocks", "grass", "willow_tree", 
            "reeds", "bridge", "flowers"
        ],
        "characters_present": [],
        "activities_description": "The river flows gently past smooth stones. Willow branches sway in the breeze."
    })
    
    # Training Grounds - for Marcus and friends
    spaces.append({
        "name": "Training Grounds",
        "available_objects": [
            "training_dummies", "weapons_rack", "targets", 
            "sparring_area", "bench", "water_barrel"
        ],
        "characters_present": [],
        "activities_description": "An open area for combat practice. Training dummies stand ready."
    })
    
    # Market - shopping area
    spaces.append({
        "name": "Market Street",
        "available_objects": [
            "stalls", "crates", "awnings", "baskets", 
            "scales", "produce", "goods"
        ],
        "characters_present": [],
        "activities_description": "Merchants call out their wares. The market hums with commerce and conversation."
    })
    
    # Residential - homes
    spaces.append({
        "name": "Residential District",
        "available_objects": [
            "houses", "gardens", "fences", "doors", 
            "windows", "chimneys", "pathways"
        ],
        "characters_present": [],
        "activities_description": "Quiet homes line the street. Smoke rises from chimneys."
    })
    
    # Insert all spaces
    print(f"\nCreating {len(spaces)} spaces...")
    result = await db.spaces.insert_many(spaces)
    
    print(f"\n=== Successfully Created {len(result.inserted_ids)} Spaces ===\n")
    
    for i, space in enumerate(spaces):
        print(f"{i+1}. {space['name']}")
        print(f"   Objects: {len(space['available_objects'])}")
        print(f"   {space['activities_description'][:80]}...")
        print()
    
    # Close connection
    client.close()
    
    print("\nSpaces are ready for your AI life simulation!")
    print("Characters can now interact in these locations.\n")


if __name__ == "__main__":
    asyncio.run(seed_spaces())


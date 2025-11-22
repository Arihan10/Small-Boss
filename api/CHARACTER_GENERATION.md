# Character Generation Guide

## Overview

This system uses Claude 4.5 Sonnet to generate realistic, interconnected characters for your AI life simulation.

## Files

- `generate_characters.py` - AI-powered character generation (2-shot)
- `load_to_mongo.py` - Load generated JSON into MongoDB
- `generated_characters.json` - Output file (created after generation)

## Generation Process

### Two-Shot Approach

**Shot 1: Background Generation**
- Claude generates rich background stories for all 20 characters
- Focuses on interconnected narratives, families, relationships
- Creates a living, breathing medieval town

**Shot 2: Structured Parsing**
- Parses backgrounds into structured JSON
- Populates all character fields
- Creates relationship network
- Assigns appearance asset codes

## Character Fields

### Demographics
- `name` - Full name
- `age` - Age (5-60+)
- `race` - Realistic human ethnicity (White, Black, Asian, Hispanic, Middle Eastern, Native American, Mixed, etc.)
- `gender` - Male/Female/Non-binary
- `occupation` - Medieval job (Farmer, Blacksmith, etc.)

### Appearance (Asset Codes)
```json
{
  "hair": 0-15,    // Hair style
  "shoes": 0-6,    // Footwear
  "bottom": 0-5,   // Pants/skirt/etc
  "top": 0-10      // Shirt/jacket/etc
}
```

### Personality & Background
- `background` - Life story (2-3 sentences)
- `personality_traits` - Array of trait strings

### State
- `needs` - happiness, energy, hunger, hygiene (0-100)

### Relationships (One-Way)
Each character has relationships TO other characters:
```json
{
  "target_name": "Name",
  "relationship_type": "Family/Friend/Romantic/etc",
  "relationship_summary": "How this character feels",
  "relationship_score": -100 to 100
}
```

## Usage

### 1. Generate Characters

```bash
python generate_characters.py
```

**Requirements:**
- `ANTHROPIC_API_KEY` in `.env` file
- Internet connection
- Takes ~30-60 seconds

**Output:**
- Creates `generated_characters.json`
- Contains 20 characters with full data
- Relationship network included

### 2. Load into MongoDB

```bash
python load_to_mongo.py
```

**What it does:**
- Clears existing database
- Loads all characters
- Creates bidirectional relationships
- Updates character relationship lists

**Output:**
- Characters in MongoDB
- Relationships established
- Ready for API use

### 3. Start API Server

```bash
uvicorn app.main:app --reload
```

View characters at: http://localhost:8000/docs

## Customization

### Change Number of Characters

Edit `generate_characters.py`:
```python
NUM_CHARACTERS = 30  # Change from 20
```

### Change Setting

Edit `generate_characters.py`:
```python
SETTING = "cyberpunk city"  # or "fantasy village", etc.
```

### Change Jobs

Edit `MEDIEVAL_JOBS` list in `generate_characters.py`:
```python
MEDIEVAL_JOBS = [
    "Cyberdeck Hacker",
    "Neon District Vendor",
    ...
]
```

## Appearance Asset Codes

### Hair (0-15)
- 0-2: Afro styles
- 3: Buzzcut
- 4-5: Curly
- 6-7: Medium length
- 8-11: Short variations
- 12: Bun
- 13: Ponytail
- 14: Double buns
- 15: Twintails

### Shoes (0-6)
- 0: Girly boots
- 1: Orange running shoes
- 2: Sandals
- 3: Slippers
- 4: Boots
- 5: Sketchers
- 6: Worker boots

### Bottom (0-5)
- 0: Black pants
- 1: Shorts
- 2: Skirt
- 3: Jeans
- 4: Long shorts (girly)
- 5: Baggy joggers

### Top (0-10)
- 0: White gym shirt
- 1: Jacket
- 2: Sweater
- 3: Button shirt (orange)
- 4: Layered sweater
- 5: Flannel over white t
- 6: Crop top with yellow jacket
- 7: Striped shirt
- 8: Green hoodie
- 9: Shirt with tie
- 10: Suit top

## Generated Relationship Types

- **Family** - Parents, children, siblings, spouses
- **Friend** - Close friendships
- **Romantic** - Love interests, crushes
- **Professional** - Work relationships
- **Rival** - Antagonistic relationships

## Relationship Scores

- **80-100**: Very positive (best friends, family, love)
- **40-80**: Positive (friends, good acquaintances)
- **0-40**: Neutral (colleagues, casual acquaintances)
- **-40-0**: Tense (disagreements, mild conflict)
- **-100--40**: Hostile (enemies, rivals)

## Tips

1. **Review Generated JSON** - Check `generated_characters.json` before loading to MongoDB
2. **Regenerate if Needed** - Just run `generate_characters.py` again
3. **Backup** - Keep good generations as backup files
4. **Iterate** - Modify the prompts for different town dynamics

## Troubleshooting

**"ANTHROPIC_API_KEY not found"**
- Add to `.env` file: `ANTHROPIC_API_KEY=sk-ant-...`

**"JSON parsing error"**
- Claude output may need cleaning
- Check `generated_characters.json` for syntax errors
- Regenerate if corrupted

**"Character not found in relationships"**
- Character name mismatch
- Will skip invalid relationships with warning
- Most relationships should still work

**MongoDB connection failed**
- Check `MONGO_DB_URI` in `.env`
- Ensure MongoDB is running

## Example Output

```json
{
  "name": "Thomas the Blacksmith",
  "age": 42,
  "race": "White",
  "gender": "Male",
  "occupation": "Blacksmith",
  "background": "Master craftsman who inherited the forge from his father...",
  "personality_traits": ["hardworking", "honest", "gruff", "protective"],
  "appearance": {
    "hair": 3,   // buzzcut
    "shoes": 6,  // worker boots
    "bottom": 0, // black pants
    "top": 5     // flannel over white t
  },
  "relationships": [
    {
      "target_name": "Margaret the Baker",
      "relationship_type": "Romantic",
      "relationship_summary": "Has had feelings for her for years but hasn't confessed",
      "relationship_score": 65
    }
  ]
}
```

## Next Steps

After loading characters:
1. Test API endpoints
2. Integrate with Unity
3. Implement LLM decision-making (`.decide()`)
4. Build interaction system

Good luck with your AI life simulation! 🎮


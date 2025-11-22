# AI Life Simulation - Backend API

FastAPI backend for an AI-powered life simulation game, built to integrate with Unity. This API manages characters, relationships, spaces, and interactions in a dynamic simulation world.

## Features

- **Character Management**: Create and manage AI-powered characters with personalities, needs, and memories
- **Relationship System**: Track bidirectional relationships between characters with interaction histories
- **Space Management**: Manage locations with dynamic state tracking
- **Interaction Logging**: Record and retrieve character interactions
- **MongoDB Integration**: Async MongoDB support with Motor
- **REST API**: Full CRUD operations for all entities
- **CORS Enabled**: Ready for Unity integration

## Project Structure

```
api/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration and environment settings
│   ├── database.py          # MongoDB connection management
│   ├── models/              # Pydantic models and schemas
│   │   ├── enums.py        # Interaction state enums
│   │   ├── character.py    # Character models
│   │   ├── relationship.py # Relationship models
│   │   ├── space.py        # Space models
│   │   └── interaction.py  # Interaction models
│   └── routes/              # API endpoints
│       ├── characters.py   # Character endpoints
│       ├── relationships.py # Relationship endpoints
│       ├── spaces.py       # Space endpoints
│       └── interactions.py # Interaction endpoints
├── seed.py                  # Database seeding script
├── requirements.txt         # Python dependencies
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- MongoDB (local or cloud instance like MongoDB Atlas)

### Installation

1. **Clone the repository** (or navigate to the api directory)

```bash
cd api
```

2. **Create a virtual environment**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

Create a `.env` file in the root directory:

```env
MONGO_DB_URI=mongodb://localhost:27017/ai_life_sim
```

For MongoDB Atlas (cloud):
```env
MONGO_DB_URI=mongodb+srv://username:password@cluster.mongodb.net/ai_life_sim
```

### Running the Server

1. **Start the FastAPI server**

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

2. **View the interactive API documentation**

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Seeding the Database

To populate the database with example data:

```bash
python seed.py
```

This will create:
- 4 example characters (Sarah, Mike, Emma, David)
- 3 spaces (Town Square, Coffee Shop, City Park)
- 2 relationships
- 1 sample interaction

## API Endpoints

### Characters (Unity-Focused)

- `GET /characters` - List all characters
- `GET /characters/{id}` - Get character by ID
- `POST /characters/{id}/use/{object}` - Use object (AI flavor text with emoji)

### Relationships

- `GET /characters/{id}/relationships` - Get outgoing relationships
- `GET /characters/{id}/incoming` - Get incoming relationships

### Spaces

- `GET /spaces` - List all spaces
- `GET /spaces/{id}` - Get space by ID
- `PUT /spaces/{id}/characters` - Update characters present
- `PUT /spaces/{id}/generate-activities` - AI-generate scene description

### Interaction Sessions

- `POST /interaction-sessions/` - Start conversation
- `GET /interaction-sessions/{id}` - Get session state
- `POST /interaction-sessions/{id}/advance` - AI-advance conversation
- `POST /interaction-sessions/{id}/end` - End conversation

> **📖 See [API_ENDPOINTS.md](API_ENDPOINTS.md) for complete Unity integration guide with examples**

## Data Models

### Character

```json
{
  "name": "Sarah Chen",
  "age": 28,
  "appearance": {
    "hair": 12,
    "shoes": 1,
    "bottom": 3,
    "top": 8
  },
  "race": "Asian",
  "gender": "Female",
  "occupation": "Software Engineer",
  "background": "Grew up in a small town...",
  "personality_traits": ["ambitious", "creative", "driven", "friendly"],
  "needs": {
    "happiness": 70,
    "energy": 60,
    "hunger": 40,
    "hygiene": 80
  },
  "current_desire": "Wants to grab coffee",
  "action_log": [],
  "memory_log": [],
  "relationships": []
}
```

### Relationship (One-Way)

**Note:** Relationships are directional. Each pair of characters has two separate relationships - one for how A feels about B, and one for how B feels about A.

```json
{
  "from_character_id": "507f1f77bcf86cd799439011",
  "to_character_id": "507f1f77bcf86cd799439012",
  "relationship_type": "Friendly",
  "relationship_summary": "Sarah admires Mike's positive energy and enjoys their conversations",
  "relationship_score": 45,
  "interaction_history": [],
  "current_interaction_state": "none"
}
```

### Space

```json
{
  "name": "Coffee Shop",
  "available_objects": ["coffee_machine", "table", "chair"],
  "characters_present": [],
  "activities_description": "Quiet morning atmosphere. A few patrons working on laptops."
}
```

## Unity Integration

The API is configured with CORS to allow requests from Unity. Use UnityWebRequest or similar to make HTTP calls:

```csharp
// Example: Get all characters
UnityWebRequest request = UnityWebRequest.Get("http://localhost:8000/characters");
yield return request.SendWebRequest();

if (request.result == UnityWebRequest.Result.Success) {
    string jsonResponse = request.downloadHandler.text;
    // Parse JSON and use data
}
```

## Development Notes

### For LLM Integration

The following methods are designed for future LLM integration but are currently unimplemented:

- `.decide()` - Character decision making based on context
- `.use(object)` - Generic object interaction with LLM-generated text
- Interaction summaries - Generated after conversations/interactions end
- Relationship summaries - Narrative descriptions of relationships

These can be implemented using OpenAI API, Anthropic, or other LLM providers.

### Database Collections

- `characters` - All character data
- `relationships` - Bidirectional relationship edges
- `spaces` - Location/space data
- `interactions` - Historical interaction logs

### Architecture Notes

- **Async/Await**: All database operations are async for better performance
- **Motor Driver**: Async MongoDB driver compatible with FastAPI
- **Pydantic Models**: Type-safe request/response validation
- **ID Format**: MongoDB ObjectId, returned as strings in API responses

## Testing

Use the interactive documentation at `/docs` to test endpoints, or use tools like:

- Postman
- Thunder Client (VS Code extension)
- curl

Example curl command:

```bash
# Create a character
curl -X POST "http://localhost:8000/characters" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Character",
    "age": 25,
    "appearance": "Test appearance",
    "race": "Human",
    "gender": "Other",
    "occupation": "Tester",
    "background": "A test character"
  }'
```

## Troubleshooting

### MongoDB Connection Issues

- Ensure MongoDB is running: `mongod` (for local installations)
- Check your `MONGO_DB_URI` in `.env`
- For MongoDB Atlas, ensure your IP is whitelisted

### Port Already in Use

```bash
# Run on different port
uvicorn app.main:app --reload --port 8001
```

## Future Enhancements

- [ ] Implement LLM integration for `.decide()` method
- [ ] Add WebSocket support for real-time updates
- [ ] Implement authentication/authorization
- [ ] Add rate limiting
- [ ] Create background tasks for periodic AI decisions
- [ ] Add context system for local/global character awareness
- [ ] Implement interaction state machine

## License

Built for Hack Western hackathon project.


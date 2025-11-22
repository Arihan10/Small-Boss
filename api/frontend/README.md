# AI Life Simulation - React Frontend

A simple React frontend for testing the turn-based interaction system.

## Setup

```bash
cd frontend
npm install
```

## Run

Make sure the FastAPI backend is running first:
```bash
# In the api directory
uvicorn app.main:app --reload
```

Then start the frontend:
```bash
# In the frontend directory
npm run dev
```

Visit http://localhost:3000

## Features

- **Character Selection**: Browse and select medieval town characters
- **Turn-Based Interactions**: Start conversations between 2-4 characters
- **Real-time Chat**: Take turns speaking as different characters
- **Actions**: Talk, emote, or leave the conversation
- **Session Management**: Interactions are saved and can be ended

## How to Use

1. Select 2-4 characters from the list
2. Click "Start Interaction"
3. Take turns typing what each character says
4. Use action buttons:
   - **Talk**: Send a message
   - **Emote**: Perform an action (e.g., *laughs*, *sighs*)
   - **Leave**: End the interaction for that character
5. Click "End Interaction" to finish and save the conversation

## API Integration

The frontend connects to the FastAPI backend via proxy:
- Characters API: `/api/characters`
- Interaction Sessions: `/api/interaction-sessions`

All interactions are stored in MongoDB with full conversation history.


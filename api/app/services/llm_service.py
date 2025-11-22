"""LLM service for generating character responses and interactions."""

import os
from anthropic import AsyncAnthropic
from app.config import settings


class LLMService:
    """Service for making LLM calls."""
    
    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = "claude-sonnet-4-20250514"
    
    async def generate_dialogue(
        self,
        character,
        other_characters,
        conversation_history,
        space_info=None,
        relationships=None
    ) -> str:
        """
        Generate what a character would say in a conversation.
        
        Args:
            character: The character who is speaking
            other_characters: Other participants in the conversation
            conversation_history: Previous messages in this interaction
            space_info: Information about where this is happening
            relationships: Character's relationships with other participants
        
        Returns:
            What the character says
        """
        
        # Build comprehensive context
        context_parts = []
        
        # Character identity
        context_parts.append(f"You are {character['name']}, a {character['age']}-year-old {character['race']} {character['occupation']}.")
        context_parts.append(f"Background: {character['background']}")
        context_parts.append(f"Personality: {', '.join(character['personality_traits'])}")
        
        # Current state/needs
        needs = character.get('needs', {})
        context_parts.append(f"\nCurrent state:")
        context_parts.append(f"- Happiness: {needs.get('happiness', 50)}/100")
        context_parts.append(f"- Energy: {needs.get('energy', 50)}/100")
        context_parts.append(f"- Hunger: {needs.get('hunger', 50)}/100")
        
        if character.get('current_desire'):
            context_parts.append(f"- Current desire: {character['current_desire']}")
        
        # Recent memories
        if character.get('memory_log'):
            context_parts.append(f"\nRecent memories:")
            for memory in character['memory_log'][-3:]:
                context_parts.append(f"- {memory['event']}")
        
        # Recent actions
        if character.get('action_log'):
            context_parts.append(f"\nRecent actions:")
            for action in character['action_log'][-3:]:
                context_parts.append(f"- {action['action']}: {action.get('details', '')}")
        
        # Relationships with other participants
        if relationships:
            context_parts.append(f"\nYour relationships:")
            for rel in relationships:
                other_char = next((c for c in other_characters if c['_id'] == rel['to_character_id']), None)
                if other_char:
                    context_parts.append(f"- {other_char['name']}: {rel['relationship_type']} (score: {rel['relationship_score']}/100)")
                    context_parts.append(f"  {rel['relationship_summary']}")
                    
                    # Recent interactions
                    if rel.get('interaction_history'):
                        recent = rel['interaction_history'][-2:]
                        if recent:
                            context_parts.append(f"  Recent interactions:")
                            for interaction in recent:
                                context_parts.append(f"  - {interaction['summary']}")
        
        # Space/location context
        if space_info:
            context_parts.append(f"\nLocation: {space_info['name']}")
            if space_info.get('activities_description'):
                context_parts.append(f"What's happening here: {space_info['activities_description']}")
            if space_info.get('available_objects'):
                context_parts.append(f"Objects nearby: {', '.join(space_info['available_objects'])}")
        
        # Other participants in conversation
        context_parts.append(f"\nYou are talking with:")
        for other in other_characters:
            context_parts.append(f"- {other['name']}: {other['age']}yo {other['occupation']}")
            context_parts.append(f"  Personality: {', '.join(other['personality_traits'][:3])}")
        
        # Conversation so far
        if conversation_history:
            context_parts.append(f"\nConversation so far:")
            for msg in conversation_history:
                speaker = msg['character_name']
                content = msg['content']
                context_parts.append(f"{speaker}: {content}")
        else:
            context_parts.append(f"\nThis conversation is just starting.")
        
        # Build the prompt
        context = "\n".join(context_parts)
        
        prompt = f"""{context}

Based on your personality, current state, relationships, and the conversation so far, what would you say next?

IMPORTANT:
- Stay in character based on your personality traits and background
- Consider your relationship with the other person/people
- Your response should be natural and realistic
- Keep it to 1-3 sentences
- Show emotion and personality
- Do NOT use asterisks or actions, just speak naturally

Respond ONLY with what {character['name']} would say (no quotes, no labels, just the dialogue):"""

        # Call Claude
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=300,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        return response.content[0].text.strip()
    
    async def generate_object_interaction(
        self,
        character,
        object_name: str,
        space_info=None
    ) -> str:
        """
        Generate flavor text for a character interacting with an object.
        
        Args:
            character: The character using the object
            object_name: Name of the object being used
            space_info: Optional space/location context
        
        Returns:
            Flavor text describing the interaction
        """
        
        # Build context
        context_parts = []
        
        context_parts.append(f"Character: {character['name']}, a {character['age']}-year-old {character['occupation']}")
        context_parts.append(f"Personality: {', '.join(character['personality_traits'][:4])}")
        
        # Current state
        needs = character.get('needs', {})
        context_parts.append(f"Current mood/state:")
        context_parts.append(f"- Happiness: {needs.get('happiness', 50)}/100")
        context_parts.append(f"- Energy: {needs.get('energy', 50)}/100")
        
        if character.get('current_desire'):
            context_parts.append(f"- Current desire: {character['current_desire']}")
        
        # Location context
        if space_info:
            context_parts.append(f"\nLocation: {space_info['name']}")
            if space_info.get('activities_description'):
                context_parts.append(f"Scene: {space_info['activities_description']}")
        
        context = "\n".join(context_parts)
        
        prompt = f"""{context}

{character['name']} is interacting with: {object_name}

Generate a SHORT, punchy flavor text (5-8 words max) describing this interaction. This will appear as a subtitle above the character.

IMPORTANT:
- Keep it VERY SHORT (5-8 words maximum)
- Include 1-2 relevant emojis
- Use third person (e.g., "sits on the bench 🪑")
- Show their personality in the action
- Make it interesting but concise
- NO full sentences, just key action + emoji

Example GOOD formats:
- "polishing mugs behind the bar 🍺✨"
- "hammering metal at the forge ⚒️🔥"
- "reading by the fireplace 📖🔥"
- "napping on a bench 😴💤"
- "practicing sword swings ⚔️💪"

BAD (too long): "Sarah sits down on the bench and contemplates her day"
GOOD (concise): "resting on the bench 🪑💭"

Generate the flavor text:"""

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=50,  # Reduced for shorter responses
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        return response.content[0].text.strip()
    
    async def generate_space_activities(
        self,
        space,
        characters: list
    ) -> str:
        """
        Generate a description of what's happening in a space.
        
        Args:
            space: The space/location
            characters: List of characters currently in the space
        
        Returns:
            A vivid description of the scene
        """
        
        if not characters:
            # No characters present - describe empty space
            return f"{space['name']} is quiet and empty. The atmosphere is peaceful and undisturbed."
        
        # Build context
        context_parts = []
        
        context_parts.append(f"Location: {space['name']}")
        
        if space.get('available_objects'):
            context_parts.append(f"Available objects: {', '.join(space['available_objects'][:10])}")
        
        context_parts.append(f"\nCharacters present ({len(characters)}):")
        
        for char in characters:
            context_parts.append(f"\n- {char['name']} ({char['age']}yo {char['occupation']})")
            context_parts.append(f"  Personality: {', '.join(char['personality_traits'][:3])}")
            
            # Current state
            needs = char.get('needs', {})
            context_parts.append(f"  Energy: {needs.get('energy', 50)}/100, Happiness: {needs.get('happiness', 50)}/100")
            
            if char.get('current_desire'):
                context_parts.append(f"  Wants to: {char['current_desire']}")
            
            # Recent actions
            if char.get('action_log'):
                recent_actions = char['action_log'][-2:]
                if recent_actions:
                    context_parts.append(f"  Recent actions:")
                    for action in recent_actions:
                        context_parts.append(f"    - {action['action']}: {action.get('details', '')[:50]}")
        
        context = "\n".join(context_parts)
        
        prompt = f"""{context}

Generate a concise, factual description of what's happening in {space['name']} right now.

IMPORTANT:
- Describe what EACH person is doing in simple, clear terms
- Write in present tense
- Be direct and descriptive, not flowery or narrative
- No embellishments, sensory details, or storytelling flourishes
- Just state the facts of what each person is doing
- Keep it short and to-the-point

Example good format: "Margery is tending the bar counter. Thomas is sitting by the fireplace. Marcus and Johan are talking in the corner."

BAD (too flowery): "Margery tends the bar with practiced efficiency, her sharp eyes missing nothing as she polishes mugs with care."

GOOD (concise): "Margery is cleaning mugs at the bar."

Generate the scene description:"""

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=400,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        return response.content[0].text.strip()
    
    async def generate_interaction_summary(
        self,
        participants,
        messages,
        interaction_type
    ) -> dict:
        """
        Generate a summary of an interaction after it ends.
        
        Returns dict with:
        - summary: Text description
        - emotional_impact: Dict of how each character felt
        - relationship_changes: Suggested score changes
        """
        
        # Build conversation transcript
        transcript = "\n".join([
            f"{msg['character_name']}: {msg['content']}"
            for msg in messages
        ])
        
        participant_names = [p['name'] for p in participants]
        
        prompt = f"""Summarize this {interaction_type} between {', '.join(participant_names)}:

{transcript}

Provide:
1. A brief summary (2-3 sentences) of what happened
2. How each person felt emotionally
3. How this might affect their relationship (score change from -10 to +10)

Format your response as:
SUMMARY: [your summary]
EMOTIONAL_IMPACT: [character1]: [feeling], [character2]: [feeling]
RELATIONSHIP_CHANGE: [+5 or -3, etc. based on how positive/negative the interaction was]"""

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        text = response.content[0].text
        
        # Parse response (simple parsing)
        summary = ""
        emotional_impact = {}
        relationship_change = 0
        
        for line in text.split('\n'):
            if line.startswith('SUMMARY:'):
                summary = line.replace('SUMMARY:', '').strip()
            elif line.startswith('EMOTIONAL_IMPACT:'):
                impact_text = line.replace('EMOTIONAL_IMPACT:', '').strip()
                # Parse character feelings
                for part in impact_text.split(','):
                    if ':' in part:
                        char, feeling = part.split(':', 1)
                        emotional_impact[char.strip()] = feeling.strip()
            elif line.startswith('RELATIONSHIP_CHANGE:'):
                change_text = line.replace('RELATIONSHIP_CHANGE:', '').strip()
                try:
                    relationship_change = int(change_text.replace('+', ''))
                except:
                    relationship_change = 0
        
        return {
            "summary": summary or text[:200],
            "emotional_impact": emotional_impact,
            "relationship_change": relationship_change
        }


# Singleton instance
_llm_service = None

def get_llm_service() -> LLMService:
    """Get the LLM service singleton."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


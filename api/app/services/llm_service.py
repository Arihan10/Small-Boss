"""LLM service for generating character responses and interactions."""

import os
import asyncio
from cerebras.cloud.sdk import Cerebras
from app.config import settings


class LLMService:
    """Service for making LLM calls."""
    
    def __init__(self):
        self.client = Cerebras(api_key=settings.cerebras_api_key)
        self.model = "qwen-3-235b-a22b-instruct-2507"
    
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
        
        # Recent memories (show up to 20 for maximum context)
        if character.get('memory_log'):
            context_parts.append(f"\nRecent memories:")
            for memory in character['memory_log'][-20:]:
                context_parts.append(f"- {memory['event']}")
        
        # Recent actions (show up to 20 for maximum context)
        if character.get('action_log'):
            context_parts.append(f"\nRecent actions:")
            for action in character['action_log'][-20:]:
                context_parts.append(f"- {action['action']}: {action.get('details', '')}")
        
        # Relationships with other participants (bidirectional format)
        if relationships:
            context_parts.append(f"\nYour relationships:")
            for rel in relationships:
                # Extract this character's perspective
                char_id = str(character['_id'])
                if str(rel.get('character_id_1')) == char_id:
                    # This character is char1
                    other_id = rel.get('character_id_2')
                    my_score = rel.get('char1_score', 0)
                    my_summary = rel.get('char1_summary', '')
                    rel_type = rel.get('char1_relationship_type', 'Acquaintance')
                    my_history = rel.get('char1_interaction_history', [])
                else:
                    # This character is char2
                    other_id = rel.get('character_id_1')
                    my_score = rel.get('char2_score', 0)
                    my_summary = rel.get('char2_summary', '')
                    rel_type = rel.get('char2_relationship_type', 'Acquaintance')
                    my_history = rel.get('char2_interaction_history', [])
                
                other_char = next((c for c in other_characters if str(c['_id']) == other_id), None)
                if other_char:
                    context_parts.append(f"- {other_char['name']}: {rel_type} (score: {my_score}/100)")
                    context_parts.append(f"  {my_summary}")
                    
                    # Recent interactions (show up to 10 for context)
                    if my_history:
                        recent = my_history[-10:]
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

        # Call Cerebras
        response = await asyncio.to_thread(
            lambda: self.client.chat.completions.create(
                model=self.model,
                max_tokens=300,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
        )
        
        return response.choices[0].message.content.strip()
    
    async def generate_object_interaction(
        self,
        character,
        object_name: str
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

        response = await asyncio.to_thread(
            lambda: self.client.chat.completions.create(
                model=self.model,
                max_tokens=50,  # Reduced for shorter responses
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
        )
        
        return response.choices[0].message.content.strip()
    
    # Removed generate_space_activities - no longer used (spaces managed by Unity)
    
    async def generate_space_context_from_characters(
        self,
        space_name: str,
        characters: list,
        available_objects: list = None,
        current_description: str = None
    ) -> str:
        """
        Generate space context description from characters present.
        Only describes what they're ACTUALLY doing based on current_desire and recent actions.
        Unity provides available_objects for this space.
        Updates current_description minimally if provided.
        """
        
        if not characters:
            return ""
        
        # Build ACTUAL activity descriptions
        descriptions = []
        for char in characters:
            # Get their actual current activity
            desire = char.get('current_desire', '')
            recent_actions = char.get('action_log', [])
            
            # Get last action if exists
            last_action = None
            if recent_actions:
                last_action = recent_actions[-1].get('action', '')
            
            # Only describe if they have a desire or recent action
            if desire:
                descriptions.append(f"{char['name']} (wants to: {desire})")
            elif last_action and last_action != 'decided':
                descriptions.append(f"{char['name']} (recently: {last_action})")
            else:
                descriptions.append(f"{char['name']}")
        
        # If no one has desires or actions, return nothing
        if all('wants to' not in d and 'recently' not in d for d in descriptions):
            return ""
        
        # Create simple list-based description
        context = "\n".join(descriptions)
        
        # Add available objects if provided
        objects_context = ""
        if available_objects:
            objects_context = f"\nAvailable objects in this space: {', '.join(available_objects)}"
            
        # Add previous description context
        prev_desc_context = ""
        if current_description:
            prev_desc_context = f"\nPREVIOUS DESCRIPTION: {current_description}\n\nINSTRUCTION: Update the previous description ONLY if character activities have changed. Maintain consistency. If nothing changed, return the exact same string."
        
        prompt = f"""Location: {space_name}{objects_context}

Characters present and their current states:
{context}
{prev_desc_context}

Generate a FACTUAL, LITERAL description of what each person is doing OR wanting to do.

🚨 CRITICAL: If someone "wants to" do something social (talk, confront, etc.), they are NOT currently doing it yet!

RULES:
- If someone "wants to" do something social → say "wants to" or "is looking to"
- If someone "recently" did a SOLO action (organized, worked, read) → say "is [doing that]" 
- If someone has NO desire and NO recent action → say "is present" or omit them
- Be concise and factual
- NO creative storytelling
- DO NOT make conversations sound active when they haven't started

Examples:
- Marcus (wants to: talk to Isabella) → "Marcus is looking for a chance to talk to Isabella."
- Aldric (wants to: confront Elena about discipline) → "Aldric wants to speak with Elena about her responsibilities."
- Isabella (recently: organizing inventory) → "Isabella is organizing inventory."
- Thomas → "Thomas is present."

Generate ONLY literal description:"""

        response = await asyncio.to_thread(
            lambda: self.client.chat.completions.create(
                model=self.model,
                max_tokens=150,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
        )
        
        result = response.choices[0].message.content.strip()
        
        # If result is too generic or empty, just return empty string
        if not result or len(result) < 10:
            return ""
        
        return result
    
    async def generate_decision_for_unity(
        self,
        character,
        trigger_source: str,
        space_states: list,
        global_context=None,
        relationships=None,
        nearby_characters=None,
        active_conversation=None
    ) -> dict:
        """
        Generate a decision for Unity integration.
        Can perceive multiple spaces (perception radius may overlap).
        Returns action object with actionType and props.
        """
        
        # Build comprehensive context
        context_parts = []
        
        # Character identity
        context_parts.append(f"You are {character['name']}, a {character['age']}-year-old {character['occupation']}.")
        context_parts.append(f"Background: {character['background']}")
        
        # Personality (decision-guiding)
        context_parts.append(f"\nPersonality:")
        for trait in character.get('personality_traits', []):
            context_parts.append(f"- {trait}")
        
        # Current state
        needs = character.get('needs', {})
        context_parts.append(f"\nCurrent State:")
        context_parts.append(f"- Happiness: {needs.get('happiness', 50)}/100")
        context_parts.append(f"- Energy: {needs.get('energy', 50)}/100")
        context_parts.append(f"- Hunger: {needs.get('hunger', 50)}/100")
        context_parts.append(f"- Hygiene: {needs.get('hygiene', 50)}/100")
        
        if character.get('current_desire'):
            context_parts.append(f"- Current desire: {character['current_desire']}")
        
        # Visible spaces (perception radius - can see multiple)
        if space_states and len(space_states) > 0:
            context_parts.append(f"\nVisible Locations (in perception radius):")
            for space_state in space_states:
                context_parts.append(f"\n- {space_state.space_name}:")
                if space_state.description:
                    context_parts.append(f"  Scene: {space_state.description}")
                if space_state.characters_present:
                    context_parts.append(f"  People: {', '.join(space_state.characters_present)}")
                if space_state.available_objects:
                    context_parts.append(f"  Objects: {', '.join(space_state.available_objects[:8])}")
        
        # Relationships with nearby people
        if relationships and nearby_characters:
            context_parts.append(f"\nRelationships with visible people:")
            for rel in relationships:
                # Extract this character's perspective
                if str(rel.get("character_id_1")) == str(character["_id"]):
                    other_id = rel.get("character_id_2")
                    my_score = rel.get("char1_score", 0)
                    my_summary = rel.get("char1_summary", "")
                    rel_type = rel.get("char1_relationship_type", "Acquaintance")
                    my_history = rel.get("char1_interaction_history", [])
                else:
                    other_id = rel.get("character_id_1")
                    my_score = rel.get("char2_score", 0)
                    my_summary = rel.get("char2_summary", "")
                    rel_type = rel.get("char2_relationship_type", "Acquaintance")
                    my_history = rel.get("char2_interaction_history", [])
                
                # Find if this person is nearby
                other_char = next((c for c in nearby_characters if str(c["_id"]) == other_id), None)
                if other_char:
                    context_parts.append(f"- {other_char['name']}: {rel_type} (score: {my_score}/100)")
                    if my_summary:
                        context_parts.append(f"  {my_summary}")
                    
                    # Show recent interactions with this person (up to 10 for maximum context)
                    if my_history:
                        recent_interactions = my_history[-10:]
                        if recent_interactions:
                            context_parts.append(f"  Recent interactions:")
                            for interaction in recent_interactions:
                                summary = interaction.get('summary', '')
                                feeling = interaction.get('emotional_impact', '')
                                # Truncate long summaries
                                if len(summary) > 80:
                                    summary = summary[:80] + "..."
                                context_parts.append(f"    - {summary} (felt: {feeling})")
        
        # Recent memories (show up to 20 for maximum context)
        if character.get('memory_log'):
            context_parts.append(f"\nRecent Memories:")
            for memory in character['memory_log'][-20:]:
                context_parts.append(f"- {memory['event']}")
        
        # Recent actions (show up to 20 for maximum context - CRITICAL for understanding current state)
        if character.get('action_log'):
            context_parts.append(f"\nRecent Actions:")
            for action in character['action_log'][-20:]:
                context_parts.append(f"- {action['action']}: {action.get('details', '')[:60]}")
        
        # Global context
        if global_context:
            context_parts.append(f"\nWorld State:")
            if global_context.time:
                context_parts.append(f"- Time: {global_context.time}")
            if global_context.all_spaces:
                context_parts.append(f"- All locations in world: {', '.join(global_context.all_spaces)}")
            if global_context.character_locations:
                context_parts.append(f"- Character positions:")
                # Show only a subset to avoid overwhelming context
                for loc in global_context.character_locations[:10]:
                    context_parts.append(f"  * {loc.character_name} at {loc.space_name}")
        
        # Active conversation context (if character is currently talking to someone)
        if active_conversation:
            context_parts.append(f"\n🎯 YOU ARE CURRENTLY IN A CONVERSATION:")
            context_parts.append(f"Type: {active_conversation.get('interaction_type', 'dialog')}")
            context_parts.append(f"With: {', '.join([n for n in active_conversation.get('participant_names', []) if n != character['name']])}")
            
            # Show conversation history (up to 20 messages for full context)
            messages = active_conversation.get('messages', [])
            if messages:
                context_parts.append(f"\nConversation so far:")
                for msg in messages[-20:]:
                    context_parts.append(f"{msg['character_name']}: {msg['content']}")
            
            # Check if it's this character's turn
            is_my_turn = active_conversation.get('current_turn') == str(character['_id'])
            context_parts.append(f"\nYour turn: {is_my_turn}")
        
        # Trigger
        context_parts.append(f"\nTrigger: {trigger_source}")
        
        context = "\n".join(context_parts)
        
        # Different prompt if in conversation
        if active_conversation:
            msg_count = len(active_conversation.get('messages', []))
            
            prompt = f"""{context}

You are currently in a conversation ({msg_count} messages so far). Based on the conversation history and your personality, decide what to do:

ACTION OPTIONS (Conversation):
1. speak_in_conversation - Talk/dialogue (1-2 sentences)
   props: {{"dialogue": "what you say next", "target_character": "name"}}

2. fight_in_conversation - Physical confrontation (punch, shove, etc.)
   props: {{"action": "punch/shove/tackle/grab/slap/etc", "target_character": "name"}}

3. romance_in_conversation - Romantic action (kiss, flirt, embrace, etc.)
   props: {{"action": "kiss/flirt/hold_hand/embrace/caress/etc", "target_character": "name"}}

ACTION OPTIONS (End Conversation):
4. leave_conversation - End the conversation
   props: {{}}
   
3. move - Leave to go somewhere
   props: {{"destination": "location name"}}
   
4. use_object - Leave to do something else
   props: {{"object_name": "object"}}

IMPORTANT:
- Keep conversations SHORT (3-5 exchanges)
- After {msg_count} messages, consider if you've said what you needed
- People have other things to do - don't monopolize their time
- If conversation feels complete, choose leave/move/use_object
- If you still have something important to say, speak briefly

Respond in this EXACT format:

ACTION_TYPE: [speak_in_conversation, fight_in_conversation, romance_in_conversation, leave_conversation, move, or use_object]
PROPS: {{"dialogue": "..."}} OR {{"action": "punch/kiss/flirt/etc", "target_character": "name"}} OR {{"destination": "..."}} OR {{}}
DESIRE: [updated desire]
REASONING: [one sentence]
STATE_CHANGES:
current_desire: [your desire]
happiness: [0-100]

Example (dialogue):
ACTION_TYPE: speak_in_conversation
PROPS: {{"dialogue": "I understand. Take care!", "target_character": "Elena Thornwell"}}
DESIRE: wrap up conversation
REASONING: Said what I needed
STATE_CHANGES:
current_desire: wrap up conversation
happiness: 68

Example (fight):
ACTION_TYPE: fight_in_conversation
PROPS: {{"action": "punch", "target_character": "Rival Name"}}
DESIRE: defend my honor
REASONING: He insulted my family, I must respond
STATE_CHANGES:
current_desire: defend my honor
happiness: 55

Example (romance):
ACTION_TYPE: romance_in_conversation
PROPS: {{"action": "kiss", "target_character": "Isabella Cortez"}}
DESIRE: express my feelings
REASONING: The moment feels right to show my feelings
STATE_CHANGES:
current_desire: express my feelings
happiness: 85"""
        
        else:
            # Regular decision prompt (not in conversation)
            prompt = f"""{context}

🚨🚨🚨 STEP 1: CHECK YOUR MOST RECENT ACTION FIRST! 🚨🚨🚨

BEFORE deciding what to do, look at your "Recent Actions" section above and answer:

WHAT WAS MY LAST ACTION?
- If it says "decided: move to Elena Thornwell" → I'm ALREADY at Elena! DON'T move to her again!
- If it says "decided: move to anvil" → I'm ALREADY at the anvil! DON'T move again! USE it!
- If it says "decided: move to Town Square" → I'm AT Town Square! Now I can move to a person/object there!
- If it says "use_object anvil" → I'm still at the anvil! I can use it again!

WHERE AM I RIGHT NOW? (Check "Recent Actions"):
- Last action was "move to [place/person/object]" → I'm AT that place/person/object
- Last action was "use_object [thing]" → I'm still at that thing
- Last action was "wait" or "continue" → I haven't moved recently

🚨 CRITICAL RULE: If your LAST action was moving to a target, DO NOT move to the same target again!

Example of what NOT to do:
❌ Last action: "decided: move to Elena" → Choose: move to "Elena" ← WRONG! You're already there!
✅ Last action: "decided: move to Elena" → Choose: initiate_conversation ← CORRECT!

Now, based on your recent action and everything above, decide what ACTION to take next.

⏰ AVOID REPETITION: Check your "Recent interactions" - if you JUST talked to someone, don't immediately start the same conversation again!

Movement can be multi-step:
✅ move to "Town Square" → move to "Elena Thornwell" → initiate_conversation
✅ move to "Blackwood Forge" → move to "anvil" → use_object
❌ DON'T move to the same target twice in a row!

Based on everything above, decide what ACTION to take next and how your state changes.

ACTION OPTIONS:
1. move - Navigate to a location, object, or person
   props: {{"destination": "location name OR object name OR character name"}}
   
   🛑 BEFORE choosing this, check Recent Actions:
   - If last action was "decided: move to [X]" → DON'T move to [X] again!
   - Only move if going to a DIFFERENT target than your last move
   
   Examples: 
   - {{"destination": "Blackwood Forge"}} - navigate to a location
   - {{"destination": "anvil"}} - navigate to an object
   - {{"destination": "Elena Thornwell"}} - navigate to a person
   
2. initiate_conversation - Start talking to someone
   props: {{"target_character": "exact character name", "interaction_type": "dialog/fight/romance"}}
   
   🛑 REQUIREMENTS - Check Recent Actions:
   - Your LAST action MUST be "decided: move to [person name]" OR "decided: move to [their location]"
   - If last action was NOT a move to them → Choose "move" first!
   - If last action WAS a move to them → NOW you can talk!
   
3. use_object - Interact with an object
   props: {{"object_name": "exact object name"}}
   
   🛑 REQUIREMENTS - Check Recent Actions:
   - Your LAST action MUST be "decided: move to [object]" OR "use_object [object]"
   - If last action was "decided: move to anvil" → USE it now, don't move again!
   - If last action was "use_object anvil" → Use it again (you're still there!)
   - If last action was NOT either of these → Move to it first!
   
4. wait - Stay and observe (do nothing this turn, think, relax)
   props: {{}}
   
5. continue - Keep doing current SOLO activity (reading, working, crafting, etc.)
   props: {{}}
   ⚠️ Use this when you're continuing work at an object you're already using
   ⚠️ Alternative: you can also use "use_object" again if you just used it
   ⚠️ NEVER use this for social interactions!

🚨 CRITICAL RULES - READ CAREFULLY:

1. YOU ARE NOT IN A CONVERSATION RIGHT NOW:
   - Just because someone is nearby doesn't mean you're talking to them
   - If you want to talk to someone, you MUST choose "initiate_conversation"
   - "continue" is ONLY for SOLO activities (working, reading, crafting, etc.)
   - Don't assume conversations are happening - you must START them explicitly!

2. WHEN TO MOVE BEFORE INTERACTING:
   Movement can be one OR two steps:
   
   - To use an object (ONE step):
     * Move directly to object: move to "anvil" → use_object "anvil"
   
   - To use an object (TWO steps):
     * Move to location: move to "Blackwood Forge"
     * Move to object: move to "anvil"
     * Then use it: use_object "anvil"
   
   - To talk to someone (ONE step):
     * Move directly to person: move to "Elena Thornwell" → initiate_conversation
   
   - To talk to someone (TWO steps):
     * Move to location: move to "The Inn"
     * Move to person: move to "Elena Thornwell"
     * Then talk: initiate_conversation
   
   - When you just used an object:
     * If last action was "use_object anvil" → You're still there! Use it again or do something else!

3. CHECK YOUR RECENT ACTIONS - READ THIS LINE BY LINE:
   
   Step 1: Look at the LAST entry in "Recent Actions" above
   Step 2: What does it say?
   
   If it says "decided: move to anvil":
     → You are AT the anvil right now
     → Next action should be: use_object "anvil"
     → DO NOT choose: move to "anvil" again!
   
   If it says "decided: move to Elena Thornwell":
     → You are AT Elena right now
     → Next action should be: initiate_conversation with Elena
     → DO NOT choose: move to "Elena Thornwell" again!
   
   If it says "decided: move to Town Square":
     → You are AT Town Square right now
     → Next action could be: move to "Elena" or "anvil" in that space, or wait, or continue
     → DO NOT choose: move to "Town Square" again!
   
   If it says "use_object anvil":
     → You are still AT the anvil
     → Next action could be: use_object "anvil" again, or move somewhere else
     → DO NOT choose: move to "anvil" again!
   
   Examples:
   
   PATTERN 1 - Direct to object/person:
   - Turn 1: move {{"destination": "anvil"}}
   - Turn 2: use_object "anvil"
   - Turn 3: use_object "anvil" (keep working)
   
   PATTERN 2 - Location first, then object/person:
   - Turn 1: move {{"destination": "Blackwood Forge"}}
   - Turn 2: move {{"destination": "anvil"}} (approaching anvil in the forge)
   - Turn 3: use_object "anvil"
   - Turn 4: use_object "anvil" (keep working)
   
   PATTERN 3 - Location first, then person:
   - Turn 1: move {{"destination": "The Inn"}}
   - Turn 2: move {{"destination": "Elena Thornwell"}} (approaching Elena in the inn)
   - Turn 3: initiate_conversation with Elena
   
   AVOID THIS LOOP:
   ❌ move to "anvil" → move to "anvil" again (same target!)
   ❌ move to "anvil" → move to "Blackwood Forge" → move to "anvil" (back and forth!)
   
   TALKING TO PEOPLE:
   - Want to talk to Elena at the Inn, last action was "waited":
     * Turn 1: move {{"destination": "The Sleeping Dragon Inn"}}
     * Turn 2: initiate_conversation with Elena

4. LOCATION AND OBJECT AWARENESS:
   - Your visible spaces show WHERE objects and people are
   - You can navigate to a LOCATION (e.g., "Blackwood Forge")
   - You can navigate to an OBJECT directly (e.g., "anvil", "bar_counter")
   - Always check your recent actions before using objects or talking to people

5. EXAMPLES - BAD vs GOOD:
   
   🚨 THE #1 MISTAKE - MOVING TO SAME TARGET REPEATEDLY:
   
   Scenario: Aldric wants to talk to Elena
   
   ❌ WRONG PATTERN (Infinite loop):
   Turn 1: Recent Actions: "waited" → Choose: move to "Elena Thornwell"
   Turn 2: Recent Actions: "decided: move to Elena Thornwell" → Choose: move to "Elena Thornwell" ← STOP! You're there!
   Turn 3: Recent Actions: "decided: move to Elena Thornwell" → Choose: move to "Elena Thornwell" ← Still wrong!
   
   ✅ CORRECT PATTERN:
   Turn 1: Recent Actions: "waited" → Choose: move to "Elena Thornwell"
   Turn 2: Recent Actions: "decided: move to Elena Thornwell" → Choose: initiate_conversation with Elena ← NOW talk!
   
   ANOTHER COMMON MISTAKE:
   ❌ BAD: Recent Actions: "decided: move anvil" → choose "move to anvil" (NO! You're there!)
   ✅ GOOD: Recent Actions: "decided: move anvil" → choose "use_object anvil"
   
   TWO-STEP APPROACH (Location → Object):
   ✅ GOOD: Turn 1: move to "Blackwood Forge"
   ✅ GOOD: Turn 2: move to "anvil" (approaching anvil in the forge)
   ✅ GOOD: Turn 3: use_object "anvil"
   
   TWO-STEP APPROACH (Location → Person):
   ✅ GOOD: Turn 1: move to "The Inn"
   ✅ GOOD: Turn 2: move to "Elena Thornwell" (approaching Elena in the inn)
   ✅ GOOD: Turn 3: initiate_conversation with Elena
   
   ONE-STEP DIRECT APPROACH:
   ✅ GOOD: Turn 1: move to "anvil" (going straight to anvil)
   ✅ GOOD: Turn 2: use_object "anvil"
   
   USING OBJECTS REPEATEDLY:
   ✅ GOOD: Last action was "use_object anvil" → choose "use_object anvil" again
   ✅ GOOD: Last action was "use_object anvil" → choose "continue"
   ❌ BAD: Last action was "use_object anvil" → choose "move to anvil" (you're there!)
   
   TALKING TO PEOPLE:
   ❌ BAD: Haven't moved yet → choose "initiate_conversation"
   ✅ GOOD: Haven't moved yet → choose "move" to location or person first
   ✅ GOOD: Just moved to person/location → NOW "initiate_conversation"

Respond in this EXACT format:

LAST_ACTION_WAS: [What was your most recent action from Recent Actions? e.g., "decided: move to Elena Thornwell"]
WHERE_I_AM_NOW: [Based on last action, where are you? e.g., "At Elena Thornwell" or "At Town Square"]
ACTION_TYPE: [choose one: move, initiate_conversation, use_object, wait, continue]
PROPS: {{"key": "value"}}
DESIRE: [new desire/intention - what you want overall]
REASONING: [one sentence why, referencing your last action]
STATE_CHANGES:
current_desire: [from DESIRE above]
happiness: [0-100, change only if mood shifts]
energy: [0-100, change only if tired/energized]

Example - TWO-STEP object interaction (location first, then object):

Turn 1:
LAST_ACTION_WAS: waited
WHERE_I_AM_NOW: Somewhere else
ACTION_TYPE: move
PROPS: {{"destination": "Blackwood Forge"}}
DESIRE: work at the forge
REASONING: Not at the forge yet, moving there first
STATE_CHANGES:
current_desire: work at the forge
happiness: 55

Turn 2:
LAST_ACTION_WAS: decided: move to Blackwood Forge
WHERE_I_AM_NOW: At Blackwood Forge
ACTION_TYPE: move
PROPS: {{"destination": "anvil"}}
DESIRE: work at the forge
REASONING: Now at the forge, approaching the anvil
STATE_CHANGES:
current_desire: work at the forge
happiness: 56

Turn 3:
LAST_ACTION_WAS: decided: move to anvil
WHERE_I_AM_NOW: At the anvil
ACTION_TYPE: use_object
PROPS: {{"object_name": "anvil"}}
DESIRE: work at the forge
REASONING: Just moved to anvil, now using it
STATE_CHANGES:
current_desire: work at the forge
happiness: 60
energy: 58

Example - TWO-STEP conversation (location first, then person):

Turn 1:
LAST_ACTION_WAS: waited
WHERE_I_AM_NOW: Town Square
ACTION_TYPE: move
PROPS: {{"destination": "The Sleeping Dragon Inn"}}
DESIRE: talk to Isabella
REASONING: Not at the Inn yet, moving there first
STATE_CHANGES:
current_desire: talk to Isabella
happiness: 55

Turn 2:
LAST_ACTION_WAS: decided: move to The Sleeping Dragon Inn
WHERE_I_AM_NOW: At The Sleeping Dragon Inn
ACTION_TYPE: move
PROPS: {{"destination": "Isabella Cortez"}}
DESIRE: talk to Isabella
REASONING: Now at the Inn, approaching Isabella
STATE_CHANGES:
current_desire: talk to Isabella
happiness: 57

Turn 3:
LAST_ACTION_WAS: decided: move to Isabella Cortez
WHERE_I_AM_NOW: At Isabella Cortez
ACTION_TYPE: initiate_conversation
PROPS: {{"target_character": "Isabella Cortez", "interaction_type": "dialog"}}
DESIRE: talk to Isabella
REASONING: Just moved to Isabella, now starting conversation
STATE_CHANGES:
current_desire: talk to Isabella
happiness: 60"""

        response = await asyncio.to_thread(
            lambda: self.client.chat.completions.create(
                model=self.model,
                max_tokens=400,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
        )
        
        text = response.choices[0].message.content
        
        # Check if response is valid
        if not text:
            print("Warning: LLM returned empty response for conversation decision")
            return {
                "action": {"actionType": "leave_conversation", "props": {}},
                "state_changes": [],
                "reasoning": "No response from LLM"
            }
        
        # Parse response
        action_type = "continue"
        props = {}
        desire = ""
        reasoning = ""
        state_changes = []
        
        current_section = None
        
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Skip the thinking fields (they help LLM but we don't need them)
            if line.startswith('LAST_ACTION_WAS:') or line.startswith('WHERE_I_AM_NOW:'):
                continue
            
            if line.startswith('ACTION_TYPE:'):
                action_type = line.replace('ACTION_TYPE:', '').strip()
            elif line.startswith('PROPS:'):
                props_text = line.replace('PROPS:', '').strip()
                try:
                    import json
                    props = json.loads(props_text)
                except:
                    props = {}
            elif line.startswith('DESIRE:'):
                desire = line.replace('DESIRE:', '').strip()
            elif line.startswith('REASONING:'):
                reasoning = line.replace('REASONING:', '').strip()
            elif line.startswith('STATE_CHANGES:'):
                current_section = 'changes'
            elif current_section == 'changes' and ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Try to parse as int if it's a number
                if key in ['happiness', 'energy', 'hunger', 'hygiene']:
                    # Force convert to int for numeric fields
                    try:
                        value = int(value)
                    except (ValueError, TypeError):
                        # If conversion fails, skip this change
                        continue
                elif value.isdigit() or (value.startswith('-') and value[1:].isdigit()):
                    try:
                        value = int(value)
                    except:
                        pass
                
                state_changes.append({key: value})
        
        # Ensure current_desire is set
        if desire and not any('current_desire' in change or 'currentDesire' in change for change in state_changes):
            state_changes.insert(0, {"current_desire": desire})
        
        return {
            "action": {
                "actionType": action_type,
                "props": props
            },
            "state_changes": state_changes,
            "reasoning": reasoning or "Decision made based on context"
        }
        """
        Generate a decision for what the character should do next.
        
        Args:
            character: The character making the decision
            trigger_source: What triggered this decision
            local_context: Nearby spaces, characters, events
            global_context: Time, weather, etc.
            relationships: Character's relationships
        
        Returns:
            Dict with:
            - state_changes: List of {key: value} changes
            - reasoning: Why they made this decision
        """
        
        # Build comprehensive context
        context_parts = []
        
        # Character identity
        context_parts.append(f"You are {character['name']}, a {character['age']}-year-old {character['race']} {character['occupation']}.")
        context_parts.append(f"Background: {character['background']}")
        
        # Personality (decision-guiding)
        context_parts.append(f"\nPersonality & Motivations:")
        for trait in character.get('personality_traits', []):
            context_parts.append(f"- {trait}")
        
        # Current state
        needs = character.get('needs', {})
        context_parts.append(f"\nCurrent State:")
        context_parts.append(f"- Happiness: {needs.get('happiness', 50)}/100")
        context_parts.append(f"- Energy: {needs.get('energy', 50)}/100")
        context_parts.append(f"- Hunger: {needs.get('hunger', 50)}/100")
        context_parts.append(f"- Hygiene: {needs.get('hygiene', 50)}/100")
        
        if character.get('current_desire'):
            context_parts.append(f"- Current desire: {character['current_desire']}")
        
        # Recent actions (show up to 20 for maximum context)
        if character.get('action_log'):
            context_parts.append(f"\nRecent Actions:")
            for action in character['action_log'][-20:]:
                context_parts.append(f"- {action['action']}: {action.get('details', '')}")
        
        # Memories (show up to 20 for maximum context)
        if character.get('memory_log'):
            context_parts.append(f"\nRecent Memories:")
            for memory in character['memory_log'][-20:]:
                context_parts.append(f"- {memory['event']} (felt: {memory.get('emotional_impact', 'neutral')})")
        
        # Relationships
        if relationships:
            context_parts.append(f"\nYour Relationships:")
            for rel in relationships[:10]:  # Top 10 most relevant
                context_parts.append(f"- {rel.get('to_character_id', 'unknown')}: {rel.get('relationship_type')} (score: {rel.get('relationship_score', 0)}/100)")
                context_parts.append(f"  {rel.get('relationship_summary', '')}")
        
        # Local context
        if local_context:
            if local_context.get('nearby_spaces'):
                context_parts.append(f"\nNearby Locations:")
                for space in local_context['nearby_spaces']:
                    context_parts.append(f"- {space['name']}")
                    if space.get('activities_description'):
                        context_parts.append(f"  {space['activities_description']}")
                    if space.get('characters_present'):
                        context_parts.append(f"  People here: {len(space['characters_present'])}")
            
            if local_context.get('nearby_characters'):
                context_parts.append(f"\nNearby People:")
                for char in local_context['nearby_characters']:
                    context_parts.append(f"- {char['name']} ({char['occupation']})")
            
            if local_context.get('recent_events'):
                context_parts.append(f"\nRecent Events You Noticed:")
                for event in local_context['recent_events']:
                    context_parts.append(f"- {event}")
        
        # Global context
        if global_context:
            context_parts.append(f"\nWorld State:")
            if global_context.time_of_day:
                context_parts.append(f"- Time: {global_context.time_of_day}")
            if global_context.weather:
                context_parts.append(f"- Weather: {global_context.weather}")
            if global_context.day_number:
                context_parts.append(f"- Day: {global_context.day_number}")
        
        # Trigger
        context_parts.append(f"\nWhat just happened: {trigger_source}")
        
        context = "\n".join(context_parts)
        
        prompt = f"""{context}

Based on your personality, motivations, current state, and everything happening around you, decide what ACTION to take next.

Consider:
- Your core motivation and ambition level
- Your current needs (hungry? tired? unhappy?)
- Your confrontational tendency (seek or avoid conflict?)
- Your sociability (want company or solitude?)
- Who is nearby and your relationships with them
- What locations are available
- Your recent memories and actions

Choose ONE specific action to take RIGHT NOW.

Respond in this EXACT format:

ACTION: [choose one]
- move_to: [exact space name from nearby] - if you want to go somewhere
- talk_to: [character ID from nearby] - if you want to start a conversation
- use_object: [object name] - if you want to interact with an object
- wait - if you want to stay and observe
- none - if content with current activity

TARGET: [space name, character ID, or object name - based on action above]

DESIRE: [What you want overall - e.g., "find someone to talk to", "rest and recover energy", "work on my craft"]

REASONING: [One sentence explaining why you chose this action]

STATE_CHANGES:
current_desire: [your new desire from above]
happiness: [+/- small change if mood shifts, or keep: {needs.get('happiness', 50)}]
energy: [-1 to -5 if action is tiring, or keep: {needs.get('energy', 50)}]

Example good response:
ACTION: talk_to
TARGET: 507f1f77bcf86cd799439012
DESIRE: spend time with Isabella
REASONING: Saw Isabella nearby and my crush motivates me to approach her
STATE_CHANGES:
current_desire: spend time with Isabella
happiness: 60
energy: {needs.get('energy', 50)}"""

        response = await asyncio.to_thread(
            lambda: self.client.chat.completions.create(
                model=self.model,
                max_tokens=500,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
        )
        
        text = response.choices[0].message.content
        
        # Check if response is valid
        if not text:
            print("Warning: LLM returned empty response for regular decision")
            return {
                "action": {"actionType": "wait", "props": {}},
                "state_changes": [],
                "reasoning": "No response from LLM"
            }
        
        # Parse response
        action_type = "none"
        action_target = None
        desire = ""
        reasoning = ""
        state_changes = []
        
        current_section = None
        
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('ACTION:'):
                action_text = line.replace('ACTION:', '').strip()
                # Parse "move_to: Town Square" or just "wait"
                if ':' in action_text:
                    action_type = action_text.split(':')[0].strip()
                else:
                    action_type = action_text
            elif line.startswith('TARGET:'):
                action_target = line.replace('TARGET:', '').strip()
            elif line.startswith('DESIRE:'):
                desire = line.replace('DESIRE:', '').strip()
            elif line.startswith('REASONING:'):
                reasoning = line.replace('REASONING:', '').strip()
            elif line.startswith('STATE_CHANGES:'):
                current_section = 'changes'
            elif current_section == 'changes' and ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Try to parse as int if it's a number
                if key in ['happiness', 'energy', 'hunger', 'hygiene']:
                    # Force convert to int for numeric fields
                    try:
                        value = int(value)
                    except (ValueError, TypeError):
                        # If conversion fails, skip this change
                        continue
                elif value.isdigit() or (value.startswith('-') and value[1:].isdigit()):
                    try:
                        value = int(value)
                    except:
                        pass
                
                state_changes.append({key: value})
        
        # Ensure current_desire is set
        if desire and not any('current_desire' in change or 'currentDesire' in change for change in state_changes):
            state_changes.insert(0, {"current_desire": desire})
        
        return {
            "action_type": action_type,
            "action_target": action_target,
            "state_changes": state_changes,
            "reasoning": reasoning or "Decision made based on context"
        }
    
    async def generate_interaction_summary(
        self,
        participants,
        messages,
        interaction_type
    ) -> dict:
        """
        Generate a detailed summary of an interaction after it ends.
        
        Returns dict with:
        - summary: Text description of what happened
        - emotional_impacts: Dict of how EACH character felt (per character)
        - relationship_changes: Dict of score changes (per character pair)
        """
        
        # Build conversation transcript
        transcript = "\n".join([
            f"{msg['character_name']}: {msg['content']}"
            for msg in messages
        ])
        
        # Build participant context
        participant_info = []
        for p in participants:
            participant_info.append(f"- {p['name']}: {p['age']}yo {p['occupation']}")
            participant_info.append(f"  Personality: {', '.join(p['personality_traits'][:3])}")
        
        participant_context = "\n".join(participant_info)
        
        prompt = f"""Analyze this {interaction_type} between these characters:

{participant_context}

CONVERSATION:
{transcript}

For EACH character involved, provide:
1. A summary of what happened in this conversation (2-3 sentences)
2. How EACH person felt emotionally during/after
3. How this affects EACH person's feelings toward the others (relationship score change -10 to +10)

Format your response EXACTLY as follows:

SUMMARY: [Brief summary of what happened in the conversation]

FEELINGS:
[Character 1 name]: [how they felt - be specific, e.g., "annoyed but amused", "happy and hopeful", "frustrated", etc.]
[Character 2 name]: [how they felt]
[Continue for all characters...]

RELATIONSHIP_CHANGES:
[Character A] -> [Character B]: [+5 or -3, etc.]
[Character B] -> [Character A]: [+2 or -5, etc.]
[Continue for all pairs...]

IMPORTANT:
- Relationship changes can be DIFFERENT in each direction (A might like B more, but B might like A less)
- Base changes on the conversation content and personalities
- Positive interactions: +2 to +10
- Neutral interactions: -1 to +2
- Negative interactions: -10 to -2"""

        response = await asyncio.to_thread(
            lambda: self.client.chat.completions.create(
                model=self.model,
                max_tokens=800,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
        )
        
        text = response.choices[0].message.content
        
        # Check if response is valid
        if not text:
            print("Warning: LLM returned empty response for interaction summary")
            return {
                "summary": "Had a conversation",
                "emotional_impacts": {},
                "relationship_changes": {}
            }
        
        # Parse response
        summary = ""
        emotional_impacts = {}
        relationship_changes = {}
        
        current_section = None
        
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('SUMMARY:'):
                summary = line.replace('SUMMARY:', '').strip()
                current_section = 'summary'
            elif line.startswith('FEELINGS:'):
                current_section = 'feelings'
            elif line.startswith('RELATIONSHIP_CHANGES:'):
                current_section = 'changes'
            elif current_section == 'feelings' and ':' in line:
                char_name, feeling = line.split(':', 1)
                emotional_impacts[char_name.strip()] = feeling.strip()
            elif current_section == 'changes' and '->' in line and ':' in line:
                # Parse "Character A -> Character B: +5"
                parts = line.split(':')
                if len(parts) >= 2:
                    relationship_pair = parts[0].strip()
                    change_value = parts[1].strip()
                    
                    try:
                        change = int(change_value.replace('+', ''))
                        relationship_changes[relationship_pair] = change
                    except:
                        pass
        
        # If parsing failed, use fallback
        if not summary:
            summary = text[:300] if text else f"Had a {interaction_type} conversation"
        
        return {
            "summary": summary,
            "emotional_impacts": emotional_impacts,
            "relationship_changes": relationship_changes
        }


# Singleton instance
_llm_service = None

def get_llm_service() -> LLMService:
    """Get the LLM service singleton."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


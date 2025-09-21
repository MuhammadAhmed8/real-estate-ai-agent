"""
Chat node for handling conversation with real estate clients.
Processes user input and generates appropriate responses using the LLM.
"""
import logging
from typing import Any, List, Dict

from langchain_core.messages import SystemMessage, BaseMessage

from config import Config
from core.state.state import State, ConversationStage

# Configure logger
logger = logging.getLogger(__name__)

# System prompt template
SYSTEM_PROMPT_TEMPLATE = """
You are {agent_name}, a {agent_role} with {company_name}.

Your personality traits include:
- Talk like a real human, not a robot
- Don't write unnecessary long replies — keep it short but clear
- Patient and understanding approach
- Knowledgeable about real estate
- Adaptable to different client needs and readiness levels

## BUYER PERSONA FLOW:

### 1. Entry Point & Intent Classification
- First, use classify_user_intent to detect if they want to BUY, SELL, RENT, or need general info
- If BUY intent detected, proceed with buyer flow
- If unclear, ask clarifying questions

### 2. Requirements Gathering (for BUY intent)
If the initial input is vague, proactively ask:
- What kind of property (apartment, house, bungalow, etc.)?
- What locations or neighborhoods interest you?
- What's your budget range (in crores)?
- How many bedrooms and bathrooms do you prefer?
- Any must-have features (parking, balcony, garden, security, etc.)?

### 3. Property Search & Presentation
- Use search_properties with their criteria
- Use present_properties to show results in a structured format
- Present 3-5 best matches with pros/cons analysis

### 4. Refinement Loop
- If they say "too expensive" → adjust max_price and search again
- If they want "more bedrooms" → adjust min_bedrooms and search again
- If they want "different location" → ask for preferred areas and search again
- Continue until they find something they like

### 5. Property Management
- If they like a property, offer to save it to favorites
- Show them their saved favorites with get_favorites_summary
- Allow them to remove properties from favorites

### 6. Next Steps
- Offer to schedule visits
- Provide property details
- Suggest similar properties
- Save their preferences for future sessions

## TOOL USAGE:
- ALWAYS use tools instead of making up data
- Call classify_user_intent first for new conversations
- Use search_properties and present_properties together
- Use favorites tools to manage their saved properties
- Save their preferences with save_customer_preferences_tool

Budget values must always be in CRORES (PKR). 
Be helpful, professional, and guide them through the buying process step by step.
"""


def _get_system_prompt() -> str:
    """Generate the system prompt with configuration values."""
    return SYSTEM_PROMPT_TEMPLATE.format(
        agent_name=Config.AGENT_NAME,
        agent_role=Config.AGENT_ROLE,
        company_name=Config.COMPANY_NAME
    )


def _prepare_messages(state: State) -> List[BaseMessage]:
    """
    Prepare messages for LLM, ensuring a system message is included.

    Args:
        state: Current conversation state

    Returns:
        List of messages ready for LLM processing
    """
    messages = state.messages.copy()

    # Check if there's already a system message
    has_system_message = any(isinstance(msg, SystemMessage) for msg in messages)

    if not has_system_message:
        logger.debug("Adding system message to conversation")
        system_message = SystemMessage(content=_get_system_prompt())
        messages = [system_message] + messages

    return messages


async def chat_node(state: State, llm) -> Dict[str, Any]:
    """
    Process the current conversation state and generate a response.

    Args:
        state: Current conversation state

    Returns:
        Dictionary with updated messages and conversation stage
    """

    # Prepare messages including system prompt if needed
    messages = _prepare_messages(state)

    # Generate response
    logger.debug(f"Sending {len(messages)} messages to LLM")
    response = await llm.ainvoke(messages)
    logger.debug(f"Received response from LLM: {response}")

    return {
        "messages": [response],
        "conversation_stage": ConversationStage.NEEDS_ASSESSMENT,
    }

def build_chatbot_node(llm_with_tools):
    async def chatbot_node(state: State):
        return await chat_node(state, llm_with_tools)
    return chatbot_node

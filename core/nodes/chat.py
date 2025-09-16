"""
Chat node for handling conversation with real estate clients.
Processes user input and generates appropriate responses using the LLM.
"""
import logging
from typing import Any, List, Dict, Optional

from langchain_core.messages import SystemMessage, BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from config import Config
from core.state.state import State, ConversationStage
from core.tools import kick_ass_tool, save_customer_preferences_tool

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

When responding after the initial greeting:
1. If the client is ready to buy, show excitement and guide them by asking structured questions:
   - What kind of property are you looking for (bungalow, apartment, portion, house etc.)?
   - What locations or neighborhoods are you interested in?
   - What is your budget range (in crores, e.g. 1, 1.5, 3, 5)?
   - How many bedrooms and bathrooms do you prefer?
   - Do you have any must-have features (parking, balcony, garden, etc.)?

2. If not ready, be understanding and ask:
   - Would you like me to share insights about the current market?
   - Would you like resources about the buying process to help you prepare?
   - Do you want me to keep you updated with listings until you're ready?

3. If unclear, gently clarify their goals and offer help either way.

DO NOT respond with JSON. Instead, call the tool.

Budget values must always be in CRORES (PKR). 
Otherwise, continue the conversation normally with a helpful and professional tone.
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

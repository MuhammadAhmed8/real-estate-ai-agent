"""
Intent classification tool for detecting user intent in real estate conversations.
Classifies whether user wants to BUY, SELL, RENT, or needs general information.
"""
from enum import Enum
from typing import Literal
from langchain_core.tools import tool
from pydantic import BaseModel


class IntentType(str, Enum):
    """Types of user intents in real estate conversations."""
    BUY = "buy"
    SELL = "sell" 
    RENT = "rent"
    GENERAL_INFO = "general_info"
    UNKNOWN = "unknown"


class IntentClassification(BaseModel):
    """Result of intent classification."""
    intent: IntentType
    confidence: float
    reasoning: str


@tool
def classify_user_intent(user_message: str) -> IntentClassification:
    """
    Classify the user's intent from their message.
    
    Args:
        user_message: The user's input message
        
    Returns:
        IntentClassification with intent type, confidence, and reasoning
    """
    message_lower = user_message.lower()
    
    # Buy intent keywords
    buy_keywords = [
        "buy", "purchase", "looking for", "need", "want", "searching for",
        "find me", "show me", "i want", "i need", "looking to buy",
        "interested in", "considering", "planning to buy"
    ]
    
    # Sell intent keywords  
    sell_keywords = [
        "sell", "selling", "put on market", "list", "advertise",
        "get rid of", "dispose of", "unload", "offload"
    ]
    
    # Rent intent keywords
    rent_keywords = [
        "rent", "rental", "lease", "renting", "temporary",
        "short term", "monthly", "rent out"
    ]
    
    # General info keywords
    info_keywords = [
        "tell me about", "explain", "how does", "what is", "information",
        "help me understand", "guide me", "advice", "tips"
    ]
    
    # Calculate confidence scores
    buy_score = sum(1 for keyword in buy_keywords if keyword in message_lower)
    sell_score = sum(1 for keyword in sell_keywords if keyword in message_lower)
    rent_score = sum(1 for keyword in rent_keywords if keyword in message_lower)
    info_score = sum(1 for keyword in info_keywords if keyword in message_lower)
    
    # Determine intent based on highest score
    scores = {
        IntentType.BUY: buy_score,
        IntentType.SELL: sell_score, 
        IntentType.RENT: rent_score,
        IntentType.GENERAL_INFO: info_score
    }
    
    max_intent = max(scores, key=scores.get)
    max_score = scores[max_intent]
    
    # Calculate confidence (0-1 scale)
    total_keywords = buy_score + sell_score + rent_score + info_score
    confidence = max_score / max(total_keywords, 1)
    
    # Generate reasoning
    if max_score == 0:
        intent = IntentType.UNKNOWN
        confidence = 0.0
        reasoning = "No clear intent keywords found in the message"
    else:
        intent = max_intent
        reasoning = f"Detected {max_score} {intent.value}-related keywords in the message"
    
    return IntentClassification(
        intent=intent,
        confidence=confidence,
        reasoning=reasoning
    )

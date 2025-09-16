from enum import Enum


class ConversationStage(str, Enum):
    """Stages of the real estate conversation flow."""
    GREETING = "greeting"
    NEEDS_ASSESSMENT = "needs_assessment"
    PROPERTY_SEARCH = "property_search"
    PROPERTY_PRESENTATION = "property_presentation"
    FOLLOW_UP = "follow_up"
    SCHEDULING = "scheduling"
    CLOSING = "closing"

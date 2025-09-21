from enum import Enum


class ConversationStage(str, Enum):
    """Stages of the real estate conversation flow."""
    GREETING = "greeting"
    INTENT_CLASSIFICATION = "intent_classification"
    NEEDS_ASSESSMENT = "needs_assessment"
    REQUIREMENTS_GATHERING = "requirements_gathering"
    PROPERTY_SEARCH = "property_search"
    PROPERTY_PRESENTATION = "property_presentation"
    REFINEMENT = "refinement"
    PROPERTY_DETAILS = "property_details"
    FAVORITES_MANAGEMENT = "favorites_management"
    FOLLOW_UP = "follow_up"
    SCHEDULING = "scheduling"
    CLOSING = "closing"

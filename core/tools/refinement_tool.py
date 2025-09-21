"""
Refinement tool for adjusting search criteria based on user feedback.
"""
from typing import Optional, List, Dict, Any
from langchain_core.tools import tool
from pydantic import BaseModel

from .property_search_tool import PropertySearchCriteria


class RefinementRequest(BaseModel):
    """Request for refining search criteria."""
    current_criteria: PropertySearchCriteria
    user_feedback: str
    adjustment_type: str  # price, bedrooms, location, features, etc.


class RefinementResult(BaseModel):
    """Result of search criteria refinement."""
    updated_criteria: PropertySearchCriteria
    changes_made: List[str]
    reasoning: str


@tool
def refine_search_criteria(
    current_criteria: PropertySearchCriteria,
    user_feedback: str
) -> RefinementResult:
    """
    Refine search criteria based on user feedback.
    
    Args:
        current_criteria: Current search criteria
        user_feedback: User's feedback (e.g., "too expensive", "need more bedrooms")
        
    Returns:
        RefinementResult with updated criteria and explanation of changes
    """
    feedback_lower = user_feedback.lower()
    changes_made = []
    updated_criteria = current_criteria.model_copy()
    
    # Price adjustments
    if any(phrase in feedback_lower for phrase in ["too expensive", "price too high", "over budget", "reduce price"]):
        if updated_criteria.max_price:
            # Reduce max price by 20%
            updated_criteria.max_price = updated_criteria.max_price * 0.8
            changes_made.append(f"Reduced max price to {updated_criteria.max_price:.1f} crores")
        else:
            # Set a reasonable max price if none was set
            updated_criteria.max_price = 2.0
            changes_made.append("Set max price to 2.0 crores")
    
    elif any(phrase in feedback_lower for phrase in ["increase budget", "higher price", "more expensive"]):
        if updated_criteria.max_price:
            updated_criteria.max_price = updated_criteria.max_price * 1.5
            changes_made.append(f"Increased max price to {updated_criteria.max_price:.1f} crores")
        else:
            updated_criteria.max_price = 5.0
            changes_made.append("Set max price to 5.0 crores")
    
    # Bedroom adjustments
    if any(phrase in feedback_lower for phrase in ["more bedrooms", "need more rooms", "bigger house"]):
        if updated_criteria.min_bedrooms:
            updated_criteria.min_bedrooms = max(updated_criteria.min_bedrooms + 1, 3)
            changes_made.append(f"Increased min bedrooms to {updated_criteria.min_bedrooms}")
        else:
            updated_criteria.min_bedrooms = 3
            changes_made.append("Set min bedrooms to 3")
    
    elif any(phrase in feedback_lower for phrase in ["fewer bedrooms", "smaller house", "less rooms"]):
        if updated_criteria.min_bedrooms:
            updated_criteria.min_bedrooms = max(updated_criteria.min_bedrooms - 1, 1)
            changes_made.append(f"Reduced min bedrooms to {updated_criteria.min_bedrooms}")
        else:
            updated_criteria.min_bedrooms = 1
            changes_made.append("Set min bedrooms to 1")
    
    # Location adjustments
    if any(phrase in feedback_lower for phrase in ["different location", "other area", "change location"]):
        # Ask for specific location preferences
        changes_made.append("Please specify which areas you'd prefer")
    
    # Feature adjustments
    if any(phrase in feedback_lower for phrase in ["need parking", "must have parking"]):
        if not updated_criteria.must_have_features:
            updated_criteria.must_have_features = []
        if "parking" not in updated_criteria.must_have_features:
            updated_criteria.must_have_features.append("parking")
            changes_made.append("Added parking as must-have feature")
    
    if any(phrase in feedback_lower for phrase in ["need balcony", "must have balcony"]):
        if not updated_criteria.must_have_features:
            updated_criteria.must_have_features = []
        if "balcony" not in updated_criteria.must_have_features:
            updated_criteria.must_have_features.append("balcony")
            changes_made.append("Added balcony as must-have feature")
    
    if any(phrase in feedback_lower for phrase in ["need garden", "must have garden"]):
        if not updated_criteria.must_have_features:
            updated_criteria.must_have_features = []
        if "garden" not in updated_criteria.must_have_features:
            updated_criteria.must_have_features.append("garden")
            changes_made.append("Added garden as must-have feature")
    
    # Property type adjustments
    if any(phrase in feedback_lower for phrase in ["apartment", "flat"]):
        updated_criteria.property_type = "apartment"
        changes_made.append("Set property type to apartment")
    
    elif any(phrase in feedback_lower for phrase in ["house", "bungalow", "villa"]):
        updated_criteria.property_type = "house"
        changes_made.append("Set property type to house")
    
    # Generate reasoning
    if changes_made:
        reasoning = f"Based on your feedback '{user_feedback}', I've made these adjustments: {', '.join(changes_made)}. Let me search for properties with these updated criteria."
    else:
        reasoning = f"I understand your feedback '{user_feedback}', but I need more specific information to adjust the search. Could you tell me what specific changes you'd like to make?"
    
    return RefinementResult(
        updated_criteria=updated_criteria,
        changes_made=changes_made,
        reasoning=reasoning
    )

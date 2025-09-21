"""
Property presentation tool for displaying search results in a structured format.
"""
from typing import List, Dict, Any
from langchain_core.tools import tool
from pydantic import BaseModel

from .property_search_tool import Property, PropertySearchResult


class PropertySummary(BaseModel):
    """Summary of a property for presentation."""
    id: str
    title: str
    price_crores: float
    location: str
    bedrooms: int
    bathrooms: int
    size_sqft: int
    key_features: List[str]
    price_per_sqft: float
    pros: List[str]
    cons: List[str]


class PropertyPresentationResult(BaseModel):
    """Result of property presentation formatting."""
    summaries: List[PropertySummary]
    total_properties: int
    presentation_text: str


def _calculate_price_per_sqft(price_crores: float, size_sqft: int) -> float:
    """Calculate price per square foot."""
    if size_sqft == 0:
        return 0.0
    return (price_crores * 10000000) / size_sqft  # Convert crores to rupees


def _generate_property_pros_cons(property: Property) -> tuple[List[str], List[str]]:
    """Generate pros and cons for a property based on its features."""
    pros = []
    cons = []
    
    # Analyze features for pros/cons
    if property.features.parking:
        pros.append("✅ Parking available")
    else:
        cons.append("❌ No parking")
    
    if property.features.balcony:
        pros.append("✅ Balcony included")
    
    if property.features.garden:
        pros.append("✅ Private garden")
    
    if property.features.security:
        pros.append("✅ Security system")
    
    if property.features.gym:
        pros.append("✅ Gym facility")
    
    if property.features.pool:
        pros.append("✅ Swimming pool")
    
    if property.features.elevator:
        pros.append("✅ Elevator access")
    
    # Price analysis
    price_per_sqft = _calculate_price_per_sqft(property.price_crores, property.features.size_sqft)
    if price_per_sqft < 8000:  # Less than 8000 per sqft is considered good value
        pros.append("✅ Good value for money")
    elif price_per_sqft > 15000:  # More than 15000 per sqft is expensive
        cons.append("⚠️ Higher price per sqft")
    
    # Size analysis
    if property.features.size_sqft > 2000:
        pros.append("✅ Spacious living area")
    elif property.features.size_sqft < 1000:
        cons.append("⚠️ Compact living space")
    
    # Location analysis (basic)
    if "DHA" in property.location.area:
        pros.append("✅ Prime DHA location")
    elif "Phase" in property.location.area:
        pros.append("✅ Well-planned area")
    
    # Maintenance fee analysis
    if property.maintenance_fee and property.maintenance_fee < 10000:
        pros.append("✅ Low maintenance fees")
    elif property.maintenance_fee and property.maintenance_fee > 20000:
        cons.append("⚠️ High maintenance fees")
    
    return pros, cons


def _format_property_summary(property: Property) -> PropertySummary:
    """Format a property into a summary for presentation."""
    # Calculate price per sqft
    price_per_sqft = _calculate_price_per_sqft(property.price_crores, property.features.size_sqft)
    
    # Generate pros and cons
    pros, cons = _generate_property_pros_cons(property)
    
    # Extract key features
    key_features = []
    if property.features.parking:
        key_features.append("Parking")
    if property.features.balcony:
        key_features.append("Balcony")
    if property.features.garden:
        key_features.append("Garden")
    if property.features.security:
        key_features.append("Security")
    if property.features.gym:
        key_features.append("Gym")
    if property.features.pool:
        key_features.append("Pool")
    if property.features.elevator:
        key_features.append("Elevator")
    
    return PropertySummary(
        id=property.id,
        title=property.title,
        price_crores=property.price_crores,
        location=f"{property.location.area}, {property.location.city}",
        bedrooms=property.features.bedrooms,
        bathrooms=property.features.bathrooms,
        size_sqft=property.features.size_sqft,
        key_features=key_features,
        price_per_sqft=price_per_sqft,
        pros=pros,
        cons=cons
    )


def _generate_presentation_text(summaries: List[PropertySummary]) -> str:
    """Generate formatted text presentation of properties."""
    if not summaries:
        return "No properties found matching your criteria. Let me help you refine your search!"
    
    text = f"🏡 **Found {len(summaries)} properties matching your criteria:**\n\n"
    
    for i, summary in enumerate(summaries, 1):
        text += f"**{i}. {summary.title}**\n"
        text += f"💰 **Price:** {summary.price_crores:.1f} crores ({summary.price_per_sqft:,.0f} PKR/sqft)\n"
        text += f"📍 **Location:** {summary.location}\n"
        text += f"🏠 **Details:** {summary.bedrooms} bed, {summary.bathrooms} bath, {summary.size_sqft:,} sqft\n"
        text += f"✨ **Features:** {', '.join(summary.key_features) if summary.key_features else 'Basic amenities'}\n"
        
        if summary.pros:
            text += f"**Pros:**\n"
            for pro in summary.pros:
                text += f"  {pro}\n"
        
        if summary.cons:
            text += f"**Considerations:**\n"
            for con in summary.cons:
                text += f"  {con}\n"
        
        text += "\n" + "─" * 50 + "\n\n"
    
    text += "💡 **Next Steps:**\n"
    text += "• Say 'show me more details about property 1' for specific info\n"
    text += "• Say 'too expensive' to adjust your budget\n"
    text += "• Say 'I want more bedrooms' to refine your search\n"
    text += "• Say 'save property 1' to add to your favorites\n"
    
    return text


@tool
def present_properties(search_result: PropertySearchResult) -> PropertyPresentationResult:
    """
    Present property search results in a structured, user-friendly format.
    
    Args:
        search_result: Result from property search
        
    Returns:
        PropertyPresentationResult with formatted summaries and presentation text
    """
    # Convert properties to summaries
    summaries = [_format_property_summary(prop) for prop in search_result.properties]
    
    # Generate presentation text
    presentation_text = _generate_presentation_text(summaries)
    
    return PropertyPresentationResult(
        summaries=summaries,
        total_properties=len(summaries),
        presentation_text=presentation_text
    )

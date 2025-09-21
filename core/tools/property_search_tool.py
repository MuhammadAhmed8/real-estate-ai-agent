"""
Property search tool for finding real estate listings based on user criteria.
"""
import json
import os
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict
from langchain_core.tools import tool
from pydantic import BaseModel

from config import Config


@dataclass
class PropertyLocation:
    """Property location information."""
    city: str
    area: str
    address: str
    coordinates: Optional[Dict[str, float]] = None


@dataclass
class PropertyFeatures:
    """Property features and amenities."""
    bedrooms: int
    bathrooms: int
    size_sqft: int
    parking: bool
    balcony: bool
    garden: bool
    security: bool
    gym: bool = False
    pool: bool = False
    elevator: bool = False


@dataclass
class Property:
    """Complete property information."""
    id: str
    title: str
    description: str
    price_crores: float
    property_type: str  # apartment, house, bungalow, etc.
    location: PropertyLocation
    features: PropertyFeatures
    images: List[str]
    year_built: Optional[int] = None
    maintenance_fee: Optional[float] = None
    available: bool = True


class PropertySearchCriteria(BaseModel):
    """Search criteria for property search."""
    property_type: Optional[str] = None
    locations: Optional[List[str]] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_bedrooms: Optional[int] = None
    max_bedrooms: Optional[int] = None
    min_bathrooms: Optional[int] = None
    must_have_features: Optional[List[str]] = None
    max_results: int = 10


class PropertySearchResult(BaseModel):
    """Result of property search."""
    properties: List[Property]
    total_found: int
    search_criteria: PropertySearchCriteria


def _load_sample_properties() -> List[Property]:
    """Load sample property data for testing."""
    sample_properties = [
        Property(
            id="prop_001",
            title="Luxury 3-Bed Apartment in DHA Phase 5",
            description="Beautiful modern apartment with premium finishes, located in the heart of DHA Phase 5. Close to schools, shopping centers, and main roads.",
            price_crores=2.5,
            property_type="apartment",
            location=PropertyLocation(
                city="Lahore",
                area="DHA Phase 5",
                address="Block A, DHA Phase 5, Lahore"
            ),
            features=PropertyFeatures(
                bedrooms=3,
                bathrooms=3,
                size_sqft=1800,
                parking=True,
                balcony=True,
                garden=False,
                security=True,
                gym=True,
                elevator=True
            ),
            images=["https://example.com/prop1_1.jpg", "https://example.com/prop1_2.jpg"],
            year_built=2020,
            maintenance_fee=15000
        ),
        Property(
            id="prop_002", 
            title="Spacious 4-Bed House in Gulshan Iqbal",
            description="Well-maintained house with large garden, perfect for families. Located near Karachi University and major shopping areas.",
            price_crores=1.8,
            property_type="house",
            location=PropertyLocation(
                city="Karachi",
                area="Gulshan Iqbal",
                address="Block 6, Gulshan Iqbal, Karachi"
            ),
            features=PropertyFeatures(
                bedrooms=4,
                bathrooms=3,
                size_sqft=2200,
                parking=True,
                balcony=True,
                garden=True,
                security=True
            ),
            images=["https://example.com/prop2_1.jpg", "https://example.com/prop2_2.jpg"],
            year_built=2018,
            maintenance_fee=8000
        ),
        Property(
            id="prop_003",
            title="Modern 2-Bed Apartment in F-8 Islamabad",
            description="Contemporary apartment with city views, ideal for young professionals. Close to business district and restaurants.",
            price_crores=3.2,
            property_type="apartment", 
            location=PropertyLocation(
                city="Islamabad",
                area="F-8",
                address="F-8/3, Islamabad"
            ),
            features=PropertyFeatures(
                bedrooms=2,
                bathrooms=2,
                size_sqft=1200,
                parking=True,
                balcony=True,
                garden=False,
                security=True,
                gym=True,
                pool=True,
                elevator=True
            ),
            images=["https://example.com/prop3_1.jpg", "https://example.com/prop3_2.jpg"],
            year_built=2022,
            maintenance_fee=20000
        ),
        Property(
            id="prop_004",
            title="Cozy 1-Bed Apartment in Clifton Karachi",
            description="Charming apartment near the beach, perfect for singles or couples. Walking distance to restaurants and cafes.",
            price_crores=1.2,
            property_type="apartment",
            location=PropertyLocation(
                city="Karachi", 
                area="Clifton",
                address="Block 2, Clifton, Karachi"
            ),
            features=PropertyFeatures(
                bedrooms=1,
                bathrooms=1,
                size_sqft=800,
                parking=False,
                balcony=True,
                garden=False,
                security=True
            ),
            images=["https://example.com/prop4_1.jpg"],
            year_built=2019,
            maintenance_fee=12000
        ),
        Property(
            id="prop_005",
            title="Family Bungalow in DHA Phase 2",
            description="Large family bungalow with private garden and servant quarters. Perfect for extended families.",
            price_crores=4.5,
            property_type="bungalow",
            location=PropertyLocation(
                city="Lahore",
                area="DHA Phase 2", 
                address="Block B, DHA Phase 2, Lahore"
            ),
            features=PropertyFeatures(
                bedrooms=5,
                bathrooms=4,
                size_sqft=3500,
                parking=True,
                balcony=True,
                garden=True,
                security=True
            ),
            images=["https://example.com/prop5_1.jpg", "https://example.com/prop5_2.jpg"],
            year_built=2015,
            maintenance_fee=25000
        )
    ]
    return sample_properties


def _filter_properties(properties: List[Property], criteria: PropertySearchCriteria) -> List[Property]:
    """Filter properties based on search criteria."""
    filtered = properties.copy()
    
    # Filter by property type
    if criteria.property_type:
        filtered = [p for p in filtered if criteria.property_type.lower() in p.property_type.lower()]
    
    # Filter by locations
    if criteria.locations:
        location_matches = []
        for prop in filtered:
            for location in criteria.locations:
                if (location.lower() in prop.location.city.lower() or 
                    location.lower() in prop.location.area.lower()):
                    location_matches.append(prop)
                    break
        filtered = location_matches
    
    # Filter by price range
    if criteria.min_price is not None:
        filtered = [p for p in filtered if p.price_crores >= criteria.min_price]
    if criteria.max_price is not None:
        filtered = [p for p in filtered if p.price_crores <= criteria.max_price]
    
    # Filter by bedrooms
    if criteria.min_bedrooms is not None:
        filtered = [p for p in filtered if p.features.bedrooms >= criteria.min_bedrooms]
    if criteria.max_bedrooms is not None:
        filtered = [p for p in filtered if p.features.bedrooms <= criteria.max_bedrooms]
    
    # Filter by bathrooms
    if criteria.min_bathrooms is not None:
        filtered = [p for p in filtered if p.features.bathrooms >= criteria.min_bathrooms]
    
    # Filter by must-have features
    if criteria.must_have_features:
        feature_matches = []
        for prop in filtered:
            has_all_features = True
            for feature in criteria.must_have_features:
                feature_lower = feature.lower()
                if (feature_lower == "parking" and not prop.features.parking) or \
                   (feature_lower == "balcony" and not prop.features.balcony) or \
                   (feature_lower == "garden" and not prop.features.garden) or \
                   (feature_lower == "security" and not prop.features.security) or \
                   (feature_lower == "gym" and not prop.features.gym) or \
                   (feature_lower == "pool" and not prop.features.pool) or \
                   (feature_lower == "elevator" and not prop.features.elevator):
                    has_all_features = False
                    break
            if has_all_features:
                feature_matches.append(prop)
        filtered = feature_matches
    
    # Filter available properties only
    filtered = [p for p in filtered if p.available]
    
    # Limit results
    return filtered[:criteria.max_results]


@tool
def search_properties(criteria: PropertySearchCriteria) -> PropertySearchResult:
    """
    Search for properties based on specified criteria.
    
    Args:
        criteria: Search criteria including property type, location, price range, etc.
        
    Returns:
        PropertySearchResult with matching properties and metadata
    """
    
    print("Using Search tool")
    print(criteria)
    # Load sample properties (in real implementation, this would query a database)
    all_properties = _load_sample_properties()
    
    # Filter properties based on criteria
    matching_properties = _filter_properties(all_properties, criteria)
    
    return PropertySearchResult(
        properties=matching_properties,
        total_found=len(matching_properties),
        search_criteria=criteria
    )

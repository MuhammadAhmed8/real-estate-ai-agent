"""
Favorites system for saving and managing preferred properties.
"""
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from pymongo import MongoClient
from langchain_core.tools import tool
from pydantic import BaseModel

from .property_search_tool import Property


class FavoriteProperty(BaseModel):
    """A property saved to favorites."""
    property_id: str
    user_id: str
    saved_at: datetime
    notes: Optional[str] = None
    priority: str = "medium"  # low, medium, high


class FavoritesResult(BaseModel):
    """Result of favorites operation."""
    status: str
    message: str
    favorites: Optional[List[FavoriteProperty]] = None


def _get_mongo_collection():
    """Get MongoDB collection for storing favorites."""
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    client = MongoClient(mongo_uri)
    db = client["real_estate"]
    return db["favorites"]


@tool
def save_to_favorites(property_id: str, user_id: str = "1", notes: str = None, priority: str = "medium") -> FavoritesResult:
    """
    Save a property to user's favorites list.
    
    Args:
        property_id: ID of the property to save
        user_id: ID of the user (default: 1 for demo)
        notes: Optional notes about why this property is liked
        priority: Priority level (low, medium, high)
        
    Returns:
        FavoritesResult with operation status and message
    """

    print("calling save to favourites tool")
    try:
        collection = _get_mongo_collection()
        
        # Check if already saved
        existing = collection.find_one({
            "property_id": property_id,
            "user_id": user_id
        })
        
        if existing:
            return FavoritesResult(
                status="warning",
                message=f"Property {property_id} is already in your favorites!"
            )
        
        # Save to favorites
        favorite = FavoriteProperty(
            property_id=property_id,
            user_id=user_id,
            saved_at=datetime.now(),
            notes=notes,
            priority=priority
        )
        
        collection.insert_one(favorite.dict())
        
        return FavoritesResult(
            status="success",
            message=f"Property {property_id} saved to your favorites! 🏡"
        )
        
    except Exception as e:
        return FavoritesResult(
            status="error",
            message=f"Failed to save property: {str(e)}"
        )


@tool
def get_favorites(user_id: str = "1") -> FavoritesResult:
    """
    Get user's saved favorite properties.
    
    Args:
        user_id: ID of the user (default: 1 for demo)
        
    Returns:
        FavoritesResult with list of favorite properties
    """
    try:
        collection = _get_mongo_collection()
        
        # Get all favorites for user
        favorites_cursor = collection.find({"user_id": user_id}).sort("saved_at", -1)
        favorites = [FavoriteProperty(**fav) for fav in favorites_cursor]
        
        return FavoritesResult(
            status="success",
            message=f"Found {len(favorites)} favorite properties",
            favorites=favorites
        )
        
    except Exception as e:
        return FavoritesResult(
            status="error",
            message=f"Failed to get favorites: {str(e)}"
        )


@tool
def remove_from_favorites(property_id: str, user_id: str = "1") -> FavoritesResult:
    """
    Remove a property from user's favorites list.
    
    Args:
        property_id: ID of the property to remove
        user_id: ID of the user (default: 1 for demo)
        
    Returns:
        FavoritesResult with operation status and message
    """
    try:
        collection = _get_mongo_collection()
        
        # Remove from favorites
        result = collection.delete_one({
            "property_id": property_id,
            "user_id": user_id
        })
        
        if result.deleted_count > 0:
            return FavoritesResult(
                status="success",
                message=f"Property {property_id} removed from favorites"
            )
        else:
            return FavoritesResult(
                status="warning",
                message=f"Property {property_id} was not in your favorites"
            )
            
    except Exception as e:
        return FavoritesResult(
            status="error",
            message=f"Failed to remove property: {str(e)}"
        )


@tool
def get_favorites_summary(user_id: str = "1") -> str:
    """
    Get a summary of user's favorite properties.
    
    Args:
        user_id: ID of the user (default: 1 for demo)
        
    Returns:
        Formatted string summary of favorites
    """
    try:
        favorites_result = get_favorites(user_id)
        
        if favorites_result.status != "success" or not favorites_result.favorites:
            return "You haven't saved any properties to favorites yet. Start exploring and save the ones you like! 🏡"
        
        favorites = favorites_result.favorites
        
        summary = f"📋 **Your Favorite Properties ({len(favorites)}):**\n\n"
        
        for i, fav in enumerate(favorites, 1):
            summary += f"**{i}. Property ID: {fav.property_id}**\n"
            summary += f"   💾 Saved: {fav.saved_at.strftime('%Y-%m-%d %H:%M')}\n"
            summary += f"   ⭐ Priority: {fav.priority.title()}\n"
            if fav.notes:
                summary += f"   📝 Notes: {fav.notes}\n"
            summary += "\n"
        
        summary += "💡 **Next Steps:**\n"
        summary += "• Say 'show me property [ID]' to see details\n"
        summary += "• Say 'remove property [ID]' to remove from favorites\n"
        summary += "• Say 'search similar to [ID]' to find similar properties\n"
        
        return summary
        
    except Exception as e:
        return f"Failed to get favorites summary: {str(e)}"

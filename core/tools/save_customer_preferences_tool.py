import os
from dataclasses import asdict, dataclass
from typing import Optional
from pymongo import MongoClient
from langchain_core.tools import tool


@dataclass
class Budget:
    min: float
    max: float


@dataclass
class UserPreferences:
    property_type: str
    locations: list[str]
    budget: Budget
    bedrooms: Optional[str] = None
    bathrooms: Optional[str] = None
    must_have_features: Optional[list[str]] = None


def _get_mongo_collection():
    """Get MongoDB collection for storing preferences."""
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    client = MongoClient(mongo_uri)
    db = client["real_estate"]
    return db["customer_preferences"]


@tool
def save_customer_preferences_tool(user_preference: UserPreferences) -> dict:
    """Save a customer's property buying preferences into MongoDB."""

    print(f"Calling tool with {user_preference}")

    # Convert dataclass -> dict (including nested Budget)
    pref_dict = asdict(user_preference)

    try:
        collection = _get_mongo_collection()
        # Example: fixed customer_id=1, replace with session/user ID later
        customer_id = 1

        collection.update_one(
            {"customer_id": customer_id},
            {"$set": {"preferences": pref_dict}},
            upsert=True,
        )

        return {"status": "success", "message": f"Preferences saved for customer {customer_id}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}

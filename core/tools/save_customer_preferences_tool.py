import json
from pathlib import Path

from langchain_core.tools import tool
from dataclasses import dataclass

@dataclass
class Budget:
    min: float
    max: float

@dataclass
class UserPreferences:
    property_type: str
    locations: list[str]
    budget: Budget
    bedrooms: str | None = None
    bathrooms: str | None = None
    must_have_features: list[str] | None = None

@tool
def save_customer_preferences_tool(user_preference: UserPreferences) -> dict:
    """Save a customer's property buying preferences into customers.json."""

    print(f"Calling tool with {user_preference}")
    # customer_id=1
    # file_path = "customers.json"
    # if Path(file_path).exists():
    #     with open(file_path, "r", encoding="utf-8") as f:
    #         all_customers = json.load(f)
    # else:
    #     all_customers = {}
    #
    # all_customers[customer_id] = {
    #     "property_type": property_type,
    #     "locations": locations,
    #     "budget": budget,
    #     "bedrooms": bedrooms,
    #     "bathrooms": bathrooms,
    #     "must_have_features": must_have_features or []
    # }
    #
    # with open(file_path, "w", encoding="utf-8") as f:
    #     json.dump(all_customers, f, indent=4, ensure_ascii=False)

    return {"status": "success", "message": f"Preferences saved for customer 1"}


"""
MyHome Real Estate Assistant Configuration

This module handles application configuration, environment variables loading,
and validation for the MyHome Real Estate Assistant application.
"""
import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Application configuration with environment variables and validation.

    Provides central access to all configuration parameters needed by the application,
    including API keys, model settings, and agent personality configuration.
    """

    # API and model settings
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Agent personality configuration
    AGENT_NAME: str = "Sarah"
    AGENT_ROLE: str = "Senior Real Estate Agent"
    COMPANY_NAME: str = "Premier Realty Group"

    # Application paths
    DATA_DIR: Path = Path("data")
    CUSTOMER_DATA_FILE: Path = Path("customers.json")

    # LLM settings
    LLM_PROVIDER = "google"  # or "openai"
    LLM_TEMPERATURE: float = 0.7

    @classmethod
    def validate(cls) -> bool:
        """
        Validate that all required configuration values are properly set.

        Raises:
            ValueError: If any required configuration is missing

        Returns:
            bool: True if all validations pass
        """
        # Validate API keys
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is not set in environment variables.")

        # Ensure data directories exist
        cls.DATA_DIR.mkdir(exist_ok=True)

        logger.info("Configuration validated successfully")
        return True


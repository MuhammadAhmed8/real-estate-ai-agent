from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from config import Config


class LLMFactory:
    @staticmethod
    def create(provider: str = None):
        """Create an LLM instance based on provider in config or arg."""
        provider = provider or Config.LLM_PROVIDER.lower()

        if provider == "google":
            return ChatGoogleGenerativeAI(
                model=Config.GEMINI_MODEL,
                api_key=Config.GOOGLE_API_KEY,
            )
        elif provider == "openai":
            return ChatOpenAI(
                model=Config.OPENAI_MODEL,
                api_key=Config.OPENAI_API_KEY,
                temperature=0.7,
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

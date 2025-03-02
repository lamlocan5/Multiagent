"""LLM provider implementations for different models."""

from typing import Optional, Union
from langchain.schema.runnable import Runnable

from src.config.settings import settings
from src.llm.providers.openai import get_openai_provider
from src.llm.providers.deepseek import get_deepseek_provider
from src.llm.providers.gemini import get_gemini_provider

def get_llm_provider(provider_name: Optional[str] = None) -> Runnable:
    """
    Factory function to get a language model provider.
    
    Args:
        provider_name: The name of the provider to use. If None, will use the default.
        
    Returns:
        A configured LLM instance
    """
    if provider_name is None:
        # Use the default provider based on available API keys
        if settings.OPENAI_API_KEY:
            provider_name = "openai"
        elif settings.DEEPSEEK_API_KEY:
            provider_name = "deepseek"
        elif settings.GEMINI_API_KEY:
            provider_name = "gemini"
        else:
            raise ValueError("No API keys available for any LLM provider")
    
    # Return the specified provider
    if provider_name.lower() == "openai":
        provider = get_openai_provider()
        return provider.get_chat_model()
    elif provider_name.lower() == "deepseek":
        provider = get_deepseek_provider()
        return provider.get_chat_model()
    elif provider_name.lower() == "gemini":
        provider = get_gemini_provider()
        return provider.get_chat_model()
    else:
        raise ValueError(f"Unsupported provider: {provider_name}") 
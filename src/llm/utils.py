"""Utility functions for LLM module."""

from typing import Optional

class LLMProviderException(Exception):
    """Exception raised for LLM provider issues."""
    pass

def validate_api_key(api_key: Optional[str], provider_name: str) -> None:
    """
    Validate that an API key is available.
    
    Args:
        api_key: The API key to validate
        provider_name: Name of the provider for error messages
    
    Raises:
        LLMProviderException: If the API key is not available
    """
    if not api_key:
        raise LLMProviderException(f"No API key available for {provider_name}")

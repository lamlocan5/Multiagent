from typing import Dict, Any, List, Optional
from langchain.schema.runnable import Runnable
from langchain.llms import GooglePalm
from langchain_google_genai import ChatGoogleGenerativeAI

from src.config.settings import settings
from src.llm.utils import validate_api_key

class GeminiProvider:
    """
    Provider for Google's Gemini models.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini provider.
        
        Args:
            api_key: Gemini API key. If None, will use the key from settings.
        """
        self.api_key = api_key or settings.GEMINI_API_KEY
        validate_api_key(self.api_key, "Gemini")
    
    def get_chat_model(
        self, 
        model_name: str = "gemini-pro",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        streaming: bool = False
    ) -> Runnable:
        """
        Get a ChatGoogleGenerativeAI instance configured with the specified parameters.
        
        Args:
            model_name: Name of the Gemini model to use
            temperature: Temperature parameter for generation
            max_tokens: Maximum tokens to generate
            streaming: Whether to enable streaming
            
        Returns:
            Configured ChatGoogleGenerativeAI instance
        """
        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            max_output_tokens=max_tokens,
            google_api_key=self.api_key,
            streaming=streaming
        )

def get_gemini_provider() -> GeminiProvider:
    """Factory function to create a Gemini provider."""
    return GeminiProvider() 
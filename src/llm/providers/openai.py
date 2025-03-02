from typing import Dict, Any, List, Optional, Union
from langchain.llms import OpenAI as LangChainOpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema.runnable import Runnable

from src.config.settings import settings
from src.llm.utils import validate_api_key

class OpenAIProvider:
    """
    Provider for OpenAI's language models.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenAI provider.
        
        Args:
            api_key: OpenAI API key. If None, will use the key from settings.
        """
        self.api_key = api_key or settings.OPENAI_API_KEY
        validate_api_key(self.api_key, "OpenAI")
    
    def get_chat_model(
        self, 
        model_name: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        streaming: bool = False
    ) -> ChatOpenAI:
        """
        Get a ChatOpenAI instance configured with the specified parameters.
        
        Args:
            model_name: Name of the OpenAI model to use
            temperature: Temperature parameter for generation
            max_tokens: Maximum tokens to generate
            streaming: Whether to enable streaming
            
        Returns:
            Configured ChatOpenAI instance
        """
        return ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=streaming,
            openai_api_key=self.api_key
        )
    
    def get_completion_model(
        self,
        model_name: str = "gpt-3.5-turbo-instruct",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> LangChainOpenAI:
        """
        Get an OpenAI completion model instance.
        
        Args:
            model_name: Name of the OpenAI model to use
            temperature: Temperature parameter for generation
            max_tokens: Maximum tokens to generate
            
        Returns:
            Configured OpenAI instance
        """
        return LangChainOpenAI(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            openai_api_key=self.api_key
        )

def get_openai_provider() -> OpenAIProvider:
    """Factory function to create an OpenAI provider."""
    return OpenAIProvider() 
from typing import Dict, Any, List, Optional
from langchain.schema.runnable import Runnable
from langchain.chat_models import ChatDeepSeek

from src.config.settings import settings
from src.llm.utils import validate_api_key

class DeepSeekProvider:
    """
    Provider for DeepSeek's language models.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the DeepSeek provider.
        
        Args:
            api_key: DeepSeek API key. If None, will use the key from settings.
        """
        self.api_key = api_key or settings.DEEPSEEK_API_KEY
        validate_api_key(self.api_key, "DeepSeek")
    
    def get_chat_model(
        self, 
        model_name: str = "deepseek-chat",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        streaming: bool = False
    ) -> Runnable:
        """
        Get a ChatDeepSeek instance configured with the specified parameters.
        
        Args:
            model_name: Name of the DeepSeek model to use
            temperature: Temperature parameter for generation
            max_tokens: Maximum tokens to generate
            streaming: Whether to enable streaming
            
        Returns:
            Configured ChatDeepSeek instance
        """
        return ChatDeepSeek(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=streaming,
            deepseek_api_key=self.api_key
        )

def get_deepseek_provider() -> DeepSeekProvider:
    """Factory function to create a DeepSeek provider."""
    return DeepSeekProvider() 
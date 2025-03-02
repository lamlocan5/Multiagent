"""Configuration settings for the multiagent system."""

import os
from typing import Dict, Any, Optional, List
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings, loaded from environment variables."""
    
    # API settings
    API_KEY: Optional[str] = Field(None, description="API key for authentication")
    API_HOST: str = Field("0.0.0.0", description="API host")
    API_PORT: int = Field(8000, description="API port")
    
    # LLM settings
    OPENAI_API_KEY: Optional[str] = Field(None, description="OpenAI API key")
    DEEPSEEK_API_KEY: Optional[str] = Field(None, description="DeepSeek API key")
    GEMINI_API_KEY: Optional[str] = Field(None, description="Google Gemini API key")
    DEFAULT_LLM_PROVIDER: str = Field("openai", description="Default LLM provider")
    
    # Vector database settings
    VECTOR_DB_TYPE: str = Field("chroma", description="Vector database type")
    VECTOR_DB_HOST: str = Field("localhost", description="Vector database host")
    VECTOR_DB_PORT: int = Field(8000, description="Vector database port")
    
    # RAG settings
    EMBEDDING_MODEL: str = Field("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", 
                                description="Embedding model to use")
    
    # Audio settings
    ELEVENLABS_API_KEY: Optional[str] = Field(None, description="ElevenLabs API key")
    GOOGLE_API_KEY: Optional[str] = Field(None, description="Google API key for Speech & TTS") 
    
    # Web search settings
    SERPAPI_API_KEY: Optional[str] = Field(None, description="SerpAPI key for web search")
    
    # Storage settings
    UPLOAD_DIR: str = Field("./uploads", description="Directory for uploaded files")
    TEMP_DIR: str = Field("./tmp", description="Directory for temporary files")
    
    # Performance settings
    USE_GPU: bool = Field(False, description="Whether to use GPU acceleration")
    NUM_THREADS: int = Field(4, description="Number of threads for CPU operations")
    
    # Logging settings
    LOG_LEVEL: str = Field("INFO", description="Logging level")
    ENABLE_TRACING: bool = Field(False, description="Enable distributed tracing")
    
    # Vietnamese language settings
    VIETNAMESE_SUPPORT: bool = Field(True, description="Enable Vietnamese language support")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Create a singleton instance
settings = Settings()

from typing import Dict, Any, Optional
from langchain.embeddings.base import Embeddings

from src.config.settings import settings
from src.rag.embeddings.vietnamese import VietnameseOptimizedEmbeddings

def get_embeddings_model(model_name: Optional[str] = None) -> Embeddings:
    """
    Factory function to get an embeddings model based on configuration.
    
    Args:
        model_name: Optional override for the embeddings model
        
    Returns:
        Configured embeddings model
    """
    model_name = model_name or settings.EMBEDDING_MODEL
    
    # Special case for Vietnamese optimized embeddings
    if settings.VIETNAMESE_SUPPORT and model_name.startswith("vi-"):
        return VietnameseOptimizedEmbeddings(
            model_name=model_name.replace("vi-", ""),
            use_hybrid=True
        )
    
    # Otherwise, use standard HuggingFace embeddings
    from langchain.embeddings import HuggingFaceEmbeddings
    
    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": "cuda" if settings.USE_GPU else "cpu"}
    )

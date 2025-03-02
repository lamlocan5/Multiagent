from typing import Dict, Any, List, Optional, Union
from langchain.schema.vectorstore import VectorStore
from langchain.embeddings.base import Embeddings

from src.config.settings import settings
from src.utils.logging import get_logger

logger = get_logger(__name__)

def get_vector_store(
    embedding_model: Optional[Embeddings] = None,
    store_type: Optional[str] = None,
    collection_name: str = "documents",
    **kwargs
) -> VectorStore:
    """
    Factory function to get a vector store based on configuration.
    
    Args:
        embedding_model: Embeddings model to use
        store_type: Type of vector store (overrides settings)
        collection_name: Name of the collection/index
        **kwargs: Additional arguments for the vector store
        
    Returns:
        Configured vector store instance
    """
    from src.rag.embeddings import get_embeddings_model
    
    # Get embeddings model if not provided
    if embedding_model is None:
        embedding_model = get_embeddings_model()
        
    # Get store type from settings if not provided
    store_type = store_type or settings.VECTOR_DB_TYPE
    store_type = store_type.lower()
    
    # Initialize the appropriate vector store
    if store_type == "chroma":
        return _get_chroma_store(embedding_model, collection_name, **kwargs)
    elif store_type == "weaviate":
        return _get_weaviate_store(embedding_model, collection_name, **kwargs)
    elif store_type == "pinecone":
        return _get_pinecone_store(embedding_model, collection_name, **kwargs)
    elif store_type == "milvus":
        return _get_milvus_store(embedding_model, collection_name, **kwargs)
    else:
        logger.warning(f"Unsupported vector store type: {store_type}, falling back to Chroma")
        return _get_chroma_store(embedding_model, collection_name, **kwargs)

def _get_chroma_store(
    embedding_model: Embeddings,
    collection_name: str,
    persist_directory: Optional[str] = None,
    **kwargs
) -> VectorStore:
    """Initialize a Chroma vector store."""
    from langchain.vectorstores import Chroma
    
    persist_directory = persist_directory or f"./data/chroma/{collection_name}"
    
    logger.info(f"Initializing Chroma vector store at {persist_directory}")
    
    return Chroma(
        collection_name=collection_name,
        embedding_function=embedding_model,
        persist_directory=persist_directory,
        **kwargs
    )

def _get_weaviate_store(
    embedding_model: Embeddings,
    collection_name: str,
    **kwargs
) -> VectorStore:
    """Initialize a Weaviate vector store."""
    from langchain.vectorstores import Weaviate
    import weaviate
    
    logger.info(f"Initializing Weaviate vector store with collection {collection_name}")
    
    client = weaviate.Client(
        url=f"http://{settings.VECTOR_DB_HOST}:{settings.VECTOR_DB_PORT}"
    )
    
    return Weaviate(
        client=client,
        index_name=collection_name,
        text_key="content",
        embedding=embedding_model,
        **kwargs
    )

def _get_pinecone_store(
    embedding_model: Embeddings,
    collection_name: str,
    **kwargs
) -> VectorStore:
    """Initialize a Pinecone vector store."""
    from langchain.vectorstores import Pinecone
    import pinecone
    
    logger.info(f"Initializing Pinecone vector store with index {collection_name}")
    
    # Initialize Pinecone
    api_key = kwargs.pop("api_key", os.environ.get("PINECONE_API_KEY"))
    environment = kwargs.pop("environment", os.environ.get("PINECONE_ENVIRONMENT", "us-west1-gcp"))
    
    pinecone.init(api_key=api_key, environment=environment)
    
    # Create index if it doesn't exist
    if collection_name not in pinecone.list_indexes():
        pinecone.create_index(
            name=collection_name,
            dimension=384,  # Default for many embedding models
            metric="cosine"
        )
    
    index = pinecone.Index(collection_name)
    
    return Pinecone(
        index=index,
        embedding=embedding_model,
        text_key="content",
        **kwargs
    )

def _get_milvus_store(
    embedding_model: Embeddings,
    collection_name: str,
    **kwargs
) -> VectorStore:
    """Initialize a Milvus vector store."""
    from langchain.vectorstores import Milvus
    
    logger.info(f"Initializing Milvus vector store with collection {collection_name}")
    
    return Milvus(
        embedding_function=embedding_model,
        collection_name=collection_name,
        connection_args={"host": settings.VECTOR_DB_HOST, "port": settings.VECTOR_DB_PORT},
        **kwargs
    ) 
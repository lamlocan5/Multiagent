from typing import Optional, Any
from langchain.embeddings.base import Embeddings
from langchain.vectorstores import Chroma, Weaviate
from langchain.schema.vectorstore import VectorStore

from src.config.settings import settings
from src.rag.embeddings import get_embeddings_model

def get_vector_store(
    vector_db_type: str,
    host: str,
    port: int,
    embeddings: Optional[Embeddings] = None,
    collection_name: str = "documents"
) -> VectorStore:
    """
    Factory function to get a vector store instance based on configuration.
    
    Args:
        vector_db_type: Type of vector database ('chroma' or 'weaviate')
        host: Database host
        port: Database port
        embeddings: Embeddings model to use
        collection_name: Name of the collection/table
        
    Returns:
        Configured vector store instance
    """
    if embeddings is None:
        embeddings = get_embeddings_model()
    
    if vector_db_type.lower() == "chroma":
        return _get_chroma(host, port, embeddings, collection_name)
    elif vector_db_type.lower() == "weaviate":
        return _get_weaviate(host, port, embeddings, collection_name)
    else:
        raise ValueError(f"Unsupported vector database type: {vector_db_type}")

def _get_chroma(
    host: str,
    port: int,
    embeddings: Embeddings,
    collection_name: str
) -> Chroma:
    """Get a Chroma vector store instance."""
    from chromadb.config import Settings
    import chromadb
    
    # Create a client
    client = chromadb.HttpClient(
        host=host,
        port=port,
        settings=Settings(anonymized_telemetry=False)
    )
    
    # Create or get collection
    return Chroma(
        client=client,
        collection_name=collection_name,
        embedding_function=embeddings
    )

def _get_weaviate(
    host: str,
    port: int,
    embeddings: Embeddings,
    collection_name: str
) -> Weaviate:
    """Get a Weaviate vector store instance."""
    import weaviate
    from weaviate.auth import AuthApiKey
    
    # Create a client
    client = weaviate.Client(
        url=f"http://{host}:{port}"
    )
    
    # Define schema if it doesn't exist
    if not client.schema.exists(collection_name):
        class_obj = {
            "class": collection_name,
            "vectorizer": "none",  # We'll provide our own vectors
            "properties": [
                {
                    "name": "text",
                    "dataType": ["text"]
                },
                {
                    "name": "metadata",
                    "dataType": ["object"]
                }
            ]
        }
        client.schema.create_class(class_obj)
    
    return Weaviate(
        client=client,
        index_name=collection_name,
        text_key="text",
        embedding=embeddings,
        by_text=False  # Don't use Weaviate's built-in text indexing
    )

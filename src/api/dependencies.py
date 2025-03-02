from typing import Annotated, AsyncGenerator, Dict, Any
from fastapi import Depends, HTTPException, status
from langchain.vectorstores import Chroma, Weaviate
from langchain.schema.vectorstore import VectorStore

from src.config.settings import settings
from src.llm.providers import get_llm_provider
from src.rag.vectorstores import get_vector_store
from src.rag.embeddings import get_embeddings_model
from src.rag.retrieval.hybrid_search import HybridSearchRetriever
from src.agents.coordinator import AgentCoordinator
from src.agents.specialized import (
    get_research_agent,
    get_reasoning_agent,
    get_creative_agent
)

async def get_vectorstore() -> AsyncGenerator[VectorStore, None]:
    """Dependency for providing vector database access."""
    try:
        embeddings = get_embeddings_model()
        vector_store = get_vector_store(
            vector_db_type=settings.VECTOR_DB_TYPE,
            host=settings.VECTOR_DB_HOST,
            port=settings.VECTOR_DB_PORT,
            embeddings=embeddings
        )
        yield vector_store
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Vector database connection failed: {str(e)}"
        )

async def get_retriever(
    vectorstore: Annotated[VectorStore, Depends(get_vectorstore)]
) -> AsyncGenerator[HybridSearchRetriever, None]:
    """Dependency for providing RAG retrieval system."""
    try:
        retriever = HybridSearchRetriever(
            vector_store=vectorstore,
            bm25_weight=0.3,
            vector_weight=0.7
        )
        yield retriever
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to initialize retriever: {str(e)}"
        )

async def get_agent_coordinator() -> AsyncGenerator[AgentCoordinator, None]:
    """Dependency for providing the agent coordination system."""
    try:
        # Initialize specialized agents
        llm = get_llm_provider()
        vectorstore = await anext(get_vectorstore())
        retriever = HybridSearchRetriever(vector_store=vectorstore)
        
        # Create specialized agents
        research_agent = get_research_agent(llm=llm, retriever=retriever)
        reasoning_agent = get_reasoning_agent(llm=llm)
        creative_agent = get_creative_agent(llm=llm)
        
        # Initialize coordinator with all agents
        coordinator = AgentCoordinator(
            agents=[research_agent, reasoning_agent, creative_agent],
            default_agent=reasoning_agent
        )
        
        yield coordinator
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize agent coordinator: {str(e)}"
        )

async def validate_api_key(api_key: str) -> bool:
    """Validate API key for protected endpoints."""
    # In a real implementation, this would check against a database
    # For now, we'll use a simple check for demonstration
    return api_key == settings.API_KEY if hasattr(settings, 'API_KEY') else False

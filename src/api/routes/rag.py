from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel

from src.rag.retrieval.hybrid_search import HybridSearchRetriever
from src.api.dependencies import get_retriever

router = APIRouter()

class SearchQuery(BaseModel):
    """Query model for search requests."""
    query: str
    filters: Optional[Dict[str, Any]] = None
    top_k: Optional[int] = 5
    hybrid_alpha: Optional[float] = 0.7  # Weight for hybrid search (1.0 = all vector, 0.0 = all keyword)

class SearchResult(BaseModel):
    """Model for search results."""
    content: str
    metadata: Dict[str, Any]
    score: float

class SearchResponse(BaseModel):
    """Response model for search requests."""
    results: List[SearchResult]
    query: str
    total_results: int

@router.post("/search", response_model=SearchResponse)
async def search(
    query: SearchQuery,
    retriever: HybridSearchRetriever = Depends(get_retriever)
):
    """
    Search for documents using hybrid search (vector + keyword).
    
    Parameters:
    - query: Search query and parameters
    
    Returns:
    - Search results with content and metadata
    """
    try:
        # Configure retriever with hybrid_alpha if provided
        if query.hybrid_alpha is not None:
            retriever.vector_weight = query.hybrid_alpha
            retriever.bm25_weight = 1.0 - query.hybrid_alpha
        
        # Perform search
        results = await retriever.search(
            query=query.query,
            filters=query.filters,
            top_k=query.top_k
        )
        
        # Format response
        return SearchResponse(
            results=[
                SearchResult(
                    content=result["content"],
                    metadata=result["metadata"],
                    score=result["score"]
                ) for result in results
            ],
            query=query.query,
            total_results=len(results)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )

@router.get("/document/{document_id}")
async def get_document(
    document_id: str,
    retriever: HybridSearchRetriever = Depends(get_retriever)
):
    """
    Retrieve a specific document by ID.
    
    Parameters:
    - document_id: The ID of the document to retrieve
    
    Returns:
    - Document content and metadata
    """
    try:
        # Get the document by ID
        document = await retriever.get_document(document_id)
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found"
            )
        
        return document
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve document: {str(e)}"
        ) 
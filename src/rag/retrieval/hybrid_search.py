from typing import Dict, Any, List, Optional, Tuple, Union
import asyncio
from langchain.schema.vectorstore import VectorStore
from pydantic import BaseModel, Field
import numpy as np

from src.utils.logging import get_logger

logger = get_logger(__name__)

class HybridSearchRetriever:
    """
    Retriever that combines vector search with keyword search.
    
    This hybrid approach provides better results by combining the semantic understanding
    of vector search with the precision of traditional keyword (BM25) search.
    """
    
    def __init__(
        self,
        vector_store: VectorStore,
        vector_weight: float = 0.7,
        bm25_weight: float = 0.3,
        top_k: int = 5
    ):
        """
        Initialize the hybrid search retriever.
        
        Args:
            vector_store: The vector store for embeddings-based search
            vector_weight: Weight for vector search results (0.0 to 1.0)
            bm25_weight: Weight for BM25 keyword search results (0.0 to 1.0)
            top_k: Default number of results to return
        """
        self.vector_store = vector_store
        self.vector_weight = vector_weight
        self.bm25_weight = bm25_weight
        self.top_k = top_k
    
    async def search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search with both vector and keyword matching.
        
        Args:
            query: The search query
            filters: Optional metadata filters
            top_k: Number of results to return
            
        Returns:
            List of documents with scores and metadata
        """
        k = top_k or self.top_k
        
        # Get vector search results (semantic search)
        try:
            vector_results = await self._vector_search(query, k=k*2, filters=filters)
        except Exception as e:
            logger.error(f"Vector search failed: {str(e)}")
            vector_results = []
        
        # Get keyword search results (lexical search)
        try:
            keyword_results = await self._keyword_search(query, k=k*2, filters=filters)
        except Exception as e:
            logger.error(f"Keyword search failed: {str(e)}")
            keyword_results = []
        
        # Combine results with weighting
        combined_results = self._combine_results(vector_results, keyword_results)
        
        # Sort results by combined score
        combined_results.sort(key=lambda x: x["score"], reverse=True)
        
        # Return top-k results
        return combined_results[:k]
    
    async def _vector_search(
        self, 
        query: str, 
        k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform vector-based semantic search.
        
        Args:
            query: The search query
            k: Number of results to return
            filters: Optional metadata filters
            
        Returns:
            List of documents with scores
        """
        if hasattr(self.vector_store, "similarity_search_with_score"):
            results = await self.vector_store.asimilarity_search_with_score(
                query=query,
                k=k,
                filter=filters
            )
            return [
                {
                    "content": doc.page_content if hasattr(doc, "page_content") else doc.text,
                    "metadata": doc.metadata,
                    "score": score
                }
                for doc, score in results
            ]
        else:
            # Fallback for vector stores that don't support async
            results = self.vector_store.similarity_search_with_score(
                query=query,
                k=k,
                filter=filters
            )
            return [
                {
                    "content": doc.page_content if hasattr(doc, "page_content") else doc.text,
                    "metadata": doc.metadata,
                    "score": score
                }
                for doc, score in results
            ]
    
    async def _keyword_search(
        self, 
        query: str, 
        k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform keyword-based lexical search.
        
        Args:
            query: The search query
            k: Number of results to return
            filters: Optional metadata filters
            
        Returns:
            List of documents with scores
        """
        if hasattr(self.vector_store, "keyword_search"):
            # If vector store has built-in keyword search
            results = await self.vector_store.akeyword_search(
                query=query,
                k=k,
                filter=filters
            )
            return results
        else:
            # Use basic keyword matching (fallback)
            # This is very simplified; a real implementation would use BM25 or similar
            documents = self.vector_store.get()
            matched_docs = []
            
            # Split query into keywords
            keywords = query.lower().split()
            
            for doc in documents:
                content = doc.page_content.lower() if hasattr(doc, "page_content") else doc.text.lower()
                
                # Calculate a simple keyword match score
                score = sum(1 for keyword in keywords if keyword in content) / len(keywords)
                
                if score > 0:
                    matched_docs.append({
                        "content": doc.page_content if hasattr(doc, "page_content") else doc.text,
                        "metadata": doc.metadata,
                        "score": score
                    })
            
            # Sort by score and return top-k
            matched_docs.sort(key=lambda x: x["score"], reverse=True)
            return matched_docs[:k]
    
    def _combine_results(
        self, 
        vector_results: List[Dict[str, Any]], 
        keyword_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Combine and rerank results from vector and keyword search.
        
        Args:
            vector_results: Results from vector search
            keyword_results: Results from keyword search
            
        Returns:
            Combined and reranked results
        """
        # Create a dictionary to track combined results
        combined_dict = {}
        
        # Helper function to get a unique document ID
        def _get_document_id(doc):
            if "id" in doc.get("metadata", {}):
                return doc["metadata"]["id"]
            else:
                # Create a simple hash if no ID exists
                return hash(doc["content"][:100])
        
        # Process vector results
        for result in vector_results:
            doc_id = _get_document_id(result)
            combined_dict[doc_id] = {
                "content": result["content"],
                "metadata": result["metadata"],
                "vector_score": result["score"],
                "keyword_score": 0.0
            }
        
        # Process keyword results
        for result in keyword_results:
            doc_id = _get_document_id(result)
            if doc_id in combined_dict:
                combined_dict[doc_id]["keyword_score"] = result["score"]
            else:
                combined_dict[doc_id] = {
                    "content": result["content"],
                    "metadata": result["metadata"],
                    "vector_score": 0.0,
                    "keyword_score": result["score"]
                }
        
        # Calculate combined scores
        results = []
        for doc_id, data in combined_dict.items():
            combined_score = (
                data["vector_score"] * self.vector_weight +
                data["keyword_score"] * self.bm25_weight
            )
            
            results.append({
                "content": data["content"],
                "metadata": data["metadata"],
                "score": combined_score,
                "vector_score": data["vector_score"],
                "keyword_score": data["keyword_score"]
            })
        
        # Sort by combined score (descending)
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific document by ID.
        
        Args:
            document_id: The ID of the document to retrieve
            
        Returns:
            Document content and metadata, or None if not found
        """
        # Implementation depends on how documents are stored
        # This is a simplified placeholder
        try:
            if hasattr(self.vector_store, "get_document"):
                return await self.vector_store.get_document(document_id)
            else:
                # Fallback implementation
                documents = self.vector_store.get()
                for doc in documents:
                    if doc.metadata.get("id") == document_id:
                        return {
                            "content": doc.page_content if hasattr(doc, "page_content") else doc.text,
                            "metadata": doc.metadata
                        }
                return None
        except Exception as e:
            logger.error(f"Error retrieving document {document_id}: {str(e)}")
            return None

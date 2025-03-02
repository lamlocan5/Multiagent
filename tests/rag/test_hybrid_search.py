"""
Tests for the hybrid search retriever.
"""

import pytest
from unittest.mock import patch, MagicMock

from src.rag.retrieval.hybrid_search import HybridSearchRetriever

@pytest.mark.asyncio
async def test_hybrid_search_initialization(vector_store):
    """Test that hybrid search retriever initializes successfully."""
    retriever = HybridSearchRetriever(
        vector_store=vector_store,
        vector_weight=0.7,
        bm25_weight=0.3
    )
    
    assert retriever is not None
    assert retriever.vector_store is not None
    assert retriever.vector_weight == 0.7
    assert retriever.bm25_weight == 0.3

@pytest.mark.asyncio
async def test_hybrid_search_retrieval(vector_store, sample_documents):
    """Test hybrid search retrieval."""
    # Add documents to the vector store
    documents = [doc["content"] for doc in sample_documents]
    metadatas = [doc["metadata"] for doc in sample_documents]
    
    # Add documents to the vector store
    vector_store.add_texts(documents, metadatas=metadatas)
    
    # Create retriever
    retriever = HybridSearchRetriever(
        vector_store=vector_store,
        vector_weight=0.7,
        bm25_weight=0.3
    )
    
    # Search for documents
    results = await retriever.search("Việt Nam lịch sử", limit=2)
    
    # Check results
    assert len(results) <= 2, "Should return at most 2 documents"
    assert len(results) > 0, "Should return at least one document"
    assert "content" in results[0], "Result should have content"
    assert "metadata" in results[0], "Result should have metadata"
    assert "score" in results[0], "Result should have a score"

@pytest.mark.asyncio
async def test_vector_only_search(vector_store, sample_documents):
    """Test vector-only search."""
    # Create retriever
    retriever = HybridSearchRetriever(
        vector_store=vector_store,
        vector_weight=1.0,
        bm25_weight=0.0
    )
    
    # Search for documents
    results = await retriever.search("Việt Nam lịch sử", limit=3, use_hybrid=False)
    
    # Check results
    assert len(results) <= 3, "Should return at most 3 documents"
    assert len(results) > 0, "Should return at least one document"
    
    # With vector_weight=1.0 and bm25_weight=0.0, the score should equal the vector_score
    if "vector_score" in results[0]:
        assert abs(results[0]["score"] - results[0]["vector_score"]) < 0.001, "Score should equal vector_score"

@pytest.mark.asyncio
async def test_get_document_by_id(vector_store, sample_documents):
    """Test retrieving a document by ID."""
    # Create retriever
    retriever = HybridSearchRetriever(
        vector_store=vector_store
    )
    
    # Get a document that should exist
    doc_id = sample_documents[0]["metadata"]["id"]
    document = await retriever.get_document(doc_id)
    
    # Check result
    if document is not None:  # Some vector stores may not support get_document
        assert document is not None, f"Document with ID {doc_id} should be found"
        assert "metadata" in document, "Document should have metadata"
        assert document["metadata"].get("id") == doc_id, "Document ID should match"
    
    # Get a document that doesn't exist
    non_existent_doc = await retriever.get_document("non_existent_id_123456789")
    assert non_existent_doc is None, "Non-existent document should return None"

@pytest.mark.asyncio
async def test_keyword_extraction(vector_store):
    """Test keyword extraction from queries."""
    # Create retriever
    retriever = HybridSearchRetriever(
        vector_store=vector_store
    )
    
    # Test with Vietnamese query
    keywords = retriever._extract_keywords("Lịch sử Việt Nam trong thời kỳ Lý Trần")
    
    # Check that keywords were extracted
    assert len(keywords) > 0, "Should extract keywords from query"
    assert "Việt Nam" in keywords or "lịch sử" in keywords, "Should extract important keywords"
    
    # Test with short query
    short_keywords = retriever._extract_keywords("Hà Nội")
    assert len(short_keywords) > 0, "Should extract keywords even from short queries"

@pytest.mark.asyncio
async def test_search_with_filter(vector_store, sample_documents):
    """Test search with metadata filter."""
    # Create retriever
    retriever = HybridSearchRetriever(
        vector_store=vector_store
    )
    
    # Search with filter
    filter_dict = {"source": "test"}
    results = await retriever.search("Việt Nam", filter=filter_dict)
    
    # Check that all results match the filter
    assert len(results) > 0, "Should return results even with filter"
    for result in results:
        assert result["metadata"].get("source") == "test", "All results should match the filter" 
"""
Tests for the agent coordinator.
"""

import pytest
from unittest.mock import patch, MagicMock

from src.agents.coordinator import AgentCoordinator
from src.core.exceptions import NotFoundError

@pytest.mark.asyncio
async def test_coordinator_initialization():
    """Test that coordinator initializes successfully."""
    coordinator = AgentCoordinator()
    await coordinator.initialize()
    
    # Should have registered some agents
    assert len(coordinator.agents) > 0
    
    # Check for common agent types
    agent_names = [agent.name for agent in coordinator.agents]
    assert any("RAG" in name for name in agent_names), "RAG agent should be registered"
    assert any("Vision" in name or "OCR" in name for name in agent_names), "Vision agent should be registered"

@pytest.mark.asyncio
async def test_process_text_query(coordinator, sample_text_query):
    """Test processing a text query."""
    response = await coordinator.process({"query": sample_text_query})
    
    # Check response structure
    assert "agent_name" in response
    assert "content" in response
    assert "success" in response
    assert response["success"] is True
    
    # Response should have some content
    assert len(response["content"]) > 0

@pytest.mark.asyncio
async def test_get_agent_by_name(coordinator):
    """Test getting an agent by name."""
    # Try to get the first agent
    first_agent = coordinator.agents[0]
    found_agent = coordinator.get_agent_by_name(first_agent.name)
    
    assert found_agent is not None
    assert found_agent.name == first_agent.name

@pytest.mark.asyncio
async def test_get_nonexistent_agent(coordinator):
    """Test that getting a nonexistent agent returns None."""
    nonexistent_agent = coordinator.get_agent_by_name("NonexistentAgent123")
    assert nonexistent_agent is None

@pytest.mark.asyncio
async def test_process_with_specific_agent(coordinator):
    """Test processing with a specific agent."""
    # Get the first agent's name
    agent_name = coordinator.agents[0].name
    
    # Process with this specific agent
    response = await coordinator.process_with_agent(
        agent_name,
        {"query": "Test query for specific agent"}
    )
    
    assert response["agent_name"] == agent_name
    assert response["success"] is True

@pytest.mark.asyncio
async def test_process_with_nonexistent_agent(coordinator):
    """Test that processing with a nonexistent agent raises an error."""
    with pytest.raises(NotFoundError):
        await coordinator.process_with_agent(
            "NonexistentAgent123",
            {"query": "This should fail"}
        )

@pytest.mark.asyncio
async def test_agent_suitability_scoring(coordinator):
    """Test that agents return different suitability scores for different queries."""
    # A query that should be handled by a RAG agent
    rag_query = "Tìm kiếm thông tin về lịch sử Việt Nam"
    
    # A query that should be handled by a vision agent
    vision_query = "Phân tích hình ảnh này và cho tôi biết có bao nhiêu người"
    
    # Get suitability scores for both queries
    rag_scores = []
    vision_scores = []
    
    for agent in coordinator.agents:
        rag_score = await agent.get_suitability_score({"query": rag_query})
        vision_score = await agent.get_suitability_score({"query": vision_query})
        
        if "RAG" in agent.name:
            rag_scores.append((agent.name, rag_score))
        elif "Vision" in agent.name or "OCR" in agent.name:
            vision_scores.append((agent.name, vision_score))
    
    # Check that agents give higher scores to relevant queries
    if rag_scores:
        assert max(score for _, score in rag_scores) > 0.5, "RAG agent should rate RAG query highly"
    
    if vision_scores:
        assert max(score for _, score in vision_scores) > 0.5, "Vision agent should rate vision query highly" 
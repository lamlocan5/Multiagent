"""
Shared test fixtures and configuration.
"""

import pytest
import asyncio
import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.settings import settings
from src.agents.coordinator import AgentCoordinator
from src.rag.embeddings import get_embeddings_model
from src.rag.vectorstores import get_vector_store
from src.utils.logging import setup_global_logging

# Configure test settings
os.environ["ENVIRONMENT"] = "test"
os.environ["DEBUG"] = "True"
os.environ["VECTOR_DB_TYPE"] = "chroma"
os.environ["VECTOR_DB_HOST"] = "localhost"
settings.UPLOAD_DIR = "./tests/data/uploads"
settings.TEMP_DIR = "./tests/data/temp"

# Set up logging for tests
setup_global_logging()

@pytest.fixture(scope="session")
def event_loop():
    """Create and yield an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def coordinator():
    """Provide a configured agent coordinator for tests."""
    coordinator = AgentCoordinator()
    await coordinator.initialize()
    yield coordinator

@pytest.fixture(scope="session")
def embeddings_model():
    """Provide an embeddings model for tests."""
    return get_embeddings_model()

@pytest.fixture(scope="session")
def vector_store(embeddings_model):
    """Provide a vector store for tests."""
    return get_vector_store(
        embedding_model=embeddings_model,
        collection_name="test_documents",
        persist_directory="./tests/data/vectordb"
    )

@pytest.fixture
def sample_text_query():
    """Sample text query for testing."""
    return "Tìm kiếm thông tin về lịch sử Việt Nam"

@pytest.fixture
def sample_documents():
    """Sample documents for testing the RAG system."""
    return [
        {
            "content": "Việt Nam là một quốc gia ở Đông Nam Á với lịch sử lâu đời.",
            "metadata": {"source": "test", "id": "doc1"}
        },
        {
            "content": "Hà Nội là thủ đô của Việt Nam, có lịch sử hơn 1000 năm.",
            "metadata": {"source": "test", "id": "doc2"}
        },
        {
            "content": "Đồng bằng sông Cửu Long là vựa lúa lớn nhất của Việt Nam.",
            "metadata": {"source": "test", "id": "doc3"}
        }
    ] 
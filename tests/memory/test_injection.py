"""
Tests for memory injection functionality.
"""
import sys
from unittest.mock import Mock, patch

# Mock the Profile class so that app.models.models can be imported without error
mock_models = Mock()
mock_models.Profile = Mock()
sys.modules['app.models.models'] = mock_models

# Mock the embedding service and database to avoid external dependencies
mock_embedding = Mock()
mock_embedding.embed = Mock()
sys.modules['app.services.embedding_service'] = mock_embedding

mock_database = Mock()
sys.modules['app.database'] = mock_database

# Now we can import the memory_injection function
from app.services.memory_injection import inject_memory_context


import asyncio


async def test_inject_memory_context_no_memories():
    """Test inject_memory_context when no memories are found."""
    mock_embedding.embed.return_value = [0.1, 0.2, 0.3]

    # Mock the database session and query result
    mock_session = Mock()
    mock_context_manager = Mock()
    mock_context_manager.__enter__.return_value = mock_session
    mock_context_manager.__exit__.return_value = None
    mock_database.SessionLocal.return_value = mock_context_manager
    mock_session.execute.return_value.fetchall.return_value = []

    result = await inject_memory_context(
        user_id="test-user-id",
        query="test query"
    )

    assert result == ""


async def test_inject_memory_context_with_memories():
    """Test inject_memory_context when memories are found."""
    mock_embedding.embed.return_value = [0.1, 0.2, 0.3]

    # Mock the database session and query result
    mock_session = Mock()
    mock_context_manager = Mock()
    mock_context_manager.__enter__.return_value = mock_session
    mock_context_manager.__exit__.return_value = None
    mock_database.SessionLocal.return_value = mock_context_manager
    mock_session.execute.return_value.fetchall.return_value = [
        ("Memory content 1",),
        ("Memory content 2",)
    ]

    result = await inject_memory_context(
        user_id="test-user-id",
        query="test query"
    )

    assert result == "## Past relevant information\n- Memory content 1\n- Memory content 2"


async def test_inject_memory_context_exception_handling():
    """Test inject_memory_context handles exceptions gracefully."""
    mock_embedding.embed.side_effect = Exception("Embedding failed")

    result = await inject_memory_context(
        user_id="test-user-id",
        query="test query"
    )

    assert result == ""


def run_tests():
    """Run all tests."""
    asyncio.run(test_inject_memory_context_no_memories())
    print("✓ test_inject_memory_context_no_memories passed")

    asyncio.run(test_inject_memory_context_with_memories())
    print("✓ test_inject_memory_context_with_memories passed")

    asyncio.run(test_inject_memory_context_exception_handling())
    print("✓ test_inject_memory_context_exception_handling passed")

    print("\nAll tests passed!")


if __name__ == "__main__":
    run_tests()
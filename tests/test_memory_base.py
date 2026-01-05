import pytest
from src.memory.base import (
    BaseMemoryProvider,
    MemoryRequest,
    MemoryResponse,
    TrajectoryData,
    MemoryStatus,
)


def test_memory_request_creation():
    """Test MemoryRequest can be created with required fields."""
    request = MemoryRequest(
        query="How to handle API errors?",
        context="Working on error handling module",
        status=MemoryStatus.BEGIN,
    )
    assert request.query == "How to handle API errors?"
    assert request.status == MemoryStatus.BEGIN
    assert request.additional_params == {}


def test_memory_response_creation():
    """Test MemoryResponse can be created."""
    response = MemoryResponse(
        guidance="Use try-except with specific exceptions",
        relevant_memories=["Past error handling patterns"],
        confidence=0.85,
    )
    assert response.confidence == 0.85
    assert len(response.relevant_memories) == 1


def test_trajectory_data_creation():
    """Test TrajectoryData for learning feedback."""
    trajectory = TrajectoryData(
        task="Implement authentication",
        steps=["Read requirements", "Design flow", "Implement"],
        outcome="success",
        score=8.5,
        learnings=["JWT works well for stateless auth"],
    )
    assert trajectory.outcome == "success"
    assert trajectory.score == 8.5


def test_base_memory_provider_is_protocol():
    """Test BaseMemoryProvider defines required interface."""
    from typing import runtime_checkable, Protocol

    assert hasattr(BaseMemoryProvider, "initialize")
    assert hasattr(BaseMemoryProvider, "provide_memory")
    assert hasattr(BaseMemoryProvider, "take_in_memory")

# tests/test_dual_buffer_memory.py
import pytest
from src.memory.base import MemoryRequest, TrajectoryData, MemoryStatus
from src.memory.dual_buffer import DualBufferMemory


@pytest.fixture
def memory_provider():
    """Create a fresh memory provider for each test."""
    provider = DualBufferMemory(
        max_short_term=10,
        max_long_term_strategic=30,
        max_long_term_operational=30,
    )
    provider.initialize()
    return provider


def test_initialize_creates_empty_buffers(memory_provider):
    """Test initialization creates empty memory buffers."""
    assert memory_provider._short_term == []
    assert memory_provider._long_term_strategic == []
    assert memory_provider._long_term_operational == []


def test_provide_memory_at_begin_returns_strategic(memory_provider):
    """BEGIN phase should retrieve strategic guidance."""
    # First, add some strategic memory
    trajectory = TrajectoryData(
        task="Implement user auth",
        steps=["Research JWT", "Implement token flow"],
        outcome="success",
        score=9.0,
        learnings=["Always validate token expiry", "Use refresh tokens"],
    )
    memory_provider.take_in_memory(trajectory)

    # Now request guidance at BEGIN
    request = MemoryRequest(
        query="How to implement API authentication?",
        context="Starting new auth feature",
        status=MemoryStatus.BEGIN,
    )
    response = memory_provider.provide_memory(request)

    assert response.guidance != ""
    assert response.source_type in ("long_term", "hybrid")


def test_provide_memory_at_in_returns_operational(memory_provider):
    """IN phase should retrieve operational guidance."""
    request = MemoryRequest(
        query="Getting 401 error on API call",
        context="Step 3 of auth implementation",
        status=MemoryStatus.IN,
        additional_params={"step_number": 3},
    )
    response = memory_provider.provide_memory(request)

    assert isinstance(response.guidance, str)
    assert response.source_type in ("short_term", "hybrid")


def test_take_in_memory_stores_successful_trajectory(memory_provider):
    """Successful trajectories should be stored in long-term memory."""
    trajectory = TrajectoryData(
        task="Build REST API",
        steps=["Design endpoints", "Implement handlers", "Add validation"],
        outcome="success",
        score=8.5,
        learnings=["Use Pydantic for validation", "Return consistent error format"],
    )

    success, message = memory_provider.take_in_memory(trajectory)

    assert success is True
    assert "learned" in message.lower() or "stored" in message.lower()
    assert (
        len(memory_provider._long_term_strategic) > 0
        or len(memory_provider._long_term_operational) > 0
    )


def test_take_in_memory_handles_failure_trajectory(memory_provider):
    """Failed trajectories should inform anti-patterns."""
    trajectory = TrajectoryData(
        task="Optimize database queries",
        steps=["Write raw SQL", "Skip indexing"],
        outcome="failure",
        score=3.0,
        learnings=["Raw SQL without ORM is error-prone"],
        error_trace="OperationalError: too many connections",
    )

    success, message = memory_provider.take_in_memory(trajectory)

    assert success is True  # Learning from failure is still success
    assert "failure" in message.lower() or "avoid" in message.lower()


def test_short_term_memory_eviction(memory_provider):
    """Short-term memory should evict oldest when full."""
    # Fill short-term memory
    for i in range(15):  # More than max_short_term=10
        memory_provider._add_short_term(f"fact_{i}")

    assert len(memory_provider._short_term) <= 10
    # Oldest facts should be evicted
    assert "fact_0" not in memory_provider._short_term

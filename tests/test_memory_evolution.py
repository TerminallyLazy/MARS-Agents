import pytest
from src.graph import memory_evolution_node
from src.state import create_initial_state


def test_memory_evolution_node_exists():
    """Test memory_evolution_node function exists."""
    assert callable(memory_evolution_node)


def test_memory_evolution_triggers_on_plateau():
    """Test evolution triggers when scores plateau."""
    state = create_initial_state("Test task")
    state["scores"] = [6.0, 6.1, 6.0, 6.2]
    state["iteration"] = 5

    result = memory_evolution_node(state)

    assert "memory_evolved" in result or "evolution_attempted" in result


def test_memory_evolution_skips_if_improving():
    """Test evolution skips when scores are improving."""
    state = create_initial_state("Test task")
    state["scores"] = [5.0, 6.0, 7.0, 8.0]
    state["iteration"] = 4

    result = memory_evolution_node(state)

    assert result.get("memory_evolved", False) is False

import pytest
from unittest.mock import patch, MagicMock
from src.graph import reflection_node, _get_memory_provider
from src.state import create_initial_state, MemoryConfig


@patch("src.graph._get_memory_provider")
@patch("src.graph.ReflectionAgent")
def test_reflection_stores_trajectory(mock_reflector_class, mock_get_provider):
    """Test reflection node stores learning in memory."""
    mock_provider = MagicMock()
    mock_provider.take_in_memory.return_value = (True, "Stored learning")
    mock_get_provider.return_value = mock_provider

    mock_reflector = MagicMock()
    mock_memory = MagicMock()
    mock_memory.iteration = 1
    mock_memory.score = 7.5
    mock_memory.improvement_suggestion = "Add more detail"
    mock_reflector.return_value = mock_memory
    mock_reflector_class.return_value = mock_reflector

    state = create_initial_state("Test task")
    state["current_draft"] = "Some content"
    state["scores"] = [7.5]
    state["feedback_history"] = ["Good work"]

    result = reflection_node(state)

    assert "reflection_memories" in result
    mock_provider.take_in_memory.assert_called_once()

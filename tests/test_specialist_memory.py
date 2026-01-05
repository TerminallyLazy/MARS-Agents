import pytest
from unittest.mock import patch, MagicMock
from src.graph import specialist_agent_node, _get_memory_provider
from src.state import MemoryConfig
from src.memory.base import MemoryStatus, TrajectoryData


def test_specialist_requests_memory_guidance():
    """Test specialist agent incorporates memory guidance into its context."""
    config = MemoryConfig(provider_type="dual_buffer")
    provider = _get_memory_provider(config, "test_specialist_task")

    provider.take_in_memory(
        TrajectoryData(
            task="Similar task",
            steps=["Step 1"],
            outcome="success",
            score=8.0,
            learnings=["Use pattern X for best results"],
        )
    )

    state = {
        "agent_type": "Analysis",
        "task": "Analyze data",
        "current_draft": "",
        "iteration": 1,
        "is_boosted": False,
        "context_summary": "",
        "meta_guidance": "",
        "memory_config": config,
        "memory_task_id": "test_specialist_task",
    }

    with patch("src.graph.get_agent") as mock_get_agent:
        mock_agent = MagicMock()
        mock_agent.return_value = {
            "agent_name": "Analysis",
            "content": "Analysis result",
            "confidence": 0.8,
        }
        mock_get_agent.return_value = mock_agent

        result = specialist_agent_node(state)

        assert result is not None
        assert "agent_outputs" in result
        mock_agent.assert_called_once()

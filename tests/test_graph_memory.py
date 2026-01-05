import pytest
from src.graph import entry_node, _get_memory_provider, _get_pareto_tracker
from src.state import create_initial_state, MemoryConfig, OptimizationConfig
from src.memory import HierarchicalMemory, DualBufferMemory


def test_get_memory_provider_hierarchical():
    """Test hierarchical memory provider creation."""
    config = MemoryConfig(provider_type="hierarchical")
    provider = _get_memory_provider(config, "test_task_1")

    assert isinstance(provider, HierarchicalMemory)
    assert provider._initialized


def test_get_memory_provider_dual_buffer():
    """Test dual buffer memory provider creation."""
    config = MemoryConfig(provider_type="dual_buffer")
    provider = _get_memory_provider(config, "test_task_2")

    assert isinstance(provider, DualBufferMemory)


def test_get_pareto_tracker():
    """Test Pareto tracker creation."""
    config = OptimizationConfig(objectives=["accuracy", "clarity"])
    tracker = _get_pareto_tracker(config, "test_task_3")

    assert tracker.objectives == ["accuracy", "clarity"]


def test_entry_node_initializes_memory():
    """Test entry node sets up memory provider."""
    state = create_initial_state("Test task")

    result = entry_node(state)

    assert result.get("memory_initialized") is True
    assert "memory_config" in result
    assert "optimization_config" in result

"""Tests for state integration with memory and optimization configs."""

import pytest
from src.state import (
    AgentState,
    create_initial_state,
    MemoryConfig,
    OptimizationConfig,
)


def test_state_has_memory_config():
    """Test AgentState includes memory configuration."""
    state = create_initial_state("Test task")

    assert "memory_config" in state
    assert state["memory_config"] is not None


def test_memory_config_defaults():
    """Test MemoryConfig has sensible defaults."""
    config = MemoryConfig()

    assert config.provider_type == "hierarchical"
    assert config.max_short_term == 10
    assert config.max_long_term == 30
    assert config.enable_pareto is True


def test_optimization_config_defaults():
    """Test OptimizationConfig has sensible defaults."""
    config = OptimizationConfig()

    assert "accuracy" in config.objectives
    assert config.epsilon == 0.1
    assert config.enable_reflective_mutation is True


def test_state_initializes_with_configs():
    """Test state is initialized with both configs."""
    state = create_initial_state("Test task")

    config = state["memory_config"]
    assert config.provider_type in ("hierarchical", "dual_buffer", "simple")

    opt_config = state["optimization_config"]
    assert len(opt_config.objectives) > 0

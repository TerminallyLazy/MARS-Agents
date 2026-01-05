import pytest
from src.memory.base import MemoryRequest, TrajectoryData, MemoryStatus
from src.memory.hierarchical import HierarchicalMemory


@pytest.fixture
def hier_memory():
    provider = HierarchicalMemory()
    provider.initialize()
    return provider


def test_hierarchical_memory_init(hier_memory):
    assert hier_memory._tree is not None
    assert hier_memory._buffer is not None
    assert hier_memory._tree.root.node_id == "root"


def test_provide_memory_uses_tree_selection(hier_memory):
    trajectory = TrajectoryData(
        task="Build API",
        steps=["Design", "Implement", "Test"],
        outcome="success",
        score=8.5,
        learnings=["Use dependency injection"],
    )
    hier_memory.take_in_memory(trajectory)

    request = MemoryRequest(
        query="How to structure API?",
        context="",
        status=MemoryStatus.BEGIN,
    )
    response = hier_memory.provide_memory(request)

    assert response.guidance != ""
    assert "tree_path" in response.additional_params or response.confidence > 0


def test_take_in_memory_adds_tree_node(hier_memory):
    initial_nodes = hier_memory._tree.get_stats()["total_nodes"]

    trajectory = TrajectoryData(
        task="Optimize query",
        steps=["Profile", "Index", "Cache"],
        outcome="success",
        score=9.0,
        learnings=["Add composite index for multi-column queries"],
    )
    hier_memory.take_in_memory(trajectory)

    new_nodes = hier_memory._tree.get_stats()["total_nodes"]
    assert new_nodes > initial_nodes


def test_evolution_selects_best_branch(hier_memory):
    for i, score in enumerate([6.0, 8.0, 9.0, 7.0]):
        trajectory = TrajectoryData(
            task=f"Task {i}",
            steps=[f"Step {i}"],
            outcome="success",
            score=score,
            learnings=[f"Learning {i}"],
        )
        hier_memory.take_in_memory(trajectory)

    best_path = hier_memory._tree.get_best_path()

    if len(best_path) > 1:
        assert best_path[-1].mean_utility >= 7.0


def test_get_memory_state_returns_serializable(hier_memory):
    trajectory = TrajectoryData(
        task="Test task",
        steps=["A", "B"],
        outcome="success",
        score=7.5,
        learnings=["Test learning"],
    )
    hier_memory.take_in_memory(trajectory)

    state = hier_memory.get_memory_state()

    assert "tree_stats" in state
    assert "buffer_stats" in state
    assert isinstance(state["tree_stats"]["total_nodes"], int)

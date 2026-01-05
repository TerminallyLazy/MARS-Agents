import pytest
from src.memory.tree import MemoryNode, MemoryTree


def test_memory_node_creation():
    """Test MemoryNode can be created with required fields."""
    node = MemoryNode(
        node_id="node_001",
        content="Initial memory state",
        score=0.0,
    )
    assert node.node_id == "node_001"
    assert node.parent_id is None
    assert node.children == []
    assert node.mean_utility == 0.0


def test_memory_node_add_child():
    """Test adding child nodes."""
    parent = MemoryNode(node_id="parent", content="Parent state")
    child = MemoryNode(node_id="child", content="Child state", parent_id="parent")

    parent.add_child(child)

    assert len(parent.children) == 1
    assert parent.children[0].node_id == "child"


def test_memory_tree_creation():
    """Test MemoryTree initialization."""
    tree = MemoryTree()

    assert tree.root is not None
    assert tree.root.node_id == "root"


def test_memory_tree_add_version():
    """Test adding new memory version to tree."""
    tree = MemoryTree()

    new_node = tree.add_version(
        parent_id="root",
        content="Improved memory state",
        improvement_description="Added error handling pattern",
    )

    assert new_node is not None
    assert new_node.parent_id == "root"
    assert len(tree.root.children) == 1


def test_memory_tree_get_best_path():
    """Test finding highest-utility path in tree."""
    tree = MemoryTree()

    v1 = tree.add_version("root", "Version 1", "First improvement")
    v1.update_utility(7.0)

    v2 = tree.add_version("root", "Version 2", "Second improvement")
    v2.update_utility(8.5)

    v3 = tree.add_version(v2.node_id, "Version 3", "Build on V2")
    v3.update_utility(9.0)

    best_path = tree.get_best_path()

    assert len(best_path) == 3
    assert best_path[-1].node_id == v3.node_id


def test_thompson_sampling_selection():
    """Test Thompson sampling for exploration-exploitation."""
    tree = MemoryTree()

    for i in range(5):
        node = tree.add_version("root", f"Version {i}", f"Improvement {i}")
        node.update_utility(5.0 + i)
        node.visit_count = i + 1

    selections = [tree.select_node_thompson() for _ in range(100)]

    node_ids = [n.node_id for n in selections]
    assert len(set(node_ids)) > 1

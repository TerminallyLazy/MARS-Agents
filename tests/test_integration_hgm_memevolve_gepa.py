import pytest
from unittest.mock import patch, MagicMock

from src.state import create_initial_state, MemoryConfig, OptimizationConfig
from src.memory import HierarchicalMemory, DualBufferMemory
from src.memory.base import MemoryRequest, MemoryStatus, TrajectoryData
from src.optimization import ParetoTracker
from src.optimization.reflective_mutation import ReflectiveMutator, FailureTrace


class TestMemoryProviderIntegration:
    def test_hierarchical_memory_full_cycle(self):
        provider = HierarchicalMemory()
        assert provider.initialize()

        request = MemoryRequest(
            query="Build a REST API",
            context="",
            status=MemoryStatus.BEGIN,
        )
        response = provider.provide_memory(request)
        assert response is not None

        trajectory = TrajectoryData(
            task="Build a REST API",
            steps=["Design endpoints", "Implement handlers", "Add auth"],
            outcome="success",
            score=8.5,
            learnings=["Use JWT for auth", "Version your API endpoints"],
        )
        success, msg = provider.take_in_memory(trajectory)
        assert success

        request2 = MemoryRequest(
            query="Build another API",
            context="",
            status=MemoryStatus.BEGIN,
        )
        response2 = provider.provide_memory(request2)
        assert response2.confidence >= response.confidence

        new_node = provider.evolve_structure()
        assert new_node is not None

    def test_dual_buffer_stores_both_types(self):
        provider = DualBufferMemory()
        provider.initialize()

        provider.take_in_memory(
            TrajectoryData(
                task="Architect system",
                steps=["Design"],
                outcome="success",
                score=9.0,
                learnings=["Use microservices for scalability"],
            )
        )

        provider.take_in_memory(
            TrajectoryData(
                task="Fix bug",
                steps=["Debug"],
                outcome="success",
                score=6.5,
                learnings=["Check null pointers"],
            )
        )

        stats = provider.get_stats()
        assert stats["strategic_count"] >= 1
        assert stats["operational_count"] >= 1


class TestParetoOptimizationIntegration:
    def test_pareto_tracker_full_workflow(self):
        tracker = ParetoTracker(objectives=["accuracy", "efficiency", "clarity"])

        c1 = tracker.add_candidate(
            content={"prompt": "v1"},
            scores={"accuracy": 7.0, "efficiency": 8.0, "clarity": 6.0},
        )
        c2 = tracker.add_candidate(
            content={"prompt": "v2"},
            scores={"accuracy": 8.0, "efficiency": 6.0, "clarity": 7.0},
        )
        c3 = tracker.add_candidate(
            content={"prompt": "v3"},
            scores={"accuracy": 6.0, "efficiency": 7.0, "clarity": 8.0},
        )

        front = tracker.get_pareto_front()
        assert len(front) == 3

        c4 = tracker.add_candidate(
            content={"prompt": "v4"},
            scores={"accuracy": 5.0, "efficiency": 5.0, "clarity": 5.0},
        )

        front = tracker.get_pareto_front()
        assert len(front) == 3
        assert c4 not in front

    @patch("src.optimization.reflective_mutation.dspy")
    def test_reflective_mutation_creates_candidate(self, mock_dspy):
        mock_result = MagicMock()
        mock_result.analysis = "Prompt too vague"
        mock_result.root_cause = "Missing specificity"
        mock_result.improvement = "Add explicit requirements"
        mock_result.confidence = 0.8
        mock_dspy.ChainOfThought.return_value.return_value = mock_result

        mutator = ReflectiveMutator()

        trace = FailureTrace(
            task="Generate docs",
            candidate_content={"prompt": "Write docs"},
            expected_outcome="Complete documentation",
            actual_outcome="Missing API section",
            score=5.0,
            objectives_failed=["completeness"],
        )

        proposal = mutator.analyze_and_propose(trace)

        assert proposal is not None
        assert proposal.rationale != ""


class TestEndToEndIntegration:
    def test_state_includes_all_configs(self):
        state = create_initial_state("Test task")

        assert "memory_config" in state
        assert "optimization_config" in state
        assert isinstance(state["memory_config"], MemoryConfig)
        assert isinstance(state["optimization_config"], OptimizationConfig)

    def test_memory_tree_persists_across_iterations(self):
        from src.graph import _get_memory_provider

        config = MemoryConfig(provider_type="hierarchical")
        task_id = "persistent_test_unique"

        provider1 = _get_memory_provider(config, task_id)
        provider1.take_in_memory(
            TrajectoryData(
                task="Task 1",
                steps=["Step"],
                outcome="success",
                score=7.0,
                learnings=["Learning 1"],
            )
        )

        provider2 = _get_memory_provider(config, task_id)

        assert provider1 is provider2

        state = provider2.get_memory_state()
        assert state["tree_stats"]["total_nodes"] > 1


class TestResearchPatternCompliance:
    def test_memevolve_dual_loop_pattern(self):
        provider = HierarchicalMemory()
        provider.initialize()

        provider.take_in_memory(
            TrajectoryData(
                task="Inner loop test",
                steps=["Execute"],
                outcome="success",
                score=8.0,
                learnings=["Content evolved"],
            )
        )

        new_node = provider.evolve_structure()

        assert new_node is not None
        assert new_node.node_id.startswith("node_")

    def test_hgm_thompson_sampling(self):
        from src.memory.tree import MemoryTree

        tree = MemoryTree()

        nodes = []
        for i in range(5):
            node = tree.add_version("root", f"Content {i}", f"Improvement {i}")
            node.update_utility(5.0 + i)
            nodes.append(node)

        selections = [tree.select_node_thompson() for _ in range(50)]

        unique_ids = len(set(n.node_id for n in selections))
        assert unique_ids >= 2

    def test_gepa_pareto_dominance(self):
        from src.optimization.pareto import Candidate

        a = Candidate("a", {}, {"x": 8.0, "y": 8.0})
        b = Candidate("b", {}, {"x": 7.0, "y": 7.0})

        assert a.dominates(b)
        assert not b.dominates(a)

        c = Candidate("c", {}, {"x": 9.0, "y": 6.0})

        assert not a.dominates(c)
        assert not c.dominates(a)

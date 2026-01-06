import os
import threading
import dspy
from typing import Literal, Union
from dotenv import load_dotenv

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

from src.state import (
    AgentState,
    AgentOutput,
    create_initial_state,
    ReflectionMemory,
    CritiqueResult,
    HealthStatus,
    ConsensusVote,
    MetaLearningState,
    CONSTITUTIONAL_PRINCIPLES,
)
from src.dspy_agents import (
    AGENT_REGISTRY,
    get_agent,
    DiagramGenerator,
)
from src.self_improvement import (
    ReflectionAgent,
    ConstitutionalCritic,
    SelfHealer,
    ConsensusVoter,
    MetaLearner,
    SelfRefiner,
)
from src.memory import HierarchicalMemory, DualBufferMemory
from src.memory.base import BaseMemoryProvider
from src.optimization import ParetoTracker
from src.state import MemoryConfig, OptimizationConfig

load_dotenv()

_memory_providers: dict[str, BaseMemoryProvider] = {}
_pareto_trackers: dict[str, ParetoTracker] = {}
_provider_lock = threading.Lock()

_dspy_configured = False
_dspy_lock = threading.Lock()


def _ensure_dspy_configured():
    global _dspy_configured
    if _dspy_configured:
        return

    with _dspy_lock:
        if _dspy_configured:
            return
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        lm = dspy.LM(model="openai/gpt-4o", api_key=api_key)
        dspy.configure(lm=lm)
        _dspy_configured = True


def _extract_text_content(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts = []
        for item in content:
            if isinstance(item, str):
                texts.append(item)
            elif isinstance(item, dict) and item.get("type") == "text":
                texts.append(item.get("text", ""))
        return " ".join(texts)
    return str(content)


def _build_context_summary(state: AgentState) -> str:
    parts = []

    scores = state.get("scores", [])
    if scores:
        parts.append(f"Score history: {' -> '.join(f'{s:.1f}' for s in scores[-5:])}")

    feedback = state.get("feedback_history", [])
    if feedback:
        parts.append(f"Latest feedback: {feedback[-1][:500]}")

    reflections = state.get("reflection_memories", [])
    if reflections:
        latest = reflections[-1]
        parts.append(f"Latest insight: {latest.improvement_suggestion[:300]}")

    critiques = state.get("critiques", [])
    critical = [c for c in critiques[-3:] if c and c.severity in ("major", "critical")]
    if critical:
        parts.append(f"Critical issues: {critical[-1].revision_request[:300]}")

    return "\n".join(parts) if parts else "First iteration - no prior context."


def _get_memory_provider(config: MemoryConfig, task_id: str = "default") -> BaseMemoryProvider:
    with _provider_lock:
        if task_id in _memory_providers:
            return _memory_providers[task_id]

        if config.provider_type == "hierarchical":
            provider = HierarchicalMemory(
                max_short_term=config.max_short_term,
                max_long_term=config.max_long_term,
            )
        elif config.provider_type == "dual_buffer":
            provider = DualBufferMemory(
                max_short_term=config.max_short_term,
                max_long_term_strategic=config.max_long_term,
                max_long_term_operational=config.max_long_term,
                retrieval_frequency=config.retrieval_frequency,
            )
        else:
            provider = DualBufferMemory()

        provider.initialize()
        _memory_providers[task_id] = provider
        return provider


def _get_pareto_tracker(config: OptimizationConfig, task_id: str = "default") -> ParetoTracker:
    with _provider_lock:
        if task_id in _pareto_trackers:
            return _pareto_trackers[task_id]

        tracker = ParetoTracker(objectives=config.objectives)
        _pareto_trackers[task_id] = tracker
        return tracker


def entry_node(state: AgentState) -> dict:
    messages = state.get("messages", [])
    task = state.get("task", "")

    if not task and messages:
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage) or (hasattr(msg, "type") and msg.type == "human"):
                task = _extract_text_content(msg.content)
                break

    agent_health = {name: HealthStatus(agent_name=name) for name in AGENT_REGISTRY.keys()}

    memory_config = state.get("memory_config") or MemoryConfig()
    optimization_config = state.get("optimization_config") or OptimizationConfig()

    task_id = f"task_{hash(task)}"
    _get_memory_provider(memory_config, task_id)
    _get_pareto_tracker(optimization_config, task_id)

    return {
        "task": task,
        "iteration": 1,
        "max_iterations": 7,
        "is_boosted": False,
        "agent_health": agent_health,
        "global_health": "healthy",
        "recovery_mode": False,
        "constitutional_principles": CONSTITUTIONAL_PRINCIPLES,
        "meta_state": MetaLearningState(),
        "memory_config": memory_config,
        "optimization_config": optimization_config,
        "memory_initialized": True,
    }


def route_to_specialists(state: AgentState) -> list[Send]:
    task = state.get("task", "")
    current_draft = state.get("current_draft", "")
    iteration = state.get("iteration", 1)
    is_boosted = state.get("is_boosted", False)

    context_summary = _build_context_summary(state)

    meta_state = state.get("meta_state")
    meta_guidance = ""
    if meta_state and meta_state.adaptation_history:
        meta_guidance = meta_state.adaptation_history[-1]

    memory_config = state.get("memory_config") or MemoryConfig()
    memory_task_id = f"task_{hash(task)}"

    return [
        Send(
            "specialist_agent",
            {
                "agent_type": agent_type,
                "task": task,
                "current_draft": current_draft,
                "iteration": iteration,
                "is_boosted": is_boosted,
                "context_summary": context_summary,
                "meta_guidance": meta_guidance,
                "memory_config": memory_config,
                "memory_task_id": memory_task_id,
            },
        )
        for agent_type in AGENT_REGISTRY.keys()
    ]


def specialist_agent_node(state: dict) -> dict:
    _ensure_dspy_configured()
    agent_type = state["agent_type"]
    task = state["task"]
    current_draft = state.get("current_draft", "")
    iteration = state.get("iteration", 1)
    is_boosted = state.get("is_boosted", False)
    context_summary = state.get("context_summary", "")
    meta_guidance = state.get("meta_guidance", "")
    memory_task_id = state.get("memory_task_id", f"task_{hash(task)}")

    guidance_parts = [f"You are the {agent_type} specialist. Iteration {iteration}."]

    if is_boosted:
        guidance_parts.append("BOOST MODE: Be more aggressive and creative in your contributions.")

    if context_summary:
        guidance_parts.append(f"Context from previous iterations:\n{context_summary}")

    if meta_guidance:
        guidance_parts.append(f"Strategy guidance: {meta_guidance}")

    try:
        from src.memory.base import MemoryRequest, MemoryStatus

        memory_config = state.get("memory_config") or MemoryConfig()
        provider = _get_memory_provider(memory_config, memory_task_id)

        memory_status = MemoryStatus.BEGIN if iteration == 1 else MemoryStatus.IN
        memory_request = MemoryRequest(
            query=task,
            context=current_draft[:500] if current_draft else "",
            status=memory_status,
            additional_params={"step_number": iteration, "agent_type": agent_type},
        )
        memory_response = provider.provide_memory(memory_request)

        if memory_response.guidance and memory_response.confidence > 0.3:
            guidance_parts.append(
                f"Memory guidance (confidence: {memory_response.confidence:.2f}):\n{memory_response.guidance}"
            )
    except Exception:
        pass

    guidance = "\n\n".join(guidance_parts)

    agent = get_agent(agent_type)
    if agent is None:
        return {
            "agent_outputs": [
                AgentOutput(
                    agent_name=agent_type,
                    content=f"Agent {agent_type} not available",
                    confidence=0.0,
                )
            ]
        }

    try:
        result = agent(task=task, current_context=current_draft, guidance=guidance)
        return {
            "agent_outputs": [
                AgentOutput(
                    agent_name=result["agent_name"],
                    content=result["content"],
                    confidence=result["confidence"],
                )
            ]
        }
    except Exception as e:
        return {
            "agent_outputs": [
                AgentOutput(
                    agent_name=agent_type,
                    content=f"Error in {agent_type}: {str(e)}",
                    confidence=0.0,
                )
            ]
        }


def refiner_node(state: AgentState) -> dict:
    _ensure_dspy_configured()
    task = state.get("task", "")
    current_draft = state.get("current_draft", "")
    agent_outputs = state.get("agent_outputs", [])
    feedback_history = state.get("feedback_history", [])
    is_boosted = state.get("is_boosted", False)
    reflection_memories = state.get("reflection_memories", [])
    iteration = state.get("iteration", 1)

    contributions = "\n\n---\n\n".join(
        [
            f"## {ao.agent_name} (confidence: {ao.confidence:.2f})\n{ao.content}"
            for ao in agent_outputs
            if ao.confidence > 0
        ]
    )

    feedback = (
        feedback_history[-1]
        if feedback_history
        else "Create comprehensive initial content addressing all aspects of the task."
    )

    reflection_insights = ""
    if reflection_memories:
        recent_reflections = reflection_memories[-2:]
        reflection_insights = "\n".join(
            [f"- Iteration {r.iteration}: {r.improvement_suggestion}" for r in recent_reflections]
        )

    intensity = "Critical" if is_boosted else "High" if iteration > 3 else "Standard"

    if is_boosted:
        print(f"!!! RECURSIVE INTROSPECTION ACTIVATED (RISE pattern) - Iteration {iteration} !!!")

    refiner = SelfRefiner()

    content_to_refine = current_draft if current_draft else contributions

    result = refiner(
        task=task,
        current_content=content_to_refine,
        self_critique=f"Agent contributions:\n{contributions}\n\nPrevious feedback:\n{feedback}",
        reflection_insights=reflection_insights,
        intensity=intensity,
    )

    return {"current_draft": result["refined_content"]}


def critique_node(state: AgentState) -> dict:
    _ensure_dspy_configured()
    current_draft = state.get("current_draft", "")
    principles = state.get("constitutional_principles", CONSTITUTIONAL_PRINCIPLES)

    if not current_draft:
        return {
            "critiques": [
                CritiqueResult(
                    severity="none",
                    critique="No content to critique yet.",
                    revision_request="Generate initial content.",
                    is_acceptable=True,
                )
            ]
        }

    critic = ConstitutionalCritic()
    critique = critic(content=current_draft, principles=principles)

    return {"critiques": [critique]}


def judge_node(state: AgentState) -> dict:
    _ensure_dspy_configured()
    task = state.get("task", "")
    current_draft = state.get("current_draft", "")
    iteration = state.get("iteration", 1)

    if not current_draft:
        return {
            "scores": [0.0],
            "feedback_history": [
                "No content generated yet. Focus on creating initial comprehensive draft."
            ],
        }

    from src.dspy_agents import DocumentJudge

    judge = DocumentJudge()
    result = judge(task=task, document=current_draft)

    overall_score = result["overall_score"]
    feedback = result["feedback"]

    print(f"Iteration {iteration}: Score {overall_score:.1f}/10")

    try:
        optimization_config = state.get("optimization_config") or OptimizationConfig()
        task_id = f"task_{hash(task)}"
        tracker = _get_pareto_tracker(optimization_config, task_id)

        criteria_scores = result.get("criteria_scores", {})
        if not criteria_scores:
            criteria_scores = {obj: overall_score for obj in optimization_config.objectives}

        tracker.add_candidate(
            content={"draft_hash": hash(current_draft), "iteration": iteration},
            scores=criteria_scores,
            parent_id=None,
            mutation_description=f"Iteration {iteration} draft",
        )

        front = tracker.get_pareto_front()
        print(f"  Pareto front size: {len(front)}")

    except Exception as e:
        print(f"  Pareto tracking failed: {e}")

    return {
        "scores": [overall_score],
        "feedback_history": [feedback],
    }


def reflection_node(state: AgentState) -> dict:
    _ensure_dspy_configured()
    task = state.get("task", "")
    current_draft = state.get("current_draft", "")
    scores = state.get("scores", [])
    feedback_history = state.get("feedback_history", [])
    reflection_memories = state.get("reflection_memories", [])
    iteration = state.get("iteration", 1)

    if not scores:
        return {"reflection_memories": []}

    reflector = ReflectionAgent()
    memory = reflector(
        task=task,
        previous_output=current_draft,
        score=scores[-1],
        feedback=feedback_history[-1] if feedback_history else "No feedback yet",
        past_reflections=reflection_memories,
    )

    print(f"Reflection {iteration}: {memory.improvement_suggestion[:100]}...")

    try:
        from src.memory.base import TrajectoryData

        memory_config = state.get("memory_config") or MemoryConfig()
        memory_task_id = f"task_{hash(task)}"
        provider = _get_memory_provider(memory_config, memory_task_id)

        trajectory = TrajectoryData(
            task=task,
            steps=[f"Iteration {iteration}", f"Score: {scores[-1]:.1f}"],
            outcome="success" if scores[-1] >= 7.0 else "partial",
            score=scores[-1],
            learnings=[memory.improvement_suggestion],
            error_trace=None,
        )

        success, msg = provider.take_in_memory(trajectory)
        if success:
            print(f"  Memory updated: {msg}")
    except Exception as e:
        print(f"  Memory update failed: {e}")

    return {"reflection_memories": [memory]}


def consensus_node(state: AgentState) -> dict:
    _ensure_dspy_configured()
    current_draft = state.get("current_draft", "")
    task = state.get("task", "")

    if not current_draft:
        return {"consensus_votes": []}

    voter_roles = [
        "Technical Accuracy Reviewer - focus on correctness and completeness",
        "Clarity & Structure Expert - focus on readability and organization",
        "Practical Utility Assessor - focus on actionability and usefulness",
    ]
    voter = ConsensusVoter()

    votes = []
    for role in voter_roles:
        try:
            vote = voter(content=current_draft, task=task, voter_role=role)
            votes.append(vote)
        except Exception as e:
            print(f"Consensus voter error ({role}): {e}")

    if votes:
        avg_score = sum(v.score for v in votes) / len(votes)
        print(f"Consensus: {avg_score:.1f}/10 from {len(votes)} voters")

    return {"consensus_votes": votes}


def meta_learning_node(state: AgentState) -> dict:
    _ensure_dspy_configured()
    scores = state.get("scores", [])
    meta_state = state.get("meta_state", MetaLearningState())
    iteration = state.get("iteration", 1)

    if len(scores) < 1:
        return {"meta_state": meta_state}

    learner = MetaLearner()
    new_meta_state = learner(
        scores=scores,
        successful_patterns=meta_state.successful_patterns,
        failed_patterns=meta_state.failed_patterns,
        current_state=meta_state,
    )

    return {"meta_state": new_meta_state}


def self_healing_node(state: AgentState) -> dict:
    _ensure_dspy_configured()
    agent_health = state.get("agent_health", {})
    task = state.get("task", "")

    failed_agents = [
        name
        for name, health in agent_health.items()
        if health.status == "failed" and health.recovery_attempts < 3
    ]

    if not failed_agents:
        return {"recovery_mode": False, "global_health": "healthy"}

    healer = SelfHealer()
    updated_health = agent_health.copy()

    for agent_name in failed_agents:
        health = updated_health[agent_name]
        recovery = healer(
            agent_name=agent_name,
            error_message=health.last_error or "Unknown error",
            error_count=health.error_count,
            task_context=task,
        )

        if recovery["should_retry"]:
            updated_health[agent_name] = HealthStatus(
                agent_name=agent_name,
                status="recovering",
                error_count=health.error_count,
                recovery_attempts=health.recovery_attempts + 1,
            )
            print(f"!!! SELF-HEALING: {agent_name} - {recovery['recovery_strategy'][:100]} !!!")
        else:
            updated_health[agent_name] = HealthStatus(
                agent_name=agent_name,
                status="degraded",
                error_count=health.error_count,
                recovery_attempts=health.recovery_attempts + 1,
            )

    degraded_count = sum(1 for h in updated_health.values() if h.status in ["failed", "degraded"])
    global_health = (
        "critical" if degraded_count > 2 else "degraded" if degraded_count > 0 else "healthy"
    )

    return {
        "agent_health": updated_health,
        "global_health": global_health,
        "recovery_mode": len(failed_agents) > 0,
    }


def loop_decision_node(state: AgentState) -> dict:
    iteration = state.get("iteration", 1)
    scores = state.get("scores", [])

    is_boosted = False
    if len(scores) >= 2:
        delta = scores[-1] - scores[-2]
        if delta < 0.3 and scores[-1] < 8.0:
            is_boosted = True
            print(f"!!! TRIGGERING RECURSIVE BOOST - Score delta {delta:.2f} !!!")

    return {
        "iteration": iteration + 1,
        "is_boosted": is_boosted,
    }


def memory_evolution_node(state: AgentState) -> dict:
    scores = state.get("scores", [])
    iteration = state.get("iteration", 1)
    task = state.get("task", "")

    should_evolve = False

    if len(scores) >= 3:
        recent = scores[-3:]
        mean_score = sum(recent) / len(recent)
        variance = sum((s - mean_score) ** 2 for s in recent) / len(recent)

        if variance < 0.25 and mean_score < 8.0:
            should_evolve = True
            print(
                f"!!! MEMORY EVOLUTION TRIGGERED - Score plateau detected (var={variance:.3f}) !!!"
            )

    if not should_evolve:
        return {"memory_evolved": False, "evolution_attempted": False}

    try:
        memory_config = state.get("memory_config") or MemoryConfig()
        task_id = f"task_{hash(task)}"

        if memory_config.provider_type == "hierarchical":
            provider = _get_memory_provider(memory_config, task_id)

            if hasattr(provider, "evolve_structure"):
                new_node = provider.evolve_structure()
                if new_node:
                    print(f"  Evolved to new memory node: {new_node.node_id}")
                    return {
                        "memory_evolved": True,
                        "evolution_attempted": True,
                    }

        return {"memory_evolved": False, "evolution_attempted": True}

    except Exception as e:
        print(f"  Memory evolution failed: {e}")
        return {"memory_evolved": False, "evolution_attempted": True}


def route_after_evolution(state: AgentState) -> Literal["loop_decision", "diagram"]:
    iteration = state.get("iteration", 1)
    max_iterations = state.get("max_iterations", 7)
    scores = state.get("scores", [])
    critiques = state.get("critiques", [])
    consensus_votes = state.get("consensus_votes", [])

    if scores and scores[-1] >= 8.5:
        print(f"Target score reached: {scores[-1]:.1f}/10")
        return "diagram"

    if iteration >= max_iterations:
        print(f"Max iterations ({max_iterations}) reached")
        return "diagram"

    has_critical = any(c.severity == "critical" for c in critiques[-3:] if c)
    if has_critical:
        print("!!! CONSTITUTIONAL VIOLATION - Forcing another iteration !!!")
        return "loop_decision"

    if consensus_votes:
        recent = consensus_votes[-3:]
        avg = sum(v.score for v in recent) / len(recent) if recent else 0
        if avg >= 8.5:
            print(f"Consensus threshold reached: {avg:.1f}/10")
            return "diagram"

    return "loop_decision"


def route_after_meta(state: AgentState) -> Literal["memory_evolution"]:
    return "memory_evolution"


def route_after_loop(state: AgentState) -> Union[list[Send], Literal["self_healing"]]:
    recovery_mode = state.get("recovery_mode", False)
    global_health = state.get("global_health", "healthy")

    if recovery_mode or global_health == "critical":
        return "self_healing"

    return route_to_specialists(state)


def diagram_node(state: AgentState) -> dict:
    _ensure_dspy_configured()
    current_draft = state.get("current_draft", "")
    scores = state.get("scores", [0])
    final_score = scores[-1] if scores else 0
    iteration = state.get("iteration", 1)
    reflection_memories = state.get("reflection_memories", [])
    meta_state = state.get("meta_state", MetaLearningState())

    diagram_gen = DiagramGenerator()
    result = diagram_gen(document=current_draft)

    learnings = (
        "\n".join(
            [
                f"- **Iteration {m.iteration}** (score: {m.score:.1f}): {m.improvement_suggestion}"
                for m in reflection_memories[-5:]
            ]
        )
        if reflection_memories
        else "No reflection memories recorded."
    )

    score_progression = " → ".join([f"{s:.1f}" for s in scores]) if scores else "N/A"

    response_content = f"""# Document Generation Complete

## Performance Summary
- **Final Score:** {final_score:.1f}/10
- **Total Iterations:** {iteration}
- **Score Progression:** {score_progression}
- **Self-Improvement Cycles:** {len(reflection_memories)}

---

## Key Learnings (Reflexion Memory)

{learnings}

---

## Generated Document

{current_draft}

---

## System Architecture Diagram

```mermaid
{result["code"]}
```
"""

    return {
        "diagram": result["code"],
        "final_document": current_draft,
        "messages": [AIMessage(content=response_content)],
    }


workflow = StateGraph(AgentState)

workflow.add_node("entry", entry_node)
workflow.add_node("specialist_agent", specialist_agent_node)
workflow.add_node("refiner", refiner_node)
workflow.add_node("critique", critique_node)
workflow.add_node("judge", judge_node)
workflow.add_node("reflection", reflection_node)
workflow.add_node("consensus", consensus_node)
workflow.add_node("meta_learning", meta_learning_node)
workflow.add_node("memory_evolution", memory_evolution_node)
workflow.add_node("loop_decision", loop_decision_node)
workflow.add_node("self_healing", self_healing_node)
workflow.add_node("diagram", diagram_node)

workflow.add_edge(START, "entry")
workflow.add_conditional_edges("entry", route_to_specialists, ["specialist_agent"])
workflow.add_edge("specialist_agent", "refiner")
workflow.add_edge("refiner", "critique")
workflow.add_edge("critique", "judge")
workflow.add_edge("judge", "reflection")
workflow.add_edge("reflection", "consensus")
workflow.add_edge("consensus", "meta_learning")
workflow.add_conditional_edges("meta_learning", route_after_meta, ["memory_evolution"])
workflow.add_conditional_edges(
    "memory_evolution", route_after_evolution, ["loop_decision", "diagram"]
)
workflow.add_conditional_edges(
    "loop_decision", route_after_loop, ["specialist_agent", "self_healing"]
)
workflow.add_conditional_edges("self_healing", route_to_specialists, ["specialist_agent"])
workflow.add_edge("diagram", END)

graph = workflow.compile()


def run_multi_agent_system(user_input: str) -> dict:
    initial_state = create_initial_state(user_input)
    # 6 specialists + 8 linear nodes per iteration = ~14 transitions/iteration
    # max_iterations=7 → need ~100+ limit for safety
    final_state = graph.invoke(initial_state, {"recursion_limit": 150})
    return {
        "document": final_state.get("final_document", ""),
        "diagram": final_state.get("diagram", ""),
        "scores": final_state.get("scores", []),
        "iterations": final_state.get("iteration", 0),
        "reflection_memories": final_state.get("reflection_memories", []),
        "meta_state": final_state.get("meta_state"),
    }


if __name__ == "__main__":
    result = run_multi_agent_system(
        "Create an AGENTS.md for a multi-agent research system with recursive self-improvement"
    )
    print("\n" + "=" * 60)
    print("FINAL DOCUMENT:")
    print("=" * 60)
    print(result["document"][:3000])
    print(f"\nCompleted in {result['iterations']} iterations")
    print(f"Score progression: {result['scores']}")

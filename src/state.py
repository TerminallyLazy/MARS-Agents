"""State schema for self-improving multi-agent system with reflection and self-healing."""

import operator
from typing import Annotated, TypedDict, Literal, Optional
from pydantic import BaseModel, Field
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from datetime import datetime


class AgentOutput(BaseModel):
    agent_name: str = Field(description="Name of the agent")
    content: str = Field(description="Agent's output content")
    confidence: float = Field(default=0.8, description="Confidence score 0-1")
    reasoning: str = Field(default="", description="Chain of thought reasoning")


class ReflectionMemory(BaseModel):
    """Episodic memory for Reflexion pattern - stores past attempts and learnings."""

    iteration: int
    action_taken: str
    outcome: str
    score: float
    reflection: str = Field(description="What was learned from this attempt")
    improvement_suggestion: str = Field(description="Concrete suggestion for next attempt")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class CritiqueResult(BaseModel):
    """Constitutional AI critique output."""

    principle_violated: Optional[str] = Field(
        default=None, description="Which principle was violated, if any"
    )
    severity: Literal["none", "minor", "major", "critical"] = Field(default="none")
    critique: str = Field(description="Detailed critique")
    revision_request: str = Field(description="Specific request for revision")
    is_acceptable: bool = Field(default=True)


class HealthStatus(BaseModel):
    """Self-healing health tracking."""

    agent_name: str
    status: Literal["healthy", "degraded", "failed", "recovering"] = "healthy"
    error_count: int = 0
    last_error: Optional[str] = None
    recovery_attempts: int = 0
    last_successful_run: Optional[str] = None


class ConsensusVote(BaseModel):
    """Multi-agent debate vote."""

    voter: str
    score: float
    rationale: str
    suggested_improvements: list[str] = Field(default_factory=list)


class MetaLearningState(BaseModel):
    """Meta-learner state for strategy adaptation."""

    strategy_weights: dict[str, float] = Field(
        default_factory=lambda: {
            "depth_vs_breadth": 0.5,
            "creativity_vs_precision": 0.5,
            "exploration_vs_exploitation": 0.5,
        }
    )
    successful_patterns: list[str] = Field(default_factory=list)
    failed_patterns: list[str] = Field(default_factory=list)
    adaptation_history: list[str] = Field(default_factory=list)


class MemoryConfig(BaseModel):
    provider_type: Literal["hierarchical", "dual_buffer", "simple"] = "hierarchical"
    max_short_term: int = Field(default=10)
    max_long_term: int = Field(default=30)
    enable_pareto: bool = Field(default=True)
    enable_tree: bool = Field(default=True)
    retrieval_frequency: int = Field(default=3)


class OptimizationConfig(BaseModel):
    objectives: list[str] = Field(default_factory=lambda: ["accuracy", "completeness", "clarity"])
    epsilon: float = Field(default=0.1)
    enable_reflective_mutation: bool = True
    prune_dominated_threshold: int = Field(default=10)


class AgentState(TypedDict):
    """Enhanced state with self-improvement, reflection, and self-healing capabilities."""

    messages: Annotated[list[AnyMessage], add_messages]
    task: str

    agent_outputs: Annotated[list[AgentOutput], operator.add]
    current_draft: str

    scores: Annotated[list[float], operator.add]
    feedback_history: Annotated[list[str], operator.add]

    iteration: int
    max_iterations: int
    is_boosted: bool

    reflection_memories: Annotated[list[ReflectionMemory], operator.add]

    critiques: Annotated[list[CritiqueResult], operator.add]
    constitutional_principles: list[str]

    agent_health: dict[str, HealthStatus]
    global_health: Literal["healthy", "degraded", "critical"]
    recovery_mode: bool

    consensus_votes: Annotated[list[ConsensusVote], operator.add]
    consensus_threshold: float

    meta_state: MetaLearningState

    memory_config: MemoryConfig
    optimization_config: OptimizationConfig

    final_document: str
    diagram: str


CONSTITUTIONAL_PRINCIPLES = [
    "Output must be technically accurate and factually grounded",
    "Content should be comprehensive yet concise - no unnecessary verbosity",
    "Structure should follow established documentation patterns",
    "All claims should be verifiable or clearly marked as hypothetical",
    "The system should demonstrate clear reasoning chains",
    "Output should be actionable and practically useful",
    "Failures should be acknowledged transparently, not hidden",
    "Improvements should be measurable and concrete",
]


def create_initial_state(user_input: str) -> AgentState:
    from langchain_core.messages import HumanMessage

    return AgentState(
        messages=[HumanMessage(content=user_input)],
        task=user_input,
        agent_outputs=[],
        current_draft="",
        scores=[],
        feedback_history=[],
        iteration=0,
        max_iterations=7,
        is_boosted=False,
        reflection_memories=[],
        critiques=[],
        constitutional_principles=CONSTITUTIONAL_PRINCIPLES,
        agent_health={},
        global_health="healthy",
        recovery_mode=False,
        consensus_votes=[],
        consensus_threshold=0.7,
        meta_state=MetaLearningState(),
        memory_config=MemoryConfig(),
        optimization_config=OptimizationConfig(),
        final_document="",
        diagram="",
    )


class ParallelAgentState(TypedDict):
    agent_type: str
    task: str
    current_draft: str
    guidance: str
    meta_guidance: Optional[str]

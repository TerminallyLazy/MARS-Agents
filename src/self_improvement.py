import dspy
from typing import Optional
from src.state import (
    ReflectionMemory,
    CritiqueResult,
    HealthStatus,
    ConsensusVote,
    MetaLearningState,
    CONSTITUTIONAL_PRINCIPLES,
)


class ReflectionSignature(dspy.Signature):
    """You are implementing the Reflexion pattern (Shinn et al. 2023). Analyze the previous attempt's trajectory to extract actionable learnings. Focus on: (1) what specific aspects led to the current score, (2) what patterns from past iterations should be reinforced or avoided, (3) concrete next steps. Your reflection will be stored in episodic memory and used to guide future iterations."""

    task: str = dspy.InputField(desc="The original task/goal being worked toward")
    previous_output: str = dspy.InputField(desc="The output from the previous iteration")
    score: float = dspy.InputField(desc="Quality score 0-10 from the judge")
    feedback: str = dspy.InputField(desc="Detailed feedback from the judge explaining the score")
    past_reflections: str = dspy.InputField(
        desc="Summary of learnings from previous iterations - use this to avoid repeating mistakes"
    )

    reflection: str = dspy.OutputField(
        desc="Deep analysis: What worked? What didn't? Why did we get this score? Be specific and actionable."
    )
    root_cause: str = dspy.OutputField(
        desc="The fundamental reason for any shortcomings - dig beyond surface issues"
    )
    improvement_strategy: str = dspy.OutputField(
        desc="Concrete, specific strategy for the next iteration - what exactly should change?"
    )
    confidence_adjustment: float = dspy.OutputField(
        desc="How much to adjust confidence: -1 (major issues) to +1 (exceeded expectations)"
    )


class ConstitutionalCritiqueSignature(dspy.Signature):
    """You are a Constitutional AI critic (Anthropic 2022). Your role is to evaluate content against a set of inviolable principles. Unlike general feedback, you focus ONLY on principle violations. Be strict but fair - only flag genuine violations, not stylistic preferences. Your critique directly influences whether content can proceed or must be revised."""

    content: str = dspy.InputField(desc="The content to evaluate against constitutional principles")
    principles: str = dspy.InputField(desc="The constitutional principles - each must be checked")

    violated_principle: str = dspy.OutputField(
        desc="Which specific principle was violated, or 'none' if all principles are satisfied"
    )
    severity: str = dspy.OutputField(
        desc="Severity level: 'none' (no violation), 'minor' (small issue), 'major' (significant problem), 'critical' (must fix before proceeding)"
    )
    critique: str = dspy.OutputField(
        desc="Detailed explanation of the violation - quote the specific problematic content"
    )
    revision_request: str = dspy.OutputField(
        desc="Specific, actionable revision request that would fix the violation"
    )
    is_acceptable: bool = dspy.OutputField(
        desc="True if content meets constitutional standards, False if revision required"
    )


class SelfHealingSignature(dspy.Signature):
    """You are a Self-Healing diagnostic agent. When an agent fails, you must: (1) diagnose the root cause from the error, (2) determine if retry is viable, (3) propose a recovery strategy, (4) suggest preventive measures. Your goal is system resilience - keep the pipeline running even when individual components fail."""

    agent_name: str = dspy.InputField(desc="Name of the agent that failed")
    error_message: str = dspy.InputField(desc="The error message or failure description")
    error_count: int = dspy.InputField(
        desc="How many times this agent has failed (for retry decisions)"
    )
    task_context: str = dspy.InputField(desc="The task the agent was attempting")

    diagnosis: str = dspy.OutputField(desc="Root cause analysis - why did this agent fail?")
    recovery_strategy: str = dspy.OutputField(
        desc="Step-by-step recovery plan: what should we do to recover?"
    )
    should_retry: bool = dspy.OutputField(
        desc="True if retry is likely to succeed, False if we should skip/fallback"
    )
    fallback_action: str = dspy.OutputField(desc="What to do if retry fails or is not advisable")
    preventive_measures: str = dspy.OutputField(
        desc="How to prevent this failure in future iterations"
    )


class ConsensusSignature(dspy.Signature):
    """You are a specialized reviewer in a multi-agent debate system. Evaluate the content from your specific role's perspective. Your vote will be combined with other reviewers to reach consensus. Be critical but constructive - identify both strengths and areas for improvement."""

    content: str = dspy.InputField(desc="The content to evaluate")
    task: str = dspy.InputField(desc="The original task/goal")
    voter_role: str = dspy.InputField(
        desc="Your review perspective (e.g., 'Technical Reviewer', 'UX Expert', 'QA')"
    )

    score: float = dspy.OutputField(desc="Quality score 0-10 from your role's perspective")
    rationale: str = dspy.OutputField(
        desc="Detailed reasoning for your score - what aspects influenced it?"
    )
    improvements: str = dspy.OutputField(
        desc="Comma-separated list of specific improvements from your perspective"
    )
    confidence: float = dspy.OutputField(
        desc="Your confidence in this assessment 0-1 (1 = certain, 0 = guessing)"
    )


class MetaLearningSignature(dspy.Signature):
    """You are a Meta-Learning agent implementing strategy adaptation (MAML-inspired). Analyze performance trends across iterations to adjust the system's approach. Look for: (1) patterns in successful vs failed iterations, (2) strategy adjustments that improved scores, (3) optimal balance between exploration and exploitation."""

    performance_history: str = dspy.InputField(
        desc="Score trajectory across iterations (e.g., '5.0 -> 6.5 -> 7.2')"
    )
    successful_patterns: str = dspy.InputField(
        desc="Strategies/approaches that led to score improvements"
    )
    failed_patterns: str = dspy.InputField(desc="Strategies/approaches that led to score decreases")
    current_strategy: str = dspy.InputField(desc="Current strategy weights as dict")

    strategy_adjustment: str = dspy.OutputField(
        desc="What strategic change to make based on the patterns observed"
    )
    new_weights: str = dspy.OutputField(
        desc="Updated weights as 'key:value,key:value' format. Keys: depth_vs_breadth, creativity_vs_precision, exploration_vs_exploitation. Values: 0.0-1.0"
    )
    reasoning: str = dspy.OutputField(
        desc="Why this adjustment is recommended based on the performance patterns"
    )


class SelfRefineSignature(dspy.Signature):
    """You are implementing SELF-REFINE (Madaan et al. 2023). Given content, critique, and reflection insights, produce an improved version. Key principles: (1) address ALL points in the critique, (2) incorporate insights from reflection memory, (3) maintain what's working well, (4) be more aggressive with changes when intensity is 'High' or 'Critical'."""

    task: str = dspy.InputField(desc="The original task/goal")
    current_content: str = dspy.InputField(desc="The current version of the content to refine")
    self_critique: str = dspy.InputField(desc="Feedback and critique to address")
    reflection_insights: str = dspy.InputField(
        desc="Insights from reflection memory - learnings from previous iterations"
    )
    intensity: str = dspy.InputField(
        desc="Refinement intensity: 'Standard' (incremental), 'High' (significant changes), 'Critical' (major overhaul)"
    )

    refined_content: str = dspy.OutputField(
        desc="The improved content - must address all critique points and incorporate reflection insights"
    )
    changes_made: str = dspy.OutputField(desc="Explicit list of what was changed and why")
    remaining_issues: str = dspy.OutputField(
        desc="Any issues that couldn't be fully resolved in this iteration"
    )


class ReflectionAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.reflector = dspy.ChainOfThought(ReflectionSignature)

    def forward(
        self,
        task: str,
        previous_output: str,
        score: float,
        feedback: str,
        past_reflections: list[ReflectionMemory],
    ) -> ReflectionMemory:
        past_summary = (
            "\n".join(
                [
                    f"Iteration {r.iteration} (score={r.score:.1f}): {r.reflection} -> Action: {r.improvement_suggestion}"
                    for r in past_reflections[-3:]
                ]
            )
            if past_reflections
            else "This is the first iteration - no prior reflections available."
        )

        result = self.reflector(
            task=task,
            previous_output=previous_output[:3000],
            score=score,
            feedback=feedback,
            past_reflections=past_summary,
        )

        return ReflectionMemory(
            iteration=len(past_reflections) + 1,
            action_taken=f"Generated output with score {score:.1f}",
            outcome="success" if score >= 7.0 else "needs_improvement",
            score=score,
            reflection=result.reflection,
            improvement_suggestion=result.improvement_strategy,
        )


class ConstitutionalCritic(dspy.Module):
    def __init__(self):
        super().__init__()
        self.critic = dspy.ChainOfThought(ConstitutionalCritiqueSignature)

    def forward(self, content: str, principles: list[str] = None) -> CritiqueResult:
        principles = principles or CONSTITUTIONAL_PRINCIPLES
        principles_text = "\n".join(f"{i + 1}. {p}" for i, p in enumerate(principles))

        result = self.critic(content=content[:4000], principles=principles_text)

        severity_map = {"none": "none", "minor": "minor", "major": "major", "critical": "critical"}
        raw_severity = str(result.severity).lower().strip()
        severity = severity_map.get(raw_severity, "minor")

        return CritiqueResult(
            principle_violated=result.violated_principle
            if result.violated_principle.lower() != "none"
            else None,
            severity=severity,
            critique=result.critique,
            revision_request=result.revision_request,
            is_acceptable=result.is_acceptable
            if isinstance(result.is_acceptable, bool)
            else str(result.is_acceptable).lower() == "true",
        )


class SelfHealer(dspy.Module):
    def __init__(self):
        super().__init__()
        self.healer = dspy.ChainOfThought(SelfHealingSignature)

    def forward(
        self, agent_name: str, error_message: str, error_count: int, task_context: str
    ) -> dict:
        result = self.healer(
            agent_name=agent_name,
            error_message=error_message,
            error_count=error_count,
            task_context=task_context[:1500],
        )

        should_retry = result.should_retry
        if isinstance(should_retry, str):
            should_retry = should_retry.lower() == "true"

        return {
            "diagnosis": result.diagnosis,
            "recovery_strategy": result.recovery_strategy,
            "should_retry": should_retry and error_count < 3,
            "fallback_action": result.fallback_action,
            "preventive_measures": result.preventive_measures,
        }


class ConsensusVoter(dspy.Module):
    def __init__(self):
        super().__init__()
        self.voter = dspy.ChainOfThought(ConsensusSignature)

    def forward(self, content: str, task: str, voter_role: str) -> ConsensusVote:
        result = self.voter(content=content[:3000], task=task, voter_role=voter_role)

        try:
            score = float(result.score)
            score = max(0.0, min(10.0, score))
        except (ValueError, TypeError):
            score = 5.0

        try:
            confidence = float(result.confidence)
            confidence = max(0.0, min(1.0, confidence))
        except (ValueError, TypeError):
            confidence = 0.5

        improvements = [s.strip() for s in str(result.improvements).split(",") if s.strip()]

        return ConsensusVote(
            voter=voter_role,
            score=score,
            rationale=result.rationale,
            suggested_improvements=improvements[:5],
        )


class MetaLearner(dspy.Module):
    def __init__(self):
        super().__init__()
        self.learner = dspy.ChainOfThought(MetaLearningSignature)

    def forward(
        self,
        scores: list[float],
        successful_patterns: list[str],
        failed_patterns: list[str],
        current_state: MetaLearningState,
    ) -> MetaLearningState:
        if not scores:
            return current_state

        performance_history = " -> ".join([f"{s:.1f}" for s in scores[-5:]])

        trend = (
            "improving"
            if len(scores) >= 2 and scores[-1] > scores[-2]
            else "declining"
            if len(scores) >= 2 and scores[-1] < scores[-2]
            else "stable"
        )
        performance_history = f"{performance_history} (trend: {trend})"

        result = self.learner(
            performance_history=performance_history,
            successful_patterns=", ".join(successful_patterns[-5:])
            if successful_patterns
            else "No successful patterns recorded yet",
            failed_patterns=", ".join(failed_patterns[-5:])
            if failed_patterns
            else "No failed patterns recorded yet",
            current_strategy=str(current_state.strategy_weights),
        )

        new_weights = current_state.strategy_weights.copy()
        try:
            for pair in str(result.new_weights).split(","):
                if ":" in pair:
                    key, value = pair.split(":", 1)
                    key = key.strip()
                    if key in new_weights:
                        new_weights[key] = max(0.0, min(1.0, float(value.strip())))
        except (ValueError, AttributeError):
            pass

        new_successful = successful_patterns.copy()
        new_failed = failed_patterns.copy()

        if scores[-1] >= 8.0:
            new_successful.append(result.strategy_adjustment)
        elif scores[-1] < 6.0:
            new_failed.append(result.strategy_adjustment)

        return MetaLearningState(
            strategy_weights=new_weights,
            successful_patterns=new_successful[-10:],
            failed_patterns=new_failed[-10:],
            adaptation_history=(current_state.adaptation_history + [result.reasoning])[-10:],
        )


class SelfRefiner(dspy.Module):
    def __init__(self):
        super().__init__()
        self.refiner = dspy.ChainOfThought(SelfRefineSignature)

    def forward(
        self,
        task: str,
        current_content: str,
        self_critique: str,
        reflection_insights: str,
        intensity: str = "Standard",
    ) -> dict:
        result = self.refiner(
            task=task,
            current_content=current_content
            if current_content
            else "No content yet - create initial draft.",
            self_critique=self_critique
            if self_critique
            else "No critique yet - focus on creating comprehensive initial content.",
            reflection_insights=reflection_insights
            if reflection_insights
            else "First iteration - no prior insights.",
            intensity=intensity,
        )

        return {
            "refined_content": result.refined_content,
            "changes_made": result.changes_made,
            "remaining_issues": result.remaining_issues,
        }

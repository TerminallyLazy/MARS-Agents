import asyncio
import dspy
from typing import Optional


class WebResearchSignature(dspy.Signature):
    """Determine what web research is needed and synthesize findings."""

    task: str = dspy.InputField()
    current_context: str = dspy.InputField()
    guidance: str = dspy.InputField()
    search_queries: str = dspy.OutputField(
        desc="Comma-separated list of specific search queries to execute"
    )
    research_focus: str = dspy.OutputField(desc="Key areas to focus research on")


class WebSynthesisSignature(dspy.Signature):
    """Synthesize web research findings into actionable insights."""

    task: str = dspy.InputField()
    search_results: str = dspy.InputField()
    guidance: str = dspy.InputField()
    synthesized_findings: str = dspy.OutputField(
        desc="Comprehensive synthesis of web research findings"
    )
    key_sources: str = dspy.OutputField(desc="Most valuable sources found with URLs")
    confidence_assessment: str = dspy.OutputField(
        desc="Assessment of information reliability and gaps"
    )


class DataProcessingSignature(dspy.Signature):
    """Process and validate data for a given task."""

    task: str = dspy.InputField()
    current_context: str = dspy.InputField()
    guidance: str = dspy.InputField()
    processed_data: str = dspy.OutputField(
        desc="Cleaned, validated, and structured data relevant to the task"
    )
    data_quality_notes: str = dspy.OutputField(
        desc="Notes on data quality, anomalies, or gaps identified"
    )


class AnalysisSignature(dspy.Signature):
    """Analyze data and generate hypotheses."""

    task: str = dspy.InputField()
    current_context: str = dspy.InputField()
    guidance: str = dspy.InputField()
    analysis: str = dspy.OutputField(
        desc="Statistical and predictive analysis with patterns identified"
    )
    hypotheses: str = dspy.OutputField(desc="Generated hypotheses based on the analysis")


class ExperimentalSignature(dspy.Signature):
    """Design experiments and report findings."""

    task: str = dspy.InputField()
    current_context: str = dspy.InputField()
    guidance: str = dspy.InputField()
    experiment_design: str = dspy.OutputField(desc="Experimental methodology and test scenarios")
    findings: str = dspy.OutputField(desc="Results and findings from conceptual experiments")


class LearningSignature(dspy.Signature):
    """Synthesize knowledge and extract insights."""

    task: str = dspy.InputField()
    current_context: str = dspy.InputField()
    guidance: str = dspy.InputField()
    knowledge_synthesis: str = dspy.OutputField(
        desc="Accumulated and integrated knowledge from all sources"
    )
    learning_insights: str = dspy.OutputField(desc="Meta-learning insights and adaptations")


class OptimizationSignature(dspy.Signature):
    """Identify optimization opportunities and strategies."""

    task: str = dspy.InputField()
    current_context: str = dspy.InputField()
    guidance: str = dspy.InputField()
    optimization_strategies: str = dspy.OutputField(
        desc="Identified optimization opportunities and strategies"
    )
    efficiency_improvements: str = dspy.OutputField(
        desc="Specific efficiency improvements proposed"
    )


class CreativeSignature(dspy.Signature):
    """Generate creative and innovative solutions."""

    task: str = dspy.InputField()
    current_context: str = dspy.InputField()
    guidance: str = dspy.InputField()
    creative_solutions: str = dspy.OutputField(
        desc="Novel and innovative solutions using generative approaches"
    )
    ideation_notes: str = dspy.OutputField(desc="Creative reasoning and ideation process")


class RefineDocumentSignature(dspy.Signature):
    """Refine and improve a document based on feedback."""

    task: str = dspy.InputField()
    current_draft: str = dspy.InputField()
    agent_contributions: str = dspy.InputField()
    feedback: str = dspy.InputField()
    intensity: str = dspy.InputField(desc="Standard or High intensity refinement")
    refined_document: str = dspy.OutputField(desc="The refined and improved document")


class JudgeDocumentSignature(dspy.Signature):
    """Evaluate a document and provide scores and feedback."""

    task: str = dspy.InputField()
    document: str = dspy.InputField()
    clarity_score: float = dspy.OutputField(desc="Score 0-10 for clarity")
    completeness_score: float = dspy.OutputField(desc="Score 0-10 for completeness")
    coherence_score: float = dspy.OutputField(desc="Score 0-10 for coherence")
    innovation_score: float = dspy.OutputField(desc="Score 0-10 for innovation")
    overall_score: float = dspy.OutputField(desc="Overall score 0-10")
    feedback: str = dspy.OutputField(desc="Detailed improvement feedback")
    strengths: str = dspy.OutputField(desc="Key strengths comma-separated")
    improvements: str = dspy.OutputField(desc="Areas to improve comma-separated")


class GenerateDiagramSignature(dspy.Signature):
    """Generate a Mermaid diagram from a document."""

    document: str = dspy.InputField()
    diagram_type: str = dspy.OutputField(desc="flowchart, sequence, or class")
    mermaid_code: str = dspy.OutputField(desc="Valid Mermaid.js diagram code")


class DataProcessingAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.processor = dspy.ChainOfThought(DataProcessingSignature)

    def forward(self, task: str, current_context: str, guidance: str) -> dict:
        result = self.processor(task=task, current_context=current_context, guidance=guidance)
        return {
            "agent_name": "DataProcessingAgent",
            "content": f"{result.processed_data}\n\nData Quality: {result.data_quality_notes}",
            "confidence": 0.85,
        }


class AnalysisAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.analyzer = dspy.ChainOfThought(AnalysisSignature)

    def forward(self, task: str, current_context: str, guidance: str) -> dict:
        result = self.analyzer(task=task, current_context=current_context, guidance=guidance)
        return {
            "agent_name": "AnalysisAgent",
            "content": f"{result.analysis}\n\nHypotheses: {result.hypotheses}",
            "confidence": 0.82,
        }


class ExperimentalAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.experimenter = dspy.ChainOfThought(ExperimentalSignature)

    def forward(self, task: str, current_context: str, guidance: str) -> dict:
        result = self.experimenter(task=task, current_context=current_context, guidance=guidance)
        return {
            "agent_name": "ExperimentalAgent",
            "content": f"{result.experiment_design}\n\nFindings: {result.findings}",
            "confidence": 0.78,
        }


class LearningAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.learner = dspy.ChainOfThought(LearningSignature)

    def forward(self, task: str, current_context: str, guidance: str) -> dict:
        result = self.learner(task=task, current_context=current_context, guidance=guidance)
        return {
            "agent_name": "LearningAgent",
            "content": f"{result.knowledge_synthesis}\n\nMeta-Learning: {result.learning_insights}",
            "confidence": 0.88,
        }


class OptimizationAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.optimizer = dspy.ChainOfThought(OptimizationSignature)

    def forward(self, task: str, current_context: str, guidance: str) -> dict:
        result = self.optimizer(task=task, current_context=current_context, guidance=guidance)
        return {
            "agent_name": "OptimizationAgent",
            "content": f"{result.optimization_strategies}\n\nEfficiency: {result.efficiency_improvements}",
            "confidence": 0.80,
        }


class CreativeAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.creator = dspy.ChainOfThought(CreativeSignature)

    def forward(self, task: str, current_context: str, guidance: str) -> dict:
        result = self.creator(task=task, current_context=current_context, guidance=guidance)
        return {
            "agent_name": "CreativeAgent",
            "content": f"{result.creative_solutions}\n\nIdeation: {result.ideation_notes}",
            "confidence": 0.75,
        }


class DocumentRefiner(dspy.Module):
    def __init__(self):
        super().__init__()
        self.refiner = dspy.ChainOfThought(RefineDocumentSignature)

    def forward(
        self,
        task: str,
        current_draft: str,
        agent_contributions: str,
        feedback: str,
        intensity: str = "Standard",
    ) -> str:
        result = self.refiner(
            task=task,
            current_draft=current_draft,
            agent_contributions=agent_contributions,
            feedback=feedback,
            intensity=intensity,
        )
        return result.refined_document


class DocumentJudge(dspy.Module):
    def __init__(self):
        super().__init__()
        self.judge = dspy.Predict(JudgeDocumentSignature)

    def forward(self, task: str, document: str) -> dict:
        result = self.judge(task=task, document=document)
        return {
            "clarity": float(result.clarity_score) if result.clarity_score else 5.0,
            "completeness": float(result.completeness_score) if result.completeness_score else 5.0,
            "coherence": float(result.coherence_score) if result.coherence_score else 5.0,
            "innovation": float(result.innovation_score) if result.innovation_score else 5.0,
            "overall_score": float(result.overall_score) if result.overall_score else 5.0,
            "feedback": result.feedback or "No feedback provided",
            "strengths": [s.strip() for s in (result.strengths or "").split(",") if s.strip()],
            "improvements": [
                s.strip() for s in (result.improvements or "").split(",") if s.strip()
            ],
        }


class DiagramGenerator(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generator = dspy.Predict(GenerateDiagramSignature)

    def forward(self, document: str) -> dict:
        result = self.generator(document=document)
        return {
            "diagram_type": result.diagram_type or "flowchart",
            "code": result.mermaid_code or "graph TD\n  A[Start] --> B[End]",
        }


class WebResearchAgent(dspy.Module):
    def __init__(self):
        super().__init__()
        self.planner = dspy.ChainOfThought(WebResearchSignature)
        self.synthesizer = dspy.ChainOfThought(WebSynthesisSignature)

    def forward(self, task: str, current_context: str, guidance: str) -> dict:
        from src.web_search import WebSearchAgent

        plan = self.planner(task=task, current_context=current_context, guidance=guidance)

        queries = [q.strip() for q in plan.search_queries.split(",") if q.strip()][:3]

        if not queries:
            queries = [task[:100]]

        all_results = []
        search_agent = WebSearchAgent(max_results=3)

        for query in queries:
            try:
                response = asyncio.get_event_loop().run_until_complete(search_agent.search(query))
                if response.results:
                    for result in response.results:
                        all_results.append(
                            f"Source: {result.url}\nTitle: {result.title}\n{result.snippet}"
                        )
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    response = loop.run_until_complete(search_agent.search(query))
                    if response.results:
                        for result in response.results:
                            all_results.append(
                                f"Source: {result.url}\nTitle: {result.title}\n{result.snippet}"
                            )
                finally:
                    loop.close()
            except Exception:
                pass

        if not all_results:
            return {
                "agent_name": "WebResearchAgent",
                "content": f"Research Focus: {plan.research_focus}\n\nNo web results found for queries: {queries}",
                "confidence": 0.3,
            }

        search_results_text = "\n\n---\n\n".join(all_results[:10])

        synthesis = self.synthesizer(
            task=task, search_results=search_results_text, guidance=guidance
        )

        return {
            "agent_name": "WebResearchAgent",
            "content": f"{synthesis.synthesized_findings}\n\nKey Sources:\n{synthesis.key_sources}\n\nConfidence: {synthesis.confidence_assessment}",
            "confidence": 0.85,
            "sources_count": len(all_results),
        }


AGENT_REGISTRY = {
    "data_processing": DataProcessingAgent,
    "analysis": AnalysisAgent,
    "experimental": ExperimentalAgent,
    "learning": LearningAgent,
    "optimization": OptimizationAgent,
    "creative": CreativeAgent,
    "web_research": WebResearchAgent,
}


def get_agent(agent_type: str) -> Optional[dspy.Module]:
    agent_class = AGENT_REGISTRY.get(agent_type)
    if agent_class:
        return agent_class()
    return None

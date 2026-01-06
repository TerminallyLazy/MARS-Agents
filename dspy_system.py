import dspy
import os
from pydantic import BaseModel, Field
from typing import List, Literal
from dotenv import load_dotenv

load_dotenv()

# --- Signatures ---


class ScoreCard(BaseModel):
    clarity: float = Field(description="Score for clarity (0-10)")
    completeness: float = Field(description="Score for completeness (0-10)")
    overall_score: float = Field(description="Overall quality score (0-10)")
    feedback: str = Field(description="Detailed feedback for improvement")


class MermaidDiagram(BaseModel):
    diagram_type: str = Field(description="Type of diagram")
    code: str = Field(description="Mermaid.js code")


class RefineAgentsMD(dspy.Signature):
    """Refine the AGENTS.md content based on feedback."""

    task = dspy.InputField()
    current_draft = dspy.InputField()
    feedback = dspy.InputField()
    intensity = dspy.InputField(desc="High or Standard")
    refined_draft = dspy.OutputField(desc="The updated AGENTS.md content")


class JudgeAgentsMD(dspy.Signature):
    """Evaluate the AGENTS.md draft and provide a score card."""

    task = dspy.InputField()
    draft = dspy.InputField()
    score_card = dspy.OutputField(desc="Structured score card")


class CreateDiagram(dspy.Signature):
    """Generate a Mermaid.js diagram for the agent system."""

    draft = dspy.InputField()
    diagram = dspy.OutputField(desc="Structured Mermaid diagram")


# --- Modules ---


class MultiAgentSystem(dspy.Module):
    def __init__(self):
        super().__init__()
        self.refiner = dspy.TypedPredictor(RefineAgentsMD)
        self.judge = dspy.TypedPredictor(JudgeAgentsMD)
        self.diagrammer = dspy.TypedPredictor(CreateDiagram)

    def forward(self, task):
        draft = "Initial draft placeholder"
        feedback = "None"
        scores = []
        iterations = 0
        is_boosted = False

        while iterations < 5:
            iterations += 1
            intensity = "High" if is_boosted else "Standard"

            # Refine
            res = self.refiner(
                task=task, current_draft=draft, feedback=feedback, intensity=intensity
            )
            draft = res.refined_draft

            # Judge
            judgement = self.judge(task=task, draft=draft)
            score_card = judgement.score_card
            scores.append(score_card.overall_score)
            feedback = score_card.feedback

            print(f"Iteration {iterations}: Score {score_card.overall_score}")

            # Reward Logic / Recursive Boost
            if score_card.overall_score >= 8.5:
                break

            delta = scores[-1] - scores[-2] if len(scores) > 1 else 0
            if delta < 0.5 and score_card.overall_score < 8.0:
                print("!!! DSPy RECURSIVE BOOST !!!")
                is_boosted = True
            else:
                is_boosted = False

        # Final Diagram
        diag_res = self.diagrammer(draft=draft)
        return draft, diag_res.diagram


if __name__ == "__main__":
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not set.")
    else:
        lm = dspy.LM(model="openai/gpt-4o", api_key=api_key)
        dspy.configure(lm=lm)

        system = MultiAgentSystem()
        final_draft, final_diagram = system.forward(
            "Create an AGENTS.md for a multi-agent research system."
        )
        print("\nFINAL AGENTS.MD:\n", final_draft)
        print("\nDIAGRAM:\n", final_diagram.code)

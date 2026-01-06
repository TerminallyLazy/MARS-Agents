import os
import operator
from typing import Annotated, List, TypedDict, Union, Literal
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

load_dotenv()

# --- Data Models ---

class ScoreCard(BaseModel):
    clarity: float = Field(description="Score for clarity (0-10)")
    completeness: float = Field(description="Score for completeness (0-10)")
    overall_score: float = Field(description="Overall quality score (0-10)")
    feedback: str = Field(description="Detailed feedback for improvement")

class MermaidDiagram(BaseModel):
    diagram_type: str = Field(description="Type of diagram (e.g., flowchart, sequence)")
    code: str = Field(description="Mermaid.js code")

class Orchestration(BaseModel):
    next_action: Literal["refiner", "diagrammer", "finalize"] = Field(description="The next node to execute")
    instructions: str = Field(description="Instructions for the next agent")

# --- State Definition ---

class AgentState(TypedDict):
    task: str
    draft: str
    feedback_history: Annotated[List[str], operator.add]
    scores: Annotated[List[float], operator.add]
    diagram: str
    is_boosted: bool
    iterations: int

# --- Nodes ---

# Use environment variable for API key
llm = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))

def orchestrator(state: AgentState):
    print("--- ORCHESTRATOR ---")
    structured_llm = llm.with_structured_output(Orchestration)
    prompt = f"Task: {state['task']}\nDraft: {state['draft']}\nFeedback: {state['feedback_history'][-1] if state['feedback_history'] else 'None'}\nDecide the next step."
    res = structured_llm.invoke(prompt)
    return {"iterations": state.get("iterations", 0) + 1, "is_boosted": False}

def refiner(state: AgentState):
    print(f"--- REFINER (Boosted: {state.get('is_boosted', False)}) ---")
    intensity = "HIGH INTENSITY RECURSIVE IMPROVEMENT" if state.get("is_boosted") else "Standard refinement"
    prompt = f"Task: {state['task']}\nDraft: {state['draft']}\nFeedback: {state['feedback_history'][-1] if state['feedback_history'] else 'None'}\nMode: {intensity}\nUpdate the AGENTS.md content."
    res = llm.invoke(prompt)
    return {"draft": res.content}

def judge(state: AgentState):
    print("--- JUDGE ---")
    structured_llm = llm.with_structured_output(ScoreCard)
    prompt = f"Evaluate this AGENTS.md draft:\n{state['draft']}\nTask: {state['task']}"
    res = structured_llm.invoke(prompt)
    return {"scores": [res.overall_score], "feedback_history": [res.feedback]}

def diagrammer(state: AgentState):
    print("--- DIAGRAMMER ---")
    structured_llm = llm.with_structured_output(MermaidDiagram)
    prompt = f"Create a Mermaid diagram for this agent system:\n{state['draft']}"
    res = structured_llm.invoke(prompt)
    return {"diagram": res.code}

def reward_agent(state: AgentState):
    print("--- REWARD AGENT ---")
    scores = state.get("scores", [])
    current_score = scores[-1] if scores else 0
    delta = scores[-1] - scores[-2] if len(scores) > 1 else 0
    
    print(f"Current Score: {current_score}, Delta: {delta}")

    if current_score >= 8.5 or state["iterations"] >= 5:
        return "finalize"
    elif delta < 0.5 and current_score < 8.0:
        print("!!! TRIGGERING RECURSIVE BOOST !!!")
        return "boost"
    else:
        return "continue"

# --- Graph Construction ---

workflow = StateGraph(AgentState)

workflow.add_node("orchestrator", orchestrator)
workflow.add_node("refiner", refiner)
workflow.add_node("judge", judge)
workflow.add_node("diagrammer", diagrammer)

workflow.set_entry_point("orchestrator")

workflow.add_conditional_edges(
    "orchestrator",
    lambda x: "refiner",
    {"refiner": "refiner"}
)

workflow.add_edge("refiner", "judge")
workflow.add_edge("judge", "diagrammer")

workflow.add_conditional_edges(
    "diagrammer",
    reward_agent,
    {
        "finalize": END,
        "boost": "refiner",
        "continue": "orchestrator"
    }
)

def run_langgraph(task: str):
    app = workflow.compile()
    initial_state = {
        "task": task,
        "draft": "",
        "feedback_history": [],
        "scores": [],
        "diagram": "",
        "is_boosted": False,
        "iterations": 0
    }
    final_state = app.invoke(initial_state)
    return final_state

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not set.")
    else:
        result = run_langgraph("Create an AGENTS.md for a multi-agent research system.")
        print("\nFINAL AGENTS.MD:\n", result['draft'])
        print("\nDIAGRAM:\n", result['diagram'])

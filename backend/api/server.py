import asyncio
import json
import os
from datetime import datetime
from typing import AsyncGenerator

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

load_dotenv()

# Lazy import google.genai to avoid startup errors if not installed
_genai_client = None


def get_genai_client():
    global _genai_client
    if _genai_client is None:
        try:
            from google import genai

            _genai_client = genai.Client()
        except ImportError:
            raise HTTPException(
                status_code=500,
                detail="google-genai package not installed. Run: pip install google-genai",
            )
    return _genai_client


app = FastAPI(
    title="MARS Agent API",
    description="Multi-Agent Research System API with SSE streaming",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RunRequest(BaseModel):
    task: str
    max_iterations: int = 7


class GraphSchema(BaseModel):
    nodes: list[str]
    edges: list[tuple[str, str]]
    entry: str
    end: str


GRAPH_NODES = [
    "entry",
    "specialist_agent",
    "refiner",
    "critique",
    "judge",
    "reflection",
    "consensus",
    "meta_learning",
    "memory_evolution",
    "loop_decision",
    "self_healing",
    "diagram",
]

GRAPH_EDGES = [
    ("entry", "specialist_agent"),
    ("specialist_agent", "refiner"),
    ("refiner", "critique"),
    ("critique", "judge"),
    ("judge", "reflection"),
    ("reflection", "consensus"),
    ("consensus", "meta_learning"),
    ("meta_learning", "memory_evolution"),
    ("memory_evolution", "loop_decision"),
    ("memory_evolution", "diagram"),
    ("loop_decision", "specialist_agent"),
    ("loop_decision", "self_healing"),
    ("self_healing", "specialist_agent"),
]


def format_sse_event(event_type: str, data: dict) -> str:
    payload = json.dumps(
        {"event": event_type, "data": data, "timestamp": datetime.now().isoformat()}
    )
    return f"data: {payload}\n\n"


async def stream_agent_execution(task: str, max_iterations: int) -> AsyncGenerator[str, None]:
    try:
        from src.graph import graph
        from src.state import create_initial_state

        initial_state = create_initial_state(task)

        yield format_sse_event("run_start", {"task": task, "max_iterations": max_iterations})

        async for event in graph.astream_events(
            initial_state, {"recursion_limit": 150}, version="v2"
        ):
            event_name = event.get("event", "unknown")
            event_data = {
                "name": event.get("name", ""),
                "run_id": event.get("run_id", ""),
                "tags": event.get("tags", []),
            }

            if event_name == "on_chain_start":
                event_data["metadata"] = event.get("metadata", {})
                yield format_sse_event("node_start", event_data)

            elif event_name == "on_chain_end":
                output = event.get("data", {}).get("output", {})
                event_data["output"] = _sanitize_output(output)
                yield format_sse_event("node_end", event_data)

            elif event_name == "on_chat_model_stream":
                chunk = event.get("data", {}).get("chunk", {})
                content = chunk.content if hasattr(chunk, "content") else str(chunk)
                if content:
                    yield format_sse_event("token", {"content": content})

            elif event_name == "on_custom_event":
                custom_name = event.get("name", "")
                custom_data = event.get("data", {})
                yield format_sse_event(f"custom_{custom_name}", custom_data)

        yield format_sse_event("run_end", {"status": "completed"})

    except Exception as e:
        yield format_sse_event("error", {"message": str(e), "type": type(e).__name__})


def _sanitize_output(output: dict) -> dict:
    sanitized = {}
    for key, value in output.items() if isinstance(output, dict) else []:
        if key in ("scores", "iteration", "current_draft", "diagram", "feedback_history"):
            if key == "current_draft" and isinstance(value, str) and len(value) > 2000:
                sanitized[key] = value[:2000] + "... [truncated]"
            else:
                sanitized[key] = value
        elif key == "reflection_memories" and isinstance(value, list):
            sanitized[key] = [
                {
                    "iteration": m.iteration if hasattr(m, "iteration") else None,
                    "score": m.score if hasattr(m, "score") else None,
                    "improvement_suggestion": (
                        m.improvement_suggestion[:500]
                        if hasattr(m, "improvement_suggestion")
                        else None
                    ),
                }
                for m in value[-3:]
            ]
    return sanitized


@app.get("/")
async def root():
    return {"name": "MARS Agent API", "version": "1.0.0", "status": "healthy"}


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")),
    }


@app.post("/api/runs/stream")
async def stream_run(request: RunRequest):
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")

    return StreamingResponse(
        stream_agent_execution(request.task, request.max_iterations),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


async def stream_gemini_research(task: str) -> AsyncGenerator[str, None]:
    try:
        client = get_genai_client()

        yield format_sse_event("run_start", {"task": task, "backend": "gemini"})
        yield format_sse_event("progress", {"message": "Starting Gemini Deep Research..."})

        stream = client.interactions.create(
            input=task,
            agent="deep-research-pro-preview-12-2025",
            background=True,
            stream=True,
            agent_config={"type": "deep-research", "thinking_summaries": "auto"},
        )

        interaction_id = None
        current_draft = ""

        for chunk in stream:
            if chunk.event_type == "interaction.start":
                interaction_id = chunk.interaction.id
                yield format_sse_event(
                    "progress", {"message": f"Research initiated: {interaction_id}"}
                )

            elif chunk.event_type == "content.delta":
                if hasattr(chunk, "delta"):
                    if chunk.delta.type == "text":
                        text = chunk.delta.text
                        current_draft += text
                        yield format_sse_event("token", {"content": text})
                        yield format_sse_event("draft_update", {"content": current_draft})
                    elif chunk.delta.type == "thought_summary":
                        thought_text = (
                            chunk.delta.content.text
                            if hasattr(chunk.delta.content, "text")
                            else str(chunk.delta.content)
                        )
                        yield format_sse_event("thought", {"content": thought_text})

            elif chunk.event_type == "interaction.complete":
                yield format_sse_event("run_end", {"status": "completed"})
                break

            elif chunk.event_type == "error":
                error_msg = str(chunk.error) if hasattr(chunk, "error") else "Unknown error"
                yield format_sse_event("error", {"message": error_msg})
                break

    except HTTPException:
        raise
    except Exception as e:
        yield format_sse_event("error", {"message": str(e), "type": type(e).__name__})


@app.post("/api/research/gemini/stream")
async def stream_gemini_run(request: RunRequest):
    if not (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")):
        raise HTTPException(
            status_code=500, detail="GEMINI_API_KEY or GOOGLE_API_KEY not configured"
        )

    return StreamingResponse(
        stream_gemini_research(request.task),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/graph/schema")
async def get_graph_schema() -> GraphSchema:
    return GraphSchema(
        nodes=GRAPH_NODES,
        edges=GRAPH_EDGES,
        entry="entry",
        end="diagram",
    )


@app.get("/api/graph/nodes")
async def get_graph_nodes():
    return {
        "nodes": [
            {"id": "entry", "label": "Entry", "description": "Initialize state and memory"},
            {
                "id": "specialist_agent",
                "label": "Specialists",
                "description": "6 parallel specialist agents",
            },
            {"id": "refiner", "label": "Refiner", "description": "Synthesize specialist outputs"},
            {"id": "critique", "label": "Critique", "description": "Constitutional AI review"},
            {"id": "judge", "label": "Judge", "description": "Score and provide feedback"},
            {
                "id": "reflection",
                "label": "Reflection",
                "description": "Extract learnings (Reflexion)",
            },
            {"id": "consensus", "label": "Consensus", "description": "Multi-role debate voting"},
            {
                "id": "meta_learning",
                "label": "Meta Learning",
                "description": "Adapt strategy weights",
            },
            {
                "id": "memory_evolution",
                "label": "Memory Evolution",
                "description": "Evolve memory structure",
            },
            {
                "id": "loop_decision",
                "label": "Loop Decision",
                "description": "Continue or finalize",
            },
            {"id": "self_healing", "label": "Self Healing", "description": "Recover failed agents"},
            {"id": "diagram", "label": "Diagram", "description": "Generate final output"},
        ]
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

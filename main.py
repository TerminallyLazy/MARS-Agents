import os
from dotenv import load_dotenv
from src.graph import run_multi_agent_system

load_dotenv()


def main():
    task = "Create an AGENTS.md for a multi-agent research system with recursive self-improvement."

    print("=== RUNNING LANGGRAPH + DSPY MULTI-AGENT SYSTEM ===")

    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not set")
        return

    result = run_multi_agent_system(task)

    with open("AGENTS_output.md", "w") as f:
        f.write(result["document"])

    with open("diagram.mmd", "w") as f:
        f.write(result["diagram"])

    print(f"\nCompleted in {result['iterations']} iterations")
    print(f"Score progression: {' -> '.join(f'{s:.1f}' for s in result['scores'])}")
    print("\nFiles generated: AGENTS_output.md, diagram.mmd")


if __name__ == "__main__":
    main()

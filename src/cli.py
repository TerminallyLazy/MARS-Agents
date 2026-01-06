import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Multi-Agent Research System - LangGraph + DSPy"
    )
    parser.add_argument(
        "task",
        nargs="?",
        default=None,
        help="Task description for the multi-agent system",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="AGENTS_output.md",
        help="Output file path for the generated document",
    )
    parser.add_argument(
        "--diagram-output",
        "-d",
        type=str,
        default="diagram.mmd",
        help="Output file path for the Mermaid diagram",
    )
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Run in interactive mode"
    )
    parser.add_argument(
        "--max-iterations", type=int, default=5, help="Maximum refinement iterations"
    )

    args = parser.parse_args()

    from src.graph import run_multi_agent_system

    if args.interactive:
        print("Multi-Agent Research System")
        print("=" * 40)
        print("Enter your task (or 'quit' to exit):\n")

        while True:
            try:
                task = input("> ").strip()
                if task.lower() in ("quit", "exit", "q"):
                    print("Goodbye!")
                    break
                if not task:
                    continue

                print(f"\nProcessing: {task}\n")
                result = run_multi_agent_system(task)

                print("\n" + "=" * 60)
                print("GENERATED DOCUMENT:")
                print("=" * 60)
                print(
                    result["document"][:2000] + "..."
                    if len(result["document"]) > 2000
                    else result["document"]
                )
                print(f"\nCompleted in {result['iterations']} iterations")
                print(
                    f"Final score: {result['scores'][-1] if result['scores'] else 'N/A'}"
                )
                print("\nEnter another task or 'quit' to exit:\n")

            except KeyboardInterrupt:
                print("\n\nInterrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}\n")
    else:
        if not args.task:
            print("Error: Please provide a task or use --interactive mode")
            print("Usage: python -m src.cli 'Your task description'")
            print("       python -m src.cli --interactive")
            sys.exit(1)

        print(f"Task: {args.task}")
        print("Processing...\n")

        result = run_multi_agent_system(args.task)

        output_path = Path(args.output)
        output_path.write_text(result["document"])
        print(f"Document saved to: {output_path}")

        diagram_path = Path(args.diagram_output)
        diagram_path.write_text(result["diagram"])
        print(f"Diagram saved to: {diagram_path}")

        print(f"\nCompleted in {result['iterations']} iterations")
        print(f"Score progression: {' -> '.join(f'{s:.1f}' for s in result['scores'])}")
        print(f"Final score: {result['scores'][-1] if result['scores'] else 'N/A'}")


if __name__ == "__main__":
    main()

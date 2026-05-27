import argparse
import json
from pathlib import Path

from cograster.io import load_json
from cograster.llm import generate_workflow_with_ollama
from cograster.verifier import verify


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a workflow with Ollama and verify it."
    )
    parser.add_argument("--task", required=True, help="Path to public task JSON")
    parser.add_argument("--model", default="llama3.2", help="Ollama model name")
    parser.add_argument(
        "--mode",
        default="guided",
        choices=["naive", "minimal", "guided"],
        help="Prompt mode.",
    )
    parser.add_argument(
        "--answer-key",
        default=None,
        help="Optional path to answer key JSON. If omitted, it is inferred from task path.",
    )

    args = parser.parse_args()

    public_task = load_json(args.task)
    answer_key = load_json(args.answer_key or infer_answer_key_path(args.task))

    print("Generating workflow with LLM...")
    print(f"Mode: {args.mode}")

    workflow = generate_workflow_with_ollama(
        public_task,
        model=args.model,
        mode=args.mode,
    )

    print()
    print("Generated workflow:")
    print(json.dumps(workflow, ensure_ascii=False, indent=2))

    print()
    print("Verification:")
    report = verify(answer_key, workflow)

    print(f"Passed: {str(report.passed).lower()}")
    print(f"Cognitive Error Rate: {report.cognitive_error_rate:.3f}")

    if report.errors:
        print()
        print("Errors:")
        for error in report.errors:
            layer = f" layer={error.layer}" if error.layer else ""
            print(f"- {error.error_type}{layer}: {error.message}")
    else:
        print()
        print("No cognitive-spatial errors detected.")


def infer_answer_key_path(public_task_path: str) -> str:
    path = Path(public_task_path)

    parts = list(path.parts)

    try:
        index = parts.index("public_tasks")
    except ValueError as exc:
        raise ValueError(
            "Could not infer answer key path. "
            "Expected task path to contain 'benchmark/public_tasks/...'. "
            "Pass --answer-key explicitly."
        ) from exc

    parts[index] = "answer_keys"

    filename = Path(parts[-1])
    parts[-1] = filename.name.replace(".json", "_key.json")

    return str(Path(*parts))


if __name__ == "__main__":
    main()
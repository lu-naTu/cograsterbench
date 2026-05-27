import argparse
import json

from cograster.io import load_json
from cograster.verifier import verify


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify a raster-algebra workflow against a CogRasterBench task."
    )
    parser.add_argument("--task", required=True, help="Path to task JSON")
    parser.add_argument("--workflow", required=True, help="Path to workflow JSON")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print report as JSON instead of text",
    )

    args = parser.parse_args()

    task = load_json(args.task)
    workflow = load_json(args.workflow)

    report = verify(task, workflow)

    if args.json:
        print(_report_to_json(report))
    else:
        print(_report_to_text(report))


def _report_to_json(report) -> str:
    data = {
        "task_id": report.task_id,
        "workflow_id": report.workflow_id,
        "passed": report.passed,
        "cognitive_error_rate": report.cognitive_error_rate,
        "errors": [
            {
                "error_type": error.error_type,
                "layer": error.layer,
                "message": error.message,
                "expected": error.expected,
                "actual": error.actual,
            }
            for error in report.errors
        ],
    }

    return json.dumps(data, ensure_ascii=False, indent=2)


def _report_to_text(report) -> str:
    lines = [
        f"Task: {report.task_id}",
        f"Workflow: {report.workflow_id}",
        f"Passed: {str(report.passed).lower()}",
        f"Cognitive Error Rate: {report.cognitive_error_rate:.3f}",
    ]

    if not report.errors:
        lines.append("")
        lines.append("No cognitive-spatial errors detected.")
        return "\n".join(lines)

    lines.append("")
    lines.append("Detected cognitive-spatial errors:")

    for error in report.errors:
        layer = f" layer={error.layer}" if error.layer else ""
        lines.append(f"- {error.error_type}{layer}: {error.message}")

    return "\n".join(lines)


if __name__ == "__main__":
    main()

import json
from pathlib import Path

from cograster.io import load_json
from cograster.llm import generate_workflow_with_ollama
from cograster.verifier import verify


TASKS = [
    (
        "flood_001",
        "benchmark/public_tasks/flood/flood_001.json",
        "benchmark/answer_keys/flood/flood_001_key.json",
    ),
    (
        "flood_002",
        "benchmark/public_tasks/flood/flood_002.json",
        "benchmark/answer_keys/flood/flood_002_key.json",
    ),
    (
        "solar_001",
        "benchmark/public_tasks/solar/solar_001.json",
        "benchmark/answer_keys/solar/solar_001_key.json",
    ),
    (
        "solar_002",
        "benchmark/public_tasks/solar/solar_002.json",
        "benchmark/answer_keys/solar/solar_002_key.json",
    ),
    (
        "ndvi_001",
        "benchmark/public_tasks/spectral/ndvi_001.json",
        "benchmark/answer_keys/spectral/ndvi_001_key.json",
    ),
    (
        "ndwi_001",
        "benchmark/public_tasks/spectral/ndwi_001.json",
        "benchmark/answer_keys/spectral/ndwi_001_key.json",
    ),
        (
        "flood_003",
        "benchmark/public_tasks/flood/flood_003.json",
        "benchmark/answer_keys/flood/flood_003_key.json",
    ),
    (
        "flood_004",
        "benchmark/public_tasks/flood/flood_004.json",
        "benchmark/answer_keys/flood/flood_004_key.json",
    ),
    (
        "solar_003",
        "benchmark/public_tasks/solar/solar_003.json",
        "benchmark/answer_keys/solar/solar_003_key.json",
    ),
    (
        "solar_004",
        "benchmark/public_tasks/solar/solar_004.json",
        "benchmark/answer_keys/solar/solar_004_key.json",
    ),
    (
        "ndvi_002",
        "benchmark/public_tasks/spectral/ndvi_002.json",
        "benchmark/answer_keys/spectral/ndvi_002_key.json",
    ),
    (
        "ndwi_002",
        "benchmark/public_tasks/spectral/ndwi_002.json",
        "benchmark/answer_keys/spectral/ndwi_002_key.json",
    ),
]


MODES = ["naive", "minimal", "guided"]


def main() -> None:
    print("CogRasterAgent LLM Benchmark")
    print("============================")
    print()

    runs_dir = Path("runs/llm_benchmark")
    runs_dir.mkdir(parents=True, exist_ok=True)

    results = []

    for task_id, public_task_path, answer_key_path in TASKS:
        public_task = load_json(public_task_path)
        answer_key = load_json(answer_key_path)

        row = {
            "task_id": task_id,
        }

        for mode in MODES:
            print(f"Running {task_id} in {mode} mode...")

            workflow = generate_workflow_with_ollama(
                public_task,
                mode=mode,
            )

            report = verify(answer_key, workflow)

            row[mode] = report.passed
            row[f"{mode}_errors"] = len(report.errors)

            save_run_result(
                runs_dir=runs_dir,
                task_id=task_id,
                mode=mode,
                workflow=workflow,
                report=report,
            )

        results.append(row)
        print()

    print_results(results)


def save_run_result(
    runs_dir: Path,
    task_id: str,
    mode: str,
    workflow: dict,
    report,
) -> None:
    mode_dir = runs_dir / mode
    mode_dir.mkdir(parents=True, exist_ok=True)

    workflow_path = mode_dir / f"{task_id}_workflow.json"
    report_path = mode_dir / f"{task_id}_report.json"

    workflow_path.write_text(
        json.dumps(workflow, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    report_data = {
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

    report_path.write_text(
        json.dumps(report_data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def print_results(results: list[dict]) -> None:
    print("Results")
    print("=======")
    print()

    print(
        f"{'Task':<12} "
        f"{'Naive':<8} {'NaiveErr':<10} "
        f"{'Minimal':<8} {'MinimalErr':<10} "
        f"{'Guided':<8} {'GuidedErr':<10}"
    )
    print("-" * 78)

    for row in results:
        print(
            f"{row['task_id']:<12} "
            f"{str(row['naive']):<8} {row['naive_errors']:<10} "
            f"{str(row['minimal']):<8} {row['minimal_errors']:<10} "
            f"{str(row['guided']):<8} {row['guided_errors']:<10}"
        )

    print()

    for mode in MODES:
        passed = sum(1 for row in results if row[mode])
        print(f"{mode.capitalize()} passed: {passed} / {len(results)}")


if __name__ == "__main__":
    main()
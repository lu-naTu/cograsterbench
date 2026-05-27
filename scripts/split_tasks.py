import json
from pathlib import Path


TASK_DIRS = [
    Path("benchmark/tasks/flood"),
    Path("benchmark/tasks/solar"),
    Path("benchmark/tasks/spectral"),
]


def main() -> None:
    for task_dir in TASK_DIRS:
        domain_name = task_dir.name

        public_dir = Path("benchmark/public_tasks") / domain_name
        key_dir = Path("benchmark/answer_keys") / domain_name

        public_dir.mkdir(parents=True, exist_ok=True)
        key_dir.mkdir(parents=True, exist_ok=True)

        for task_path in task_dir.glob("*.json"):
            task = load_json(task_path)

            public_task = {
                "task_id": task["task_id"],
                "domain": task["domain"],
                "user_query": task["user_query"],
                "available_layers": extract_available_layers(task),
            }

            answer_key = {
                "task_id": task["task_id"],
                "error_traps": task.get("error_traps", []),
                "expected_operations": task.get("expected_operations", []),
                "forbidden_operations": task.get("forbidden_operations", []),
                "required_checks": task.get("required_checks", []),
            }

            if "expected_formula" in task:
                answer_key["expected_formula"] = task["expected_formula"]

            public_path = public_dir / task_path.name
            key_path = key_dir / task_path.name.replace(".json", "_key.json")

            save_json(public_path, public_task)
            save_json(key_path, answer_key)

            print(f"Created {public_path}")
            print(f"Created {key_path}")


def extract_available_layers(task: dict) -> list[str]:
    layers = []

    for item in task.get("expected_operations", []):
        layer = item.get("layer")
        if layer and layer not in layers:
            layers.append(layer)

    return layers


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
from pathlib import Path

from cograster.io import load_json
from cograster.verifier import verify


BENCHMARK_PAIRS = [
    (
        "flood_001",
        "benchmark/tasks/flood/flood_001.json",
        "benchmark/workflows/good/flood_001_good.json",
        "benchmark/workflows/bad/flood_001_bad.json",
    ),
    (
        "flood_002",
        "benchmark/tasks/flood/flood_002.json",
        "benchmark/workflows/good/flood_002_good.json",
        "benchmark/workflows/bad/flood_002_bad.json",
    ),
    (
        "solar_001",
        "benchmark/tasks/solar/solar_001.json",
        "benchmark/workflows/good/solar_001_good.json",
        "benchmark/workflows/bad/solar_001_bad.json",
    ),
    (
        "solar_002",
        "benchmark/tasks/solar/solar_002.json",
        "benchmark/workflows/good/solar_002_good.json",
        "benchmark/workflows/bad/solar_002_bad.json",
    ),
    (
        "ndvi_001",
        "benchmark/tasks/spectral/ndvi_001.json",
        "benchmark/workflows/good/ndvi_001_good.json",
        "benchmark/workflows/bad/ndvi_001_bad.json",
    ),
    (
        "ndwi_001",
        "benchmark/tasks/spectral/ndwi_001.json",
        "benchmark/workflows/good/ndwi_001_good.json",
        "benchmark/workflows/bad/ndwi_001_bad.json",
    ),
]


def main() -> None:
    print("CogRasterBench MVP")
    print("===================")
    print()

    all_ok = True

    for task_id, task_path, good_path, bad_path in BENCHMARK_PAIRS:
        task = load_json(task_path)

        good_workflow = load_json(good_path)
        bad_workflow = load_json(bad_path)

        good_report = verify(task, good_workflow)
        bad_report = verify(task, bad_workflow)

        good_ok = good_report.passed is True
        bad_ok = bad_report.passed is False

        if not good_ok or not bad_ok:
            all_ok = False

        print(f"Task: {task_id}")
        print(f"  good workflow passed: {good_ok}")
        print(f"  bad workflow failed:  {bad_ok}")
        print(f"  bad workflow errors:  {len(bad_report.errors)}")
        for error in bad_report.errors:
            print(f"    - {error.error_type}: {error.message}")

    if all_ok:
        print("Benchmark status: OK")
    else:
        print("Benchmark status: FAILED")


if __name__ == "__main__":
    main()
from cograster.io import load_json
from cograster.verifier import verify


TASK_WORKFLOW_PAIRS = [
    ("benchmark/tasks/flood/flood_001.json", "benchmark/workflows/good/flood_001_good.json", True),
    ("benchmark/tasks/flood/flood_001.json", "benchmark/workflows/bad/flood_001_bad.json", False),
    ("benchmark/tasks/flood/flood_002.json", "benchmark/workflows/good/flood_002_good.json", True),
    ("benchmark/tasks/flood/flood_002.json", "benchmark/workflows/bad/flood_002_bad.json", False),
    ("benchmark/tasks/solar/solar_001.json", "benchmark/workflows/good/solar_001_good.json", True),
    ("benchmark/tasks/solar/solar_001.json", "benchmark/workflows/bad/solar_001_bad.json", False),
    ("benchmark/tasks/solar/solar_002.json", "benchmark/workflows/good/solar_002_good.json", True),
    ("benchmark/tasks/solar/solar_002.json", "benchmark/workflows/bad/solar_002_bad.json", False),
    ("benchmark/tasks/spectral/ndvi_001.json", "benchmark/workflows/good/ndvi_001_good.json", True),
    ("benchmark/tasks/spectral/ndvi_001.json", "benchmark/workflows/bad/ndvi_001_bad.json", False),
    ("benchmark/tasks/spectral/ndwi_001.json", "benchmark/workflows/good/ndwi_001_good.json", True),
    ("benchmark/tasks/spectral/ndwi_001.json", "benchmark/workflows/bad/ndwi_001_bad.json", False),
]


def test_all_good_and_bad_workflows():
    for task_path, workflow_path, expected_passed in TASK_WORKFLOW_PAIRS:
        task = load_json(task_path)
        workflow = load_json(workflow_path)

        report = verify(task, workflow)

        assert report.passed is expected_passed, (
            f"Unexpected result for task={task_path}, workflow={workflow_path}: "
            f"errors={[error.error_type for error in report.errors]}"
        )


def test_bad_flood_001_detects_expected_error_types():
    task = load_json("benchmark/tasks/flood/flood_001.json")
    workflow = load_json("benchmark/workflows/bad/flood_001_bad.json")

    report = verify(task, workflow)
    error_types = {error.error_type for error in report.errors}

    assert "E1_factor_direction_error" in error_types
    assert "E5_categorical_continuous_confusion" in error_types
    assert "E2_grid_alignment_error" in error_types
    assert "E4_nodata_semantic_error" in error_types


def test_bad_flood_002_detects_constraint_and_unit_errors():
    task = load_json("benchmark/tasks/flood/flood_002.json")
    workflow = load_json("benchmark/workflows/bad/flood_002_bad.json")

    report = verify(task, workflow)
    error_types = {error.error_type for error in report.errors}

    assert "E1_factor_direction_error" in error_types
    assert "E6_constraint_factor_confusion" in error_types
    assert "E2_grid_alignment_error" in error_types
    assert "E3_unit_confusion" in error_types
    assert "E4_nodata_semantic_error" in error_types


def test_bad_solar_002_detects_cloud_mask_error():
    task = load_json("benchmark/tasks/solar/solar_002.json")
    workflow = load_json("benchmark/workflows/bad/solar_002_bad.json")

    report = verify(task, workflow)
    error_types = {error.error_type for error in report.errors}

    assert "E6_constraint_factor_confusion" in error_types
    assert "E5_categorical_continuous_confusion" in error_types
    assert "E1_factor_direction_error" in error_types


def test_bad_spectral_tasks_detect_formula_errors():
    for task_path, workflow_path in [
        ("benchmark/tasks/spectral/ndvi_001.json", "benchmark/workflows/bad/ndvi_001_bad.json"),
        ("benchmark/tasks/spectral/ndwi_001.json", "benchmark/workflows/bad/ndwi_001_bad.json"),
    ]:
        task = load_json(task_path)
        workflow = load_json(workflow_path)

        report = verify(task, workflow)
        error_types = {error.error_type for error in report.errors}

        assert "E7_index_semantics_error" in error_types

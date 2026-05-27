# Benchmark notes

This folder contains the current small benchmark for checking semantic errors in raster-analysis workflows.

The benchmark is synthetic. Each task is designed to contain one or more common traps in raster algebra or Earth Observation workflows. The purpose is not to model a complete GIS project, but to test whether a generated workflow preserves the intended geospatial logic.

## Folder structure

```text
tasks/      # task specifications with expected requirements
workflows/  # reference good and bad workflows
```

Each task has:

- one task JSON file;
- one reference good workflow;
- one reference bad workflow.

The verifier compares a workflow with the task specification and reports semantic errors.

## Current tasks

| Task ID | Domain | Main traps |
|---|---|---|
| `flood_001` | Flood susceptibility | factor direction, land-cover reclassification, grid checks, NoData |
| `flood_002` | Flood susceptibility | factor direction, protected-area mask, unit consistency, NoData |
| `solar_001` | Solar suitability | slope direction, land-cover reclassification, protected-area mask |
| `solar_002` | Solar suitability | cloud mask, land-cover reclassification, distance direction |
| `ndvi_001` | Spectral index | NDVI formula, output range, NoData |
| `ndwi_001` | Spectral index | NDWI formula, grid alignment, output range |

## Error classes used in the MVP

| Code | Error type | Short description |
|---|---|---|
| E1 | Factor direction error | A factor is used in the wrong direction. |
| E2 | Grid alignment error | Required raster alignment checks are missing. |
| E3 | Unit confusion | Unit consistency is not checked. |
| E4 | NoData semantic error | NoData may be treated as valid data. |
| E5 | Categorical-continuous confusion | Class IDs are treated as continuous values. |
| E6 | Constraint-factor confusion | A hard mask is treated as a weighted factor. |
| E7 | Index semantics error | A spectral-index formula uses the wrong bands or direction. |

## Example

Run a bad workflow:

```bash
python -m cograster.cli \
  --task benchmark/tasks/solar/solar_002.json \
  --workflow benchmark/workflows/bad/solar_002_bad.json
```

Expected outcome: `Passed: false`.

Run the corresponding good workflow:

```bash
python -m cograster.cli \
  --task benchmark/tasks/solar/solar_002.json \
  --workflow benchmark/workflows/good/solar_002_good.json
```

Expected outcome: `Passed: true`.

## Methodological note

The current `tasks/` files still contain both the public task information and the expected verification requirements. This is convenient for the first MVP, but it is not ideal for a clean LLM experiment.

The next version should split the benchmark into:

```text
public_tasks/   # visible to the LLM
answer_keys/    # used only by the verifier
```

This will prevent the model from seeing expected operations directly during workflow generation.

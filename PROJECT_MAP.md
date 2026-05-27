# Project map

This file explains the current code structure in plain language.

## Core idea

The project checks whether an LLM-generated raster workflow follows the intended geospatial logic. The current version does not run raster processing. It verifies workflow JSON before execution.

## Main pipeline

```text
task JSON
  -> LLM-generated workflow JSON
  -> semantic verifier
  -> verification report
```

## Important folders

### `benchmark/tasks/`

Contains task specifications. In the current MVP, these files include the user query and the expected verification requirements.

Example:

```text
benchmark/tasks/flood/flood_001.json
```

### `benchmark/workflows/`

Contains reference workflows.

```text
benchmark/workflows/good/  # workflows that should pass
benchmark/workflows/bad/   # workflows that should fail
```

These files are mainly used to test that the verifier behaves as expected.

### `cograster/`

Contains the Python code.

Main files:

- `io.py`: reads JSON files.
- `schemas.py`: defines report and error data structures.
- `metrics.py`: calculates Cognitive Error Rate.
- `verifier.py`: compares a task and a workflow and finds semantic errors.
- `cli.py`: checks one existing workflow against one task.
- `llm.py`: sends prompts to Ollama and receives workflow JSON.
- `llm_cli.py`: runs one task through the LLM and verifier.
- `llm_benchmark.py`: runs all tasks in naive and guided modes.
- `run_benchmark.py`: checks the manually written good and bad workflows.

### `tests/`

Contains automated tests for the verifier.

Run them with:

```bash
pytest
```

### `runs/`

Stores generated workflows and verification reports from LLM benchmark runs. These files are useful for inspecting why a workflow passed or failed.

## What the verifier checks

The verifier currently checks four main things:

1. expected operations;
2. forbidden operations;
3. required checks;
4. spectral-index formulas.

For example, if a flood task expects:

```text
elevation -> inverse_normalize
```

but the workflow contains:

```text
elevation -> normalize
```

then the verifier reports a factor direction error.

## Prompt modes

### Naive mode

The LLM receives only the user query, output format, and allowed operation names.

### Guided mode

The LLM receives the same information plus explicit raster-reasoning rules. This mode is useful for the first proof of concept, but it is too explicit for a final evaluation.

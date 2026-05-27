# CogRasterBench

Working draft of a small benchmark and verifier for semantic errors in LLM-generated raster analysis workflows.

The project started from a practical concern: an LLM can produce a workflow that looks valid, but still applies the wrong geospatial logic. For example, it may use elevation in the wrong direction for flood susceptibility, treat land-cover class IDs as continuous numbers, forget raster alignment checks, or use a mask as an ordinary weighted factor.

At this stage the repository is a proof of concept. It does not process real GeoTIFF files yet. It checks structured workflow JSON files against task specifications.

## What is implemented

- six synthetic benchmark tasks;
- reference good and bad workflows;
- a rule-based semantic verifier;
- a small CLI for checking one task/workflow pair;
- optional local LLM integration through Ollama;
- a naive-vs-guided planning experiment;
- saved workflow and report examples from benchmark runs.

## Current benchmark scope

| Domain | Number of tasks |
|---|---:|
| Flood susceptibility | 2 |
| Solar suitability | 2 |
| Spectral indices | 2 |

The current verifier checks seven error classes:

| Code | Error class |
|---|---|
| E1 | Factor direction error |
| E2 | Grid alignment error |
| E3 | Unit confusion |
| E4 | NoData semantic error |
| E5 | Categorical-continuous confusion |
| E6 | Constraint-factor confusion |
| E7 | Index semantics error |

## Repository structure

```text
benchmark/
  README.md       # description of the benchmark tasks
  tasks/          # task specifications
  workflows/      # reference good and bad workflows

cograster/
  cli.py          # check one existing workflow against one task
  verifier.py     # semantic verification rules
  metrics.py      # Cognitive Error Rate calculation
  schemas.py      # report and error data structures
  llm.py          # optional Ollama-based workflow generation
  llm_cli.py      # run one task through the LLM and verifier
  llm_benchmark.py# run all tasks in naive/guided modes

tests/
  test_verifier.py

EXPERIMENTS.md    # notes from the first experiment
PROJECT_MAP.md    # short explanation of the code structure
pyproject.toml
```

## Installation

The current MVP only needs Python and pytest for tests. Ollama is optional and is needed only for the LLM-based runs.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install pytest
```

## Run tests

```bash
pytest
```

## Check a reference workflow

A correct workflow should pass:

```bash
python -m cograster.cli \
  --task benchmark/tasks/flood/flood_001.json \
  --workflow benchmark/workflows/good/flood_001_good.json
```

An intentionally incorrect workflow should fail:

```bash
python -m cograster.cli \
  --task benchmark/tasks/flood/flood_001.json \
  --workflow benchmark/workflows/bad/flood_001_bad.json
```

## Optional LLM run

If Ollama and `llama3.2` are installed locally, one task can be run through the LLM planner and verifier:

```bash
python -m cograster.llm_cli \
  --task benchmark/tasks/flood/flood_001.json \
  --mode naive
```

The full small benchmark can be run with:

```bash
python -m cograster.llm_benchmark
```

## Current limitations

This repository is intentionally small and should not be presented as a finished research result.

- The benchmark has only six synthetic tasks.
- The verifier checks workflow JSON, not actual raster outputs.
- No real GeoTIFF execution is implemented yet.
- The guided prompt currently contains explicit raster-reasoning rules.
- The current experiment is useful as a sanity check, not as a strong empirical claim.

## Next steps

The most important next methodological step is to separate benchmark files into:

- public task files, visible to the LLM;
- answer keys, visible only to the verifier.

After that, the benchmark can be expanded and the experiment can compare naive, minimal, guided, and repair settings more fairly.

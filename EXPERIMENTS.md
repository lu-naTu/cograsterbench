# Experiments

This file records small experiments run during the current MVP stage. The results below should be treated as preliminary checks of the pipeline, not as final research evidence.

## Experiment 001: naive vs guided workflow planning

**Date:** 2026-05-26  
**Model:** `llama3.2` via Ollama  
**Benchmark:** 6 synthetic raster-workflow tasks  
**Verifier:** rule-based workflow verifier

## Question

Can a local LLM generate workflow JSON that passes the semantic verifier? Does an explicit guided prompt reduce the errors found by the verifier on this small benchmark?

## Setup

Two prompt modes were compared.

### Naive mode

The model receives:

- the user query;
- the required JSON output format;
- the list of allowed operation names.

It does not receive explicit raster-analysis rules.

### Guided mode

The model receives the same information as in naive mode, plus explicit rules about:

- factor direction;
- categorical rasters;
- masks and hard constraints;
- grid alignment checks;
- NoData handling;
- NDVI and NDWI formulas.

## Results

| Task | Naive passed | Naive errors | Guided passed | Guided errors |
|---|---:|---:|---:|---:|
| `flood_001` | false | 7 | true | 0 |
| `flood_002` | false | 9 | true | 0 |
| `solar_001` | false | 8 | true | 0 |
| `solar_002` | false | 8 | true | 0 |
| `ndvi_001` | false | 7 | true | 0 |
| `ndwi_001` | false | 8 | true | 0 |

| Mode | Passed tasks | Failed tasks |
|---|---:|---:|
| Naive | 0 / 6 | 6 / 6 |
| Guided | 6 / 6 | 0 / 6 |

## Interpretation

The naive prompt produced workflows that failed the verifier on all six tasks. The guided prompt produced workflows that passed the verifier on all six tasks.

This is useful as a proof of concept: the pipeline can generate workflows, check them, and measure errors in a repeatable way. However, the result should be interpreted carefully. The benchmark is small, and the guided prompt contains rules that are close to the verifier rules.

A cautious interpretation is:

> On this small synthetic benchmark, explicit raster-reasoning instructions helped the model produce workflow JSON that satisfied the current verifier.

A stronger claim would require a larger benchmark, hidden answer keys, less direct prompting, and real raster execution checks.

## Limitations

- The benchmark has only six tasks.
- All tasks are synthetic and trap-based.
- The verifier is rule-based.
- The guided prompt is deliberately explicit.
- The LLM currently sees task files that include answer-like information in the original benchmark format.
- The system checks workflow JSON, not actual GeoTIFF outputs.
- False positives and verifier coverage are not measured yet.

## Next experiment

The next step is to split the benchmark into:

- public task files, which contain only the user query and available layers;
- answer key files, which contain expected operations, forbidden operations, and required checks.

After this split, the LLM will not see the expected operations directly. This will make later comparisons more meaningful.


## Experiment 002: Public Tasks and Hidden Answer Keys

Date: 2026-05-27

Model:

- llama3.2 via Ollama

Benchmark:

- 6 synthetic trap-based raster workflow tasks
- public task JSON is given to the LLM
- hidden answer key JSON is used only by the verifier

Compared modes:

### Naive

The LLM receives the public task and the required workflow JSON format.

### Minimal

The LLM receives the public task, the workflow JSON format, and general GIS planning guidance.

### Guided

The LLM receives the public task, the workflow JSON format, and explicit raster reasoning rules.

Results:

| Task | Naive | Naive Errors | Minimal | Minimal Errors | Guided | Guided Errors |
|---|---:|---:|---:|---:|---:|---:|
| flood_001 | false | 7 | false | 6 | true | 0 |
| flood_002 | false | 9 | false | 8 | true | 0 |
| solar_001 | false | 5 | false | 5 | true | 0 |
| solar_002 | false | 5 | false | 5 | true | 0 |
| ndvi_001 | false | 6 | false | 6 | true | 0 |
| ndwi_001 | false | 8 | false | 6 | true | 0 |

Summary:

| Mode | Passed |
|---|---:|
| Naive | 0 / 6 |
| Minimal | 0 / 6 |
| Guided | 6 / 6 |

Interpretation:

After separating public tasks from hidden answer keys, the LLM no longer receives the expected operations directly. In this stricter setup, naive and minimal prompting still fail all six tasks, while guided prompting passes all six tasks.

This suggests that general GIS instructions are not sufficient for this benchmark. More explicit raster-specific reasoning rules are needed to produce workflows that satisfy the semantic verifier.

Limitations:

- The benchmark is still small.
- The tasks are synthetic.
- The guided prompt now contains stronger domain-specific rules.
- The verifier is rule-based.
- The system still checks workflow JSON rather than real GeoTIFF outputs.
- The result should be treated as a controlled proof of concept, not as a final empirical claim.
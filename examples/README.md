# Examples

This folder contains selected examples of LLM-generated workflows and verifier reports.

The goal is to show concrete cases of:

- what the LLM generated;
- what errors the semantic verifier detected;
- how naive and guided prompting differ.

## Example: flood_001

Task: create a flood susceptibility workflow using elevation, slope, distance to river, and land cover.

Files:

- `naive_flood_001_workflow.json` — workflow generated in naive mode.
- `naive_flood_001_report.json` — verifier report for the naive workflow.
- `guided_flood_001_workflow.json` — workflow generated in guided mode.
- `guided_flood_001_report.json` — verifier report for the guided workflow.

## Interpretation

In naive mode, the LLM receives only the public task and the output format. It may therefore generate an incomplete or semantically incorrect workflow.

In guided mode, the LLM receives additional raster-specific reasoning rules. In this example, the generated workflow passes the semantic verifier.

This example is part of a small proof-of-concept benchmark and should not be interpreted as a final empirical result.
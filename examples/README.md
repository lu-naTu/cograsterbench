# Examples of LLM Outputs and Verifier Reports

This folder contains selected examples of LLM-generated raster workflows and the corresponding verifier reports.

The purpose is to make the benchmark result interpretable: instead of reporting only pass/fail scores, these examples show what the LLM generated and which semantic errors were detected.

## Example 1: flood_001

Files:

- `naive_flood_001_workflow.json`
- `naive_flood_001_report.json`
- `guided_flood_001_workflow.json`
- `guided_flood_001_report.json`

This example demonstrates common raster suitability errors, such as incorrect factor direction, missing grid alignment checks, or incorrect handling of categorical layers.

## Example 2: ndvi_001

Files:

- `naive_ndvi_001_workflow.json`
- `naive_ndvi_001_report.json`
- `guided_ndvi_001_workflow.json`
- `guided_ndvi_001_report.json`

This example demonstrates semantic errors in spectral index construction, such as treating spectral bands as generic continuous factors instead of reading them as bands for index computation.

## Interpretation

The benchmark uses a strict pass/fail criterion. A workflow fails if any required semantic operation or check is missing or incorrect.

Therefore, failed naive or minimal workflows should not be interpreted as completely meaningless outputs. Rather, they are often plausible-looking workflows that do not satisfy the full raster-specific semantic verifier.
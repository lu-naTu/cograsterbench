import json
import urllib.request
from typing import Any


OLLAMA_URL = "http://localhost:11434/api/generate"


WORKFLOW_SCHEMA = {
    "type": "object",
    "properties": {
        "workflow_id": {"type": "string"},
        "operations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "layer": {"type": "string"},
                    "operation": {"type": "string"},
                },
                "required": ["layer", "operation"],
            },
        },
        "checks": {
            "type": "array",
            "items": {"type": "string"},
        },
        "formula": {
            "type": "string",
        },
    },
    "required": ["workflow_id", "operations", "checks"],
}


def generate_workflow_with_ollama(
    task: dict[str, Any],
    model: str = "llama3.2",
    mode: str = "guided",
) -> dict[str, Any]:
    if mode == "naive":
        prompt = _build_naive_prompt(task)
    elif mode == "minimal":
        prompt = _build_minimal_prompt(task)
    elif mode == "guided":
        prompt = _build_guided_prompt(task)
    else:
        raise ValueError(f"Unknown mode: {mode}")

    request_data = {
        "model": model,
        "prompt": prompt,
        "format": WORKFLOW_SCHEMA,
        "stream": False,
        "options": {
            "temperature": 0
        },
    }

    request_body = json.dumps(request_data).encode("utf-8")

    request = urllib.request.Request(
        OLLAMA_URL,
        data=request_body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=120) as response:
        response_data = json.loads(response.read().decode("utf-8"))

    workflow_text = response_data["response"]
    workflow = json.loads(workflow_text)

    return workflow


def _workflow_format_instruction() -> str:
    return """
Return ONLY valid JSON.

The JSON must have this structure:
{
  "workflow_id": "string",
  "operations": [
    {
      "layer": "string",
      "operation": "string"
    }
  ],
  "checks": ["string"],
  "formula": "string, optional"
}

Allowed operations:
- normalize
- inverse_normalize
- reclassify
- mask
- read_band
- weighted_sum
Important output requirements:
- Create exactly one operation for every layer listed in available_layers.
- Do not skip any available layer.
- Use the original layer names exactly as provided.
- The operations list must cover all available_layers.
""".strip()



def _public_task_text(task: dict[str, Any]) -> str:
    return json.dumps(
        {
            "task_id": task.get("task_id"),
            "domain": task.get("domain"),
            "user_query": task.get("user_query"),
            "available_layers": task.get("available_layers", []),
        },
        ensure_ascii=False,
        indent=2,
    )


def _build_naive_prompt(task: dict[str, Any]) -> str:
    return f"""
You are a GIS workflow planning agent.

Create a raster algebra workflow JSON for the following task.

{_workflow_format_instruction()}

Task:
{_public_task_text(task)}
""".strip()


def _build_minimal_prompt(task: dict[str, Any]) -> str:
    return f"""
You are a GIS raster workflow planning agent.

Create a raster algebra workflow JSON for the following task.

{_workflow_format_instruction()}

General GIS planning guidance:
- Decide whether each layer is continuous, categorical, or a hard constraint.
- Decide whether higher values should increase or decrease the target value.
- Include standard raster alignment and data validity checks.
- Use spectral index formulas carefully when the task asks for an index.

Task:
{_public_task_text(task)}
""".strip()


def _build_guided_prompt(task: dict[str, Any]) -> str:
    return f"""
You are a raster algebra planning agent.

Create a workflow JSON for the following task.

{_workflow_format_instruction()}

Raster reasoning rules:
- For flood risk, elevation usually has negative effect: use inverse_normalize.
- For flood risk, slope usually has negative effect: use inverse_normalize.
- For flood risk, distance_to_river has negative effect: use inverse_normalize.
- For flood risk, rainfall usually has positive effect: use normalize.
- For solar suitability, slope usually has negative effect: use inverse_normalize.
- Distance to useful infrastructure usually has negative effect: use inverse_normalize.
- Categorical rasters such as land_cover must use reclassify.
- Hard constraints such as protected_areas or cloud_mask must use mask.
- For spectral index tasks, use read_band for all spectral bands.
- Do not normalize spectral bands before computing NDVI or NDWI.
- Always include checks: same_crs, same_transform, same_resolution, nodata_preserved.
- For flood and suitability mapping tasks, also include unit_consistency in checks.
- - For spectral index tasks such as NDVI and NDWI, the checks list must include output_range_-1_1.
- Do not replace output_range_-1_1 with unit_consistency for spectral index tasks.
- NDVI formula is (NIR - Red) / (NIR + Red).
- NDWI formula is (Green - NIR) / (Green + NIR).

Task:
{_public_task_text(task)}
""".strip()
# LFGG Load LoRA (Path)

## Overview
`LFGG Load LoRA (Path)` mirrors ComfyUI's core Load LoRA node but filters the LoRA dropdown to a chosen subfolder under `loras/`. Use it when you keep LoRAs organized in subfolders and want faster, cleaner selection.

## Inputs
| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `model` | MODEL | Yes | Diffusion model to apply the LoRA to. |
| `clip` | CLIP | Yes | CLIP model to apply the LoRA to. |
| `lora_path` | STRING | Yes | Subfolder under `loras/` used to filter the dropdown (e.g. `styles/portraits`). |
| `lora_name` | dropdown | Yes | LoRA name selected from the filtered list. |
| `strength_model` | FLOAT | Yes | Strength applied to the diffusion model. Can be negative. |
| `strength_clip` | FLOAT | Yes | Strength applied to the CLIP model. Can be negative. |

## Outputs
| Name | Type | Description |
| --- | --- | --- |
| `model` | MODEL | Diffusion model with LoRA applied. |
| `clip` | CLIP | CLIP model with LoRA applied. |

## Notes
- `lora_path` is always relative to the `loras/` directory. Absolute paths and `..` segments are rejected.
- If you change `lora_path`, refresh node definitions in ComfyUI to rebuild the dropdown list.
- When the list is empty, the node reports an error instead of loading an invalid selection.

## Example Workflow
1. Store LoRAs under `loras/styles/portraits/`.
2. Add **LFGG Load LoRA (Path)** and set `lora_path = styles/portraits`.
3. Pick a LoRA from the dropdown, then adjust `strength_model` and `strength_clip`.
4. Connect the outputs to the rest of your pipeline like the standard Load LoRA node.

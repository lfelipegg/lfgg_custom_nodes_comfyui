# LFGG Model Name From Model

## Overview
`LFGG Model Name From Model` traces an incoming `MODEL` connection upstream to a supported loader node and returns the source model filename stem as a string. This is useful when you want prompts, filenames, or metadata to reflect the checkpoint or UNet currently driving the graph.

## Inputs
| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `model` | MODEL | Yes | The model connection to trace back to a supported source loader. |

## Outputs
| Name | Type | Description |
| --- | --- | --- |
| `model_name` | STRING | The source model filename stem, without path or extension. |

## Supported Sources
- `CheckpointLoader`
- `CheckpointLoaderSimple`
- `unCLIPCheckpointLoader`
- `ImageOnlyCheckpointLoader`
- `DiffusersLoader`
- `UNETLoader`

## Notes
- The node follows upstream `MODEL` links instead of inspecting the runtime model object.
- Paths such as `sdxl/juggernaut.safetensors` are normalized to `juggernaut`.
- If the upstream graph is unsupported or ambiguous, the node returns `unknown_model`.

## Example Workflow
1. Load a checkpoint with **CheckpointLoaderSimple**.
2. Optionally pass the `MODEL` through **LFGG Load LoRA (Path)** or another model-modifier node.
3. Connect the final `MODEL` output to **LFGG Model Name From Model**.
4. Use the returned `STRING` in downstream text, save-name, or metadata nodes.

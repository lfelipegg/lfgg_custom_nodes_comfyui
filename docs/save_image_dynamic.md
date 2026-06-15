# LFGG Save Image Dynamic

## Overview
`LFGG Save Image Dynamic` saves an `IMAGE` batch as PNG files under ComfyUI's configured output directory. It supports dynamic subfolder and filename templates, can include a model name supplied by `LFGG Model Name From Model`, displays saved images in the ComfyUI UI, and returns absolute saved file paths as text.

## Inputs
| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `images` | IMAGE | Yes | Image batch to save as PNG files. |
| `path_template` | STRING | Yes | Output subfolder template under ComfyUI's output directory. Defaults to `runs/{model}/{date}`. |
| `filename_template` | STRING | Yes | Filename stem template without extension. Defaults to `{model}_{datetime}_{batch}`. |
| `model_name` | STRING | Optional | Connect a model-name string, usually from `LFGG Model Name From Model`. Blank values become `unknown_model`. |
| `compress_level` | INT | Optional | PNG compression level from 0 to 9. Default is 4. |

## Outputs
| Name | Type | Description |
| --- | --- | --- |
| `saved_paths` | STRING | Newline-separated absolute paths for every saved PNG. |

The node is also an output node, so saved images appear in ComfyUI's image result panel.

## Template Tokens
Both brace and percent token styles are supported.

| Token | Description |
| --- | --- |
| `{model}` / `%model%` | Sanitized `model_name`, or `unknown_model` when blank. |
| `{date}` / `%date%` | Current date as `YYYY-MM-DD`. |
| `{time}` / `%time%` | Current time as `HH-MM-SS`. |
| `{datetime}` / `%datetime%` | Current date and time as `YYYY-MM-DD_HH-MM-SS`. |
| `{year}` / `%year%` | Four-digit year. |
| `{month}` / `%month%` | Two-digit month. |
| `{day}` / `%day%` | Two-digit day. |
| `{hour}` / `%hour%` | Two-digit hour. |
| `{minute}` / `%minute%` | Two-digit minute. |
| `{second}` / `%second%` | Two-digit second. |
| `{width}` / `%width%` | Image width in pixels. |
| `{height}` / `%height%` | Image height in pixels. |
| `{batch}` / `%batch_num%` | Zero-based image index inside the batch. |
| `{counter}` / `%counter%` | Five-digit overwrite-safe counter. |

If neither template includes a counter token, the node appends a native-style suffix like `_00001_` before `.png`.

## Safety and Sanitization
- `path_template` is always treated as a subfolder under ComfyUI's output directory.
- Absolute paths and `..` traversal are rejected.
- Unsafe Windows filename characters are replaced with underscores.
- Prompt and workflow metadata are embedded in PNG files unless ComfyUI is started with metadata disabled.

## Example Workflow
1. Load a checkpoint with **CheckpointLoaderSimple**.
2. Connect the model to **LFGG Model Name From Model**.
3. Connect generated images to **LFGG Save Image Dynamic**.
4. Set `path_template` to `runs/{model}/{date}`.
5. Set `filename_template` to `{model}_{datetime}_{batch}`.
6. Connect `model_name` from **LFGG Model Name From Model**.

Example output:
```
output/runs/juggernaut/2026-06-03/juggernaut_2026-06-03_14-05-09_0_00001_.png
```

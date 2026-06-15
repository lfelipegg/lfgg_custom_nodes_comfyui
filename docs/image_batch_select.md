# LFGG Image Batch Select

## Overview
`LFGG Image Batch Select` selects one image from an incoming `IMAGE` batch and returns it as a one-image `IMAGE` batch. It is useful for extracting the first frame, last frame, or a specific frame from animation, video, or batch-generation workflows.

## Inputs
| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `images` | IMAGE | Yes | Input image batch shaped as `(batch, height, width, channels)`. |
| `mode` | Select | Yes | `last`, `first`, or `index`. Defaults to `last`. |
| `batch_index` | INT | Yes | Zero-based image index used only when `mode` is `index`. Values above the batch size clamp to the last image. |

## Outputs
| Name | Type | Description |
| --- | --- | --- |
| `image` | IMAGE | The selected image, preserved as a batch of size 1. |

## Selection Modes
- `last`: Selects the final image in the batch.
- `first`: Selects the first image in the batch.
- `index`: Selects `batch_index`, clamped to the last available image when the requested index is too large.

## Example Workflow
1. Produce or load an `IMAGE` batch with multiple frames.
2. Connect the batch to **LFGG Image Batch Select**.
3. Set `mode` to `last` to extract the final frame, or set `mode` to `index` and choose a zero-based `batch_index`.
4. Connect the output `image` to preview, save, upscale, or image-to-image nodes.

## Constraints
- The input must be a 4D ComfyUI `IMAGE` batch: `(batch, height, width, channels)`.
- Empty image batches raise an error.
- The output remains an `IMAGE` batch with one frame so downstream ComfyUI image nodes receive the expected shape.

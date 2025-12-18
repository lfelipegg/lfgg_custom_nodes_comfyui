# LFGG Latent Size by Ratio

## Overview
`LFGG Latent Size by Ratio` turns an aspect-ratio preset (or a custom ratio) plus a target base size into latent-space width/height values and an empty LATENT tensor. The node guarantees both dimensions are divisible by a user-selected value, making it ideal for workflows where downstream samplers or VAEs require strict multiples.

## Inputs
| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `ratio_preset` | dropdown | Yes | Choose from common ratios (1:1, 4:3, 3:2, 16:9, 9:16) or switch to `Custom` to drive the ratio manually. |
| `base_size` | INT | Yes | Sets the longest side (width for landscape, height for portrait). Min 256, max 4096, step 8. |
| `custom_ratio_w` | INT | Optional | Width portion of the custom ratio. Only used when `ratio_preset = Custom`. |
| `custom_ratio_h` | INT | Optional | Height portion of the custom ratio. Only used when `ratio_preset = Custom`. |
| `divisible_by` | INT | Optional | Forces both dimensions to be divisible by this number (default 8). Helpful when mixing with tiling or patch-based models. |
| `batch_size` | INT | Optional | Number of latent samples to allocate in the output tensor. |

## Outputs
| Name | Type | Description |
| --- | --- | --- |
| `width` | INT | Final latent width after ratio math and divisibility rounding. |
| `height` | INT | Final latent height after ratio math and divisibility rounding. |
| `latent` | LATENT | Zero-initialized tensor shaped `(batch_size, 4, height/8, width/8)` generated on CPU. Plug directly into samplers or conditioning nodes that accept latents. |

## How It Works
1. Resolve the width:height ratio either from the preset list or from the custom values.
2. Use `base_size` as the maximum dimension and calculate the other side from the ratio.
3. Round both dimensions down so they are divisible by `divisible_by`.
4. Build an empty latent tensor with four channels and spatial size reduced by a factor of 8 (Stable Diffusion latent resolution).

Because the latent tensor comes pre-sized, you can bypass additional `Empty Latent Image` nodes when you just need ratio control plus batching.

## Example Workflow
1. Drop **LFGG Latent Size by Ratio** at the start of your graph.
2. Set `ratio_preset = 3:2` and `base_size = 1152` for a landscape shot.
3. Keep `divisible_by = 16` if your pipeline combines tiling or multi-resolution upscalers.
4. Connect the `latent` output to your sampler (e.g., `KSampler`), feed `width`/`height` into preview nodes, and drive the rest of the workflow normally.
5. When a vertical poster is needed, switch to the `9:16` preset or set `Custom` with `custom_ratio_w = 2`, `custom_ratio_h = 3`.

## Tips & Notes
- Increasing `divisible_by` reduces resolution but guarantees compatibility with models that expect larger tile multiples.
- `batch_size` changes only the latent tensor allocation; if you want multiple prompts per batch, coordinate with sampler settings as well.
- The output dimensions are latent space values (1/8 of pixel space for SD1.x). Multiply by 8 if you need to display the equivalent pixel resolution in UI text.
- Tensors are created on CPU; move them to GPU later in the graph if required by custom CUDA nodes.

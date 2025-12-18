# LFGG Pixel Budget Latent Size

Compute a safe width/height pair that keeps the total pixel count under a user-defined budget while preserving the aspect ratio of a reference `IMAGE`. The node also provisions an empty `LATENT` that matches the rounded resolution (height ÷ 8, width ÷ 8).

## Inputs
- `image`: Source batch of images. Only the spatial dimensions are needed; the RGB values are ignored.
- `max_pixels`: Pixel budget (`width * height`) that the resized resolution must not exceed. The node scales the aspect ratio down when the input image area is larger.
- `divisible_by`: Forces both width and height to land on multiples of `lcm(divisible_by, 8)` so downstream samplers receive compatible latent dimensions.

## Outputs
- `latent`: Zeroed tensor sized `(batch, 4, height / 8, width / 8)` useful as a placeholder for samplers or conditioning nodes.
- `width` / `height`: Final pixel dimensions after scaling and rounding.

## How It Works
1. Read the incoming image width/height and compute the aspect ratio.
2. Derive a scale factor with `scale = min(sqrt(max_pixels / (orig_width * orig_height)), 1)`.
3. Apply the scale to both axis values and round them **down** to `lcm(divisible_by, 8)` so the pixel budget is never exceeded.
4. Instantiate an empty latent tensor (on the same device as the image) sized for the rounded resolution.

## Usage Notes
- Keep `max_pixels` at or above `lcm(divisible_by, 8)²`; otherwise the node raises a warning so you know to reduce `divisible_by` or increase the budget.
- Because rounding happens after scaling, the reported width/height are always ≤ `sqrt(max_pixels)` while staying in the same aspect ratio as the source.
- Pair this node immediately before your resizing/sampling step to ensure Image-to-Video chains remain inside the VRAM budget without distorting the footage.

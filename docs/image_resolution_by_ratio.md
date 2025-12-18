# LFGG Image Resolution by Ratio

Generate a latent-sized resolution template that copies the aspect ratio from any `IMAGE` input while capping the longest edge.

## Inputs
- `image`: Source batch of images (batch, H, W, C) used only for size metadata.
- `base_size`: Maximum dimension that the resized image can reach. The longest side will match this when the input is larger.
- `divisible_by`: Snap both width and height to multiples of this value (and 8) so latents line up with downstream samplers.

## Outputs
- `latent`: Zero-initialized samples block sized for the resized resolution (batch × 4 × H/8 × W/8).
- `original_width` / `original_height`: Metadata for tracing how the node adjusted the size.
- `new_width` / `new_height`: Rounded resolution that honors `base_size` and `divisible_by`.

## Notes
- `base_size` must be at least `lcm(8, divisible_by)` to ensure the returned LATENT dimensions stay valid.
- Because the output latent is empty, feed it into a downstream sampler or conditioning node that expects only a correctly-sized tensor.

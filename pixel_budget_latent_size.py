"""PixelBudgetLatentSize node implementation."""

from __future__ import annotations

import math
from typing import Tuple

import torch


def _lcm(values: Tuple[int, int]) -> int:
    """Return least common multiple for positive integers."""

    a, b = values
    if a <= 0 or b <= 0:
        raise ValueError("lcm arguments must be positive integers")
    return abs(a * b) // math.gcd(a, b)


def _round_down(value: float, multiple: int) -> int:
    """Round down to the nearest positive multiple."""

    if multiple <= 0:
        raise ValueError("multiple must be positive")
    snapped = int(math.floor(value / multiple)) * multiple
    return snapped


class PixelBudgetLatentSize:
    """
    Resize metadata to honor a pixel budget while keeping the original ratio.
    """

    @classmethod
    def INPUT_TYPES(cls):  # noqa: N802 - ComfyUI signature
        return {
            "required": {
                "image": ("IMAGE",),
                "max_pixels": (
                    "INT",
                    {
                        "default": 900_000,
                        "min": 64,
                        "max": 67_108_864,  # 8192^2
                        "step": 1024,
                        "tooltip": "Maximum allowed width * height for the resized output.",
                    },
                ),
                "divisible_by": (
                    "INT",
                    {
                        "default": 64,
                        "min": 1,
                        "max": 512,
                        "tooltip": "Snap outputs to this multiple (and 8) so latents align with samplers.",
                    },
                ),
            }
        }

    RETURN_TYPES = ("LATENT", "INT", "INT")
    RETURN_NAMES = ("latent", "width", "height")
    FUNCTION = "generate"
    CATEGORY = "LFGG / Image Size"
    DESCRIPTION = (
        "Match an IMAGE's aspect ratio while respecting a total pixel budget.\n\n"
        "- Extract ratio from the connected IMAGE input\n"
        "- Scale down proportionally so width * height <= max_pixels\n"
        "- Round down to lcm(divisible_by, 8) to keep latents valid\n"
        "- Emit a zeroed LATENT with the finished width and height values"
    )

    def generate(self, image: torch.Tensor, max_pixels: int = 900_000, divisible_by: int = 64):
        if not isinstance(image, torch.Tensor):
            raise TypeError("image input must be a torch.Tensor")
        if image.ndim != 4:
            raise ValueError("IMAGE tensors must be shaped (batch, height, width, channels)")

        batch = int(image.shape[0])
        height = int(image.shape[1])
        width = int(image.shape[2])
        if width <= 0 or height <= 0:
            raise ValueError("IMAGE inputs must have positive width and height")

        pixel_budget = max(1, int(max_pixels))
        div_value = max(1, int(divisible_by))
        target_multiple = _lcm((div_value, 8))

        current_pixels = width * height
        if current_pixels == 0:
            raise ValueError("Invalid IMAGE sizes supplied")

        scale = min(math.sqrt(pixel_budget / current_pixels), 1.0)
        scaled_width = width * scale
        scaled_height = height * scale

        new_width = _round_down(scaled_width, target_multiple)
        new_height = _round_down(scaled_height, target_multiple)

        if new_width == 0 or new_height == 0:
            raise ValueError(
                "Pixel budget too small for the requested divisible_by: "
                "try raising max_pixels or reducing divisible_by"
            )

        latent = {
            "samples": torch.zeros(
                (batch, 4, new_height // 8, new_width // 8),
                dtype=torch.float32,
                device=image.device,
            )
        }

        return latent, int(new_width), int(new_height)


NODE_CLASS_MAPPINGS = {
    "LfggPixelBudgetLatentSize": PixelBudgetLatentSize,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LfggPixelBudgetLatentSize": "LFGG Pixel Budget Latent Size",
}

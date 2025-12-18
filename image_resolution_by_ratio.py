"""ImageResolutionByRatio node implementation."""

from __future__ import annotations

import math
from typing import Tuple

import torch


def _lcm(a: int, b: int) -> int:
    """Compute least common multiple for positive integers."""

    if a == 0 or b == 0:
        return 0
    return abs(a * b) // math.gcd(a, b)


def _scale_to_base(
    width: int,
    height: int,
    base_size: int,
) -> Tuple[float, float, bool, bool]:
    """Scale width/height so the largest side equals base_size when needed."""

    largest = max(width, height)
    if largest <= base_size:
        return float(width), float(height), False, False

    scale = base_size / largest
    width_limited = width >= height
    height_limited = height >= width
    return (
        width * scale,
        height * scale,
        width_limited,
        height_limited,
    )


def _round_to_multiple(
    value: float,
    multiple: int,
    upper_bound: int | None = None,
) -> int:
    """Round a float to the nearest multiple while honoring optional limits."""

    snapped = int(round(value / multiple)) * multiple
    if snapped < multiple:
        snapped = multiple

    if upper_bound is not None and snapped > upper_bound:
        remainder = upper_bound % multiple
        snapped = upper_bound if remainder == 0 else upper_bound - remainder
        if snapped < multiple:
            snapped = upper_bound

    return snapped


class ImageResolutionByRatio:
    """Resize metadata while preserving aspect ratio and latent compatibility."""

    @classmethod
    def INPUT_TYPES(cls):  # noqa: N802 - ComfyUI signature
        return {
            "required": {
                "image": ("IMAGE",),
                "base_size": (
                    "INT",
                    {
                        "default": 1024,
                        "min": 64,
                        "max": 8192,
                        "step": 64,
                        "tooltip": "Maximum dimension (in pixels) applied to the longest image side.",
                    },
                ),
                "divisible_by": (
                    "INT",
                    {
                        "default": 8,
                        "min": 1,
                        "max": 512,
                        "tooltip": "Round outputs to this multiple while keeping latents valid.",
                    },
                ),
            }
        }

    RETURN_TYPES = ("LATENT", "INT", "INT", "INT", "INT")
    RETURN_NAMES = (
        "latent",
        "original_width",
        "original_height",
        "new_width",
        "new_height",
    )
    FUNCTION = "process"
    CATEGORY = "LFGG / Image"
    DESCRIPTION = (
        "Adjust an image resolution to a new max size while preserving aspect ratio.\n\n"
        "- Longest edge scaled to base_size when needed\n"
        "- Dimensions snapped to divisible_by (also multiples of 8) for latent compatibility\n"
        "- Emits a zeroed LATENT, new dimensions, and the original size"
    )

    def process(self, image: torch.Tensor, base_size: int = 1024, divisible_by: int = 8):
        if not isinstance(image, torch.Tensor):
            raise TypeError("image input must be a torch.Tensor")
        if image.ndim != 4:
            raise ValueError("IMAGE tensors must be 4D: (batch, height, width, channels)")

        batch, height, width = image.shape[0], int(image.shape[1]), int(image.shape[2])
        base_size = int(base_size)
        div_value = max(1, int(divisible_by))
        target_multiple = _lcm(8, div_value)

        if target_multiple == 0:
            raise ValueError("divisible_by must be positive")
        if base_size < target_multiple:
            raise ValueError(
                "base_size must be greater than or equal to lcm(8, divisible_by)"
            )

        scaled_w, scaled_h, limit_w, limit_h = _scale_to_base(width, height, base_size)
        upper_w = base_size if limit_w else None
        upper_h = base_size if limit_h else None

        new_width = _round_to_multiple(scaled_w, target_multiple, upper_w)
        new_height = _round_to_multiple(scaled_h, target_multiple, upper_h)

        latent = {
            "samples": torch.zeros(
                (batch, 4, new_height // 8, new_width // 8),
                dtype=torch.float32,
                device=image.device,
            )
        }

        return latent, width, height, new_width, new_height


NODE_CLASS_MAPPINGS = {
    "LfggImageResolutionByRatio": ImageResolutionByRatio,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LfggImageResolutionByRatio": "LFGG Image Resolution by Ratio",
}


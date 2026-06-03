"""LatentSizeByRatio node implementation."""

from __future__ import annotations

import math

import torch


def _lcm(a: int, b: int) -> int:
    if a <= 0 or b <= 0:
        raise ValueError("lcm arguments must be positive integers")
    return abs(a * b) // math.gcd(a, b)


def _round_to_multiple(value: float, multiple: int, upper_bound: int | None = None) -> int:
    snapped = int(round(value / multiple)) * multiple
    if snapped < multiple:
        snapped = multiple

    if upper_bound is not None and snapped > upper_bound:
        remainder = upper_bound % multiple
        snapped = upper_bound if remainder == 0 else upper_bound - remainder
        if snapped < multiple:
            snapped = multiple

    return snapped

class LatentSizeByRatio:
    """
    Generates latent width, height and an empty LATENT
    based on an aspect ratio preset or custom ratio.
    """

    RATIO_PRESETS = {
        "1:1 (Square)": (1, 1),
        "4:3": (4, 3),
        "3:2": (3, 2),
        "16:9": (16, 9),
        "9:16": (9, 16),
        "Custom": None,
    }

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "ratio_preset": (tuple(cls.RATIO_PRESETS.keys()),),
                "base_size": (
                    "INT",
                    {
                        "default": 1024,
                        "min": 256,
                        "max": 4096,
                        "step": 8,
                    },
                ),
            },
            "optional": {
                "custom_ratio_w": (
                    "INT",
                    {"default": 1, "min": 1, "max": 64},
                ),
                "custom_ratio_h": (
                    "INT",
                    {"default": 1, "min": 1, "max": 64},
                ),
                "divisible_by": (
                    "INT",
                    {
                        "default": 8,
                        "min": 1,
                        "max": 64,
                        "tooltip": "Force output dimensions to be divisible by this value",
                    },
                ),
                "batch_size": (
                    "INT",
                    {
                        "default": 1,
                        "min": 1,
                        "max": 64,
                        "tooltip": "Batch size for generated LATENT",
                    },
                ),
            },
        }

    RETURN_TYPES = ("INT", "INT", "LATENT")
    RETURN_NAMES = ("width", "height", "latent")
    FUNCTION = "compute"
    CATEGORY = "LFGG / Latents"

    DESCRIPTION = (
        "Computes latent width and height from an aspect ratio.\n\n"
        "- base_size defines the largest dimension (pixels)\n"
        "- Supports preset or custom ratios\n"
        "- Snaps to lcm(8, divisible_by) to keep LATENT valid\n"
        "- Can generate an empty LATENT output directly"
    )

    def compute(
        self,
        ratio_preset: str,
        base_size: int,
        custom_ratio_w: int = 1,
        custom_ratio_h: int = 1,
        divisible_by: int = 8,
        batch_size: int = 1,
    ):
        # ---- Resolve ratio ----
        if ratio_preset == "Custom":
            w_ratio = int(custom_ratio_w)
            h_ratio = int(custom_ratio_h)
        else:
            w_ratio, h_ratio = self.RATIO_PRESETS[ratio_preset]

        if w_ratio <= 0 or h_ratio <= 0:
            raise ValueError("Ratio values must be positive integers")

        ratio = w_ratio / h_ratio
        base_size = int(base_size)

        # ---- Compute dimensions ----
        if ratio >= 1.0:
            scaled_width = float(base_size)
            scaled_height = float(base_size) / ratio
            upper_w = base_size
            upper_h = None
        else:
            scaled_height = float(base_size)
            scaled_width = float(base_size) * ratio
            upper_w = None
            upper_h = base_size

        div = max(1, int(divisible_by))
        multiple = _lcm(8, div)

        width = _round_to_multiple(scaled_width, multiple, upper_w)
        height = _round_to_multiple(scaled_height, multiple, upper_h)

        batch = max(1, int(batch_size))

        # ---- Create empty LATENT ----
        latent = {
            "samples": torch.zeros(
                (batch, 4, height // 8, width // 8),
                dtype=torch.float32,
                device="cpu",
            )
        }

        return int(width), int(height), latent


# ---- Registration ----
NODE_CLASS_MAPPINGS = {
    "LfggLatentSizeByRatio": LatentSizeByRatio,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LfggLatentSizeByRatio": "LFGG Latent Size by Ratio",
}

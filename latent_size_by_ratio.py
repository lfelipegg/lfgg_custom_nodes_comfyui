# latent_size_by_ratio.py

import torch

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
        "• base_size defines the largest dimension\n"
        "• Supports preset or custom ratios\n"
        "• Can generate an empty LATENT output directly\n"
        "• Output is latent resolution, not pixel resolution"
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

        ratio = w_ratio / h_ratio

        # ---- Compute dimensions ----
        if ratio >= 1.0:
            width = base_size
            height = int(round(base_size / ratio))
        else:
            height = base_size
            width = int(round(base_size * ratio))

        # ---- Enforce divisibility ----
        div = max(1, int(divisible_by))
        width = (width // div) * div
        height = (height // div) * div

        # ---- Create empty LATENT ----
        latent = {
            "samples": torch.zeros(
                (batch_size, 4, height // 8, width // 8),
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

# latent_size_by_ratio.py

class LatentSizeByRatio:
    """
    Computes latent width and height based on an aspect ratio preset
    or a custom ratio. The output can be constrained to be divisible
    by a specific value (e.g. 8 or 16) for model compatibility.
    """

    # ---- Ratio presets ----
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
                        "tooltip": "Largest latent dimension before aspect ratio is applied",
                    },
                ),
            },
            "optional": {
                "custom_ratio_w": (
                    "INT",
                    {
                        "default": 1,
                        "min": 1,
                        "max": 64,
                        "step": 1,
                        "tooltip": "Used only when ratio preset is Custom",
                    },
                ),
                "custom_ratio_h": (
                    "INT",
                    {
                        "default": 1,
                        "min": 1,
                        "max": 64,
                        "step": 1,
                        "tooltip": "Used only when ratio preset is Custom",
                    },
                ),
                "divisible_by": (
                    "INT",
                    {
                        "default": 8,
                        "min": 1,
                        "max": 64,
                        "step": 1,
                        "tooltip": "Force output to be divisible by this value (e.g. 8 or 16)",
                    },
                ),
            },
        }

    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("latent_width", "latent_height")
    FUNCTION = "compute"
    CATEGORY = "LFGG / Latents"

    # ---- Node description (shown in UI) ----
    DESCRIPTION = (
        "Generates latent width and height from an aspect ratio.\n\n"
        "• Choose a preset ratio or use Custom\n"
        "• base_size defines the largest dimension\n"
        "• Output can be forced to be divisible by a specific value\n\n"
        "Note: Output values are latent resolution, not final pixel size."
    )

    def compute(
        self,
        ratio_preset: str,
        base_size: int,
        custom_ratio_w: int = 1,
        custom_ratio_h: int = 1,
        divisible_by: int = 8,
    ):
        # --- Resolve ratio ---
        if ratio_preset == "Custom":
            w_ratio = int(custom_ratio_w)
            h_ratio = int(custom_ratio_h)
        else:
            w_ratio, h_ratio = self.RATIO_PRESETS[ratio_preset]

        ratio = w_ratio / h_ratio

        # --- Compute dimensions ---
        if ratio >= 1.0:
            width = base_size
            height = int(round(base_size / ratio))
        else:
            height = base_size
            width = int(round(base_size * ratio))

        # --- Enforce divisibility ---
        div = max(1, int(divisible_by))
        width = (width // div) * div
        height = (height // div) * div

        return int(width), int(height)


# ---- ComfyUI registration ----
NODE_CLASS_MAPPINGS = {
    "LatentSizeByRatio": LatentSizeByRatio,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LatentSizeByRatio": "LFGG - Latent Size by Ratio",
}

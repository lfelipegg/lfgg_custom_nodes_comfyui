# latent_size_by_ratio.py

class LatentSizeByRatio:
    """
    Computes latent width/height based on aspect ratio presets
    or a custom ratio, keeping total pixels roughly consistent.
    """

    # ---- Presets ----
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
                # IMPORTANT: COMBO -> dropdown
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
                    {
                        "default": 1,
                        "min": 1,
                        "max": 32,
                        "step": 1,
                    },
                ),
                "custom_ratio_h": (
                    "INT",
                    {
                        "default": 1,
                        "min": 1,
                        "max": 32,
                        "step": 1,
                    },
                ),
            },
        }

    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("latent_width", "latent_height")
    FUNCTION = "compute"
    CATEGORY = "LFGG / Latents"

    def compute(
        self,
        ratio_preset: str,
        base_size: int,
        custom_ratio_w: int = 1,
        custom_ratio_h: int = 1,
    ):
        # --- Resolve ratio ---
        if ratio_preset == "Custom":
            w_ratio = int(custom_ratio_w)
            h_ratio = int(custom_ratio_h)
        else:
            w_ratio, h_ratio = self.RATIO_PRESETS[ratio_preset]

        # --- Normalize ratio ---
        ratio = w_ratio / h_ratio

        # base_size represents the *largest* dimension
        if ratio >= 1.0:
            width = base_size
            height = int(round(base_size / ratio))
        else:
            height = base_size
            width = int(round(base_size * ratio))

        # --- Latents must be divisible by 8 ---
        width = (width // 8) * 8
        height = (height // 8) * 8

        return int(width), int(height)


# ---- ComfyUI registration ----
NODE_CLASS_MAPPINGS = {
    "LatentSizeByRatio": LatentSizeByRatio,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LatentSizeByRatio": "LFGG - Latent Size by Ratio",
}

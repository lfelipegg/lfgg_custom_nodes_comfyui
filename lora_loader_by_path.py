"""LoRA loader filtered by subpath under the loras/ folder."""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import List

import comfy.sd
import comfy.utils
import folder_paths

NO_LORA = "<no loras found>"


def _normalize_subpath(value: str) -> str:
    cleaned = value.replace("\\", "/").strip().strip("/")
    if not cleaned:
        return ""
    if ":" in cleaned:
        raise ValueError("LoRA path must be a subfolder under the loras directory.")
    path = PurePosixPath(cleaned)
    if path.is_absolute() or any(part == ".." for part in path.parts):
        raise ValueError("LoRA path must be a subfolder under the loras directory.")
    return path.as_posix()


def _filter_lora_choices(subpath: str) -> List[str]:
    choices = folder_paths.get_filename_list("loras")
    clean_subpath = _normalize_subpath(subpath)
    if not clean_subpath:
        return choices
    prefix = f"{clean_subpath}/"
    filtered = [name for name in choices if name.replace("\\", "/").startswith(prefix)]
    return filtered


class LoraLoaderByPath:
    """
    Load a LoRA from a specific subfolder under loras/.
    """

    DESCRIPTION = (
        "Load a LoRA from a subfolder under loras/ and apply it to model + CLIP.\n\n"
        "- lora_path filters the dropdown to a subfolder under loras/\n"
        "- Use relative paths like styles/portraits (no drive letters)\n"
        "- If the dropdown looks stale, refresh node definitions"
    )

    RETURN_TYPES = ("MODEL", "CLIP")
    OUTPUT_TOOLTIPS = ("The modified diffusion model.", "The modified CLIP model.")
    FUNCTION = "load_lora"
    CATEGORY = "LFGG / Loaders"

    _last_subpath: str = ""

    def __init__(self) -> None:
        self.loaded_lora = None

    @classmethod
    def INPUT_TYPES(cls):
        choices = _filter_lora_choices(cls._last_subpath)
        choice_tuple = tuple(choices or [NO_LORA])
        default_choice = choice_tuple[0]
        return {
            "required": {
                "model": ("MODEL", {"tooltip": "The diffusion model the LoRA will be applied to."}),
                "clip": ("CLIP", {"tooltip": "The CLIP model the LoRA will be applied to."}),
                "lora_path": (
                    "STRING",
                    {
                        "default": cls._last_subpath,
                        "multiline": False,
                        "tooltip": "Subfolder under loras/ used to filter the dropdown (e.g. styles/portraits).",
                    },
                ),
                "lora_name": (
                    choice_tuple,
                    {"tooltip": "The name of the LoRA (filtered by lora_path)."},
                ),
                "strength_model": (
                    "FLOAT",
                    {
                        "default": 1.0,
                        "min": -100.0,
                        "max": 100.0,
                        "step": 0.01,
                        "tooltip": "How strongly to modify the diffusion model. This value can be negative.",
                    },
                ),
                "strength_clip": (
                    "FLOAT",
                    {
                        "default": 1.0,
                        "min": -100.0,
                        "max": 100.0,
                        "step": 0.01,
                        "tooltip": "How strongly to modify the CLIP model. This value can be negative.",
                    },
                ),
            }
        }

    def load_lora(self, model, clip, lora_path: str, lora_name: str, strength_model: float, strength_clip: float):
        if lora_name == NO_LORA:
            raise ValueError("No LoRA files found under the specified lora_path.")

        subpath = _normalize_subpath(lora_path)
        self.__class__._last_subpath = subpath
        if subpath:
            prefix = f"{subpath}/"
            normalized_name = lora_name.replace("\\", "/")
            if not normalized_name.startswith(prefix):
                raise ValueError("Selected LoRA is not under the specified lora_path.")

        if strength_model == 0 and strength_clip == 0:
            return (model, clip)

        lora_path_full = folder_paths.get_full_path_or_raise("loras", lora_name)
        lora = None
        if self.loaded_lora is not None:
            if self.loaded_lora[0] == lora_path_full:
                lora = self.loaded_lora[1]
            else:
                self.loaded_lora = None

        if lora is None:
            lora = comfy.utils.load_torch_file(lora_path_full, safe_load=True)
            self.loaded_lora = (lora_path_full, lora)

        model_lora, clip_lora = comfy.sd.load_lora_for_models(model, clip, lora, strength_model, strength_clip)
        return (model_lora, clip_lora)


# ---- Registration ----
NODE_CLASS_MAPPINGS = {
    "LfggLoraLoaderByPath": LoraLoaderByPath,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LfggLoraLoaderByPath": "LFGG Load LoRA (Path)",
}

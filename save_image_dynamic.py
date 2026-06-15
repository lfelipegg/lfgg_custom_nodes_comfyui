"""Dynamic image save node for LFGG workflows."""

from __future__ import annotations

import json
import os
import re
import time
from types import SimpleNamespace

try:
    import folder_paths
except Exception:  # pragma: no cover - ComfyUI provides this at runtime.
    folder_paths = SimpleNamespace(get_output_directory=lambda: os.path.abspath("output"))

try:
    from comfy.cli_args import args
except Exception:  # pragma: no cover - ComfyUI provides this at runtime.
    args = SimpleNamespace(disable_metadata=False)


UNKNOWN_MODEL_NAME = "unknown_model"
_UNSAFE_COMPONENT_RE = re.compile(r'[\x00-\x1f<>:"/\\|?*]+')
_UNDERSCORE_RUN_RE = re.compile(r"_+")
_WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}

_local_time = time.localtime


def _normalize_model_name(model_name: str | None) -> str:
    cleaned = str(model_name or "").strip()
    if not cleaned:
        return UNKNOWN_MODEL_NAME
    return _sanitize_filename_component(cleaned)


def _sanitize_filename_component(value: str) -> str:
    cleaned = _UNSAFE_COMPONENT_RE.sub("_", str(value).strip())
    cleaned = _UNDERSCORE_RUN_RE.sub("_", cleaned).strip(" ._")
    if not cleaned:
        cleaned = "image"

    if cleaned.upper() in _WINDOWS_RESERVED_NAMES:
        cleaned = f"_{cleaned}"

    return cleaned


def _expand_template(template: str, values: dict[str, str]) -> str:
    expanded = str(template or "")
    for key, value in values.items():
        expanded = expanded.replace(f"{{{key}}}", value)
        expanded = expanded.replace(f"%{key}%", value)

    expanded = expanded.replace("%batch_num%", values.get("batch", "0"))
    return expanded


def _time_tokens(now=None) -> dict[str, str]:
    current = now if now is not None else _local_time()
    year = str(current.tm_year)
    month = str(current.tm_mon).zfill(2)
    day = str(current.tm_mday).zfill(2)
    hour = str(current.tm_hour).zfill(2)
    minute = str(current.tm_min).zfill(2)
    second = str(current.tm_sec).zfill(2)
    date = f"{year}-{month}-{day}"
    time_value = f"{hour}-{minute}-{second}"

    return {
        "year": year,
        "month": month,
        "day": day,
        "hour": hour,
        "minute": minute,
        "second": second,
        "date": date,
        "time": time_value,
        "datetime": f"{date}_{time_value}",
    }


def _token_values(
    *,
    model_name: str,
    width: int,
    height: int,
    batch: int,
    counter: int,
    now=None,
) -> dict[str, str]:
    values = _time_tokens(now)
    values.update(
        {
            "model": _normalize_model_name(model_name),
            "width": str(int(width)),
            "height": str(int(height)),
            "batch": str(int(batch)),
            "counter": f"{int(counter):05}",
        }
    )
    return values


def _resolve_output_folder(output_dir: str, subfolder_template: str) -> tuple[str, str]:
    if os.path.isabs(subfolder_template) or os.path.splitdrive(subfolder_template)[0]:
        raise ValueError("path_template must be a subfolder inside the ComfyUI output directory")

    components = []
    for raw_component in subfolder_template.replace("\\", "/").split("/"):
        component = raw_component.strip()
        if not component or component == ".":
            continue
        if component == "..":
            raise ValueError("path_template cannot contain path traversal")
        components.append(_sanitize_filename_component(component))

    output_root = os.path.abspath(output_dir)
    full_output_folder = os.path.abspath(os.path.join(output_root, *components))

    if os.path.commonpath((output_root, full_output_folder)) != output_root:
        raise ValueError("path_template resolves outside the ComfyUI output directory")

    return full_output_folder, "/".join(components)


def _image_dimensions(image) -> tuple[int, int]:
    shape = getattr(image, "shape", None)
    if shape is None or len(shape) < 2:
        raise ValueError("IMAGE entries must expose height and width dimensions")
    return int(shape[1]), int(shape[0])


def _template_has_counter(template: str) -> bool:
    return "{counter}" in template or "%counter%" in template


def _metadata_payload(prompt=None, extra_pnginfo=None) -> dict[str, str] | None:
    if getattr(args, "disable_metadata", False):
        return None

    metadata = {}
    if prompt is not None:
        metadata["prompt"] = json.dumps(prompt)
    if extra_pnginfo is not None:
        for key, value in extra_pnginfo.items():
            metadata[key] = json.dumps(value)

    return metadata or None


def _save_png_image(image, path: str, metadata_payload: dict[str, str] | None, compress_level: int) -> None:
    import numpy as np
    from PIL import Image
    from PIL.PngImagePlugin import PngInfo

    image_array = image.cpu().numpy() if hasattr(image, "cpu") else np.asarray(image)
    image_array = 255.0 * image_array
    pil_image = Image.fromarray(np.clip(image_array, 0, 255).astype(np.uint8))

    pnginfo = None
    if metadata_payload is not None:
        pnginfo = PngInfo()
        for key, value in metadata_payload.items():
            pnginfo.add_text(key, value)

    pil_image.save(path, pnginfo=pnginfo, compress_level=int(compress_level))


class SaveImageDynamic:
    """Save IMAGE batches with dynamic output subfolders and filename tokens."""

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("saved_paths",)
    FUNCTION = "save_images"
    OUTPUT_NODE = True
    CATEGORY = "LFGG / Image"

    DESCRIPTION = (
        "Saves images under ComfyUI's output directory with dynamic path and filename templates.\n\n"
        "- Use {model}, {date}, {time}, {datetime}, {width}, {height}, {batch}, {counter}\n"
        "- Also supports percent tokens such as %model%, %width%, %batch_num%, and %counter%\n"
        "- Connect model_name from LFGG Model Name From Model for model-aware filenames\n"
        "- path_template is always treated as an output subfolder, not an absolute path"
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "Image batch to save as PNG files."}),
                "path_template": (
                    "STRING",
                    {
                        "default": "runs/{model}/{date}",
                        "multiline": False,
                        "tooltip": "Output subfolder under ComfyUI output. Supports dynamic tokens.",
                    },
                ),
                "filename_template": (
                    "STRING",
                    {
                        "default": "{model}_{datetime}_{batch}",
                        "multiline": False,
                        "tooltip": "Filename stem without extension. Supports dynamic tokens.",
                    },
                ),
            },
            "optional": {
                "model_name": (
                    "STRING",
                    {
                        "forceInput": True,
                        "tooltip": "Optional model name string, usually from LFGG Model Name From Model.",
                    },
                ),
                "compress_level": (
                    "INT",
                    {
                        "default": 4,
                        "min": 0,
                        "max": 9,
                        "step": 1,
                        "tooltip": "PNG compression level. 0 is fastest, 9 is smallest.",
                    },
                ),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    def save_images(
        self,
        images,
        path_template: str = "runs/{model}/{date}",
        filename_template: str = "{model}_{datetime}_{batch}",
        model_name: str = "",
        compress_level: int = 4,
        prompt=None,
        extra_pnginfo=None,
    ):
        output_dir = folder_paths.get_output_directory()
        metadata = _metadata_payload(prompt=prompt, extra_pnginfo=extra_pnginfo)
        counter = 1
        saved_paths = []
        ui_images = []

        if len(images) == 0:
            raise ValueError("images must contain at least one IMAGE")

        for batch_number, image in enumerate(images):
            width, height = _image_dimensions(image)
            counter, full_path, filename, subfolder = self._next_available_path(
                output_dir=output_dir,
                path_template=path_template,
                filename_template=filename_template,
                model_name=model_name,
                width=width,
                height=height,
                batch_number=batch_number,
                counter=counter,
            )

            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            _save_png_image(image, full_path, metadata, int(compress_level))

            saved_paths.append(os.path.abspath(full_path))
            ui_images.append({"filename": filename, "subfolder": subfolder, "type": "output"})
            counter += 1

        return {"ui": {"images": ui_images}, "result": ("\n".join(saved_paths),)}

    def _next_available_path(
        self,
        *,
        output_dir: str,
        path_template: str,
        filename_template: str,
        model_name: str,
        width: int,
        height: int,
        batch_number: int,
        counter: int,
    ) -> tuple[int, str, str, str]:
        has_counter = _template_has_counter(path_template) or _template_has_counter(filename_template)

        while True:
            values = _token_values(
                model_name=model_name,
                width=width,
                height=height,
                batch=batch_number,
                counter=counter,
            )
            expanded_subfolder = _expand_template(path_template, values)
            output_folder, subfolder = _resolve_output_folder(output_dir, expanded_subfolder)

            expanded_filename = _expand_template(filename_template, values)
            filename_stem = _sanitize_filename_component(expanded_filename)
            if filename_stem.lower().endswith(".png"):
                filename_stem = filename_stem[:-4].rstrip(" ._") or "image"

            if has_counter:
                filename = f"{filename_stem}.png"
            else:
                filename = f"{filename_stem}_{values['counter']}_.png"

            full_path = os.path.abspath(os.path.join(output_folder, filename))
            if not os.path.exists(full_path):
                return counter, full_path, filename, subfolder

            counter += 1


NODE_CLASS_MAPPINGS = {
    "LfggSaveImageDynamic": SaveImageDynamic,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LfggSaveImageDynamic": "LFGG Save Image Dynamic",
}

__all__ = ["SaveImageDynamic", "NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

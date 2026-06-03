"""Extract the source model name from an upstream MODEL connection."""

from __future__ import annotations

from functools import lru_cache

UNKNOWN_MODEL_NAME = "unknown_model"

SUPPORTED_LOADER_FIELDS = {
    "CheckpointLoader": "ckpt_name",
    "CheckpointLoaderSimple": "ckpt_name",
    "unCLIPCheckpointLoader": "ckpt_name",
    "ImageOnlyCheckpointLoader": "ckpt_name",
    "DiffusersLoader": "model_path",
    "UNETLoader": "unet_name",
}


def _is_link(value) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 2
        and isinstance(value[0], str)
        and isinstance(value[1], (int, float))
    )


def _normalize_model_source_name(source_value: str) -> str:
    normalized = source_value.replace("\\", "/").strip().strip("/")
    if not normalized:
        return UNKNOWN_MODEL_NAME

    filename = normalized.split("/")[-1].strip()
    if not filename:
        return UNKNOWN_MODEL_NAME

    stem = filename.rsplit(".", 1)[0] if "." in filename else filename
    return stem or UNKNOWN_MODEL_NAME


@lru_cache(maxsize=None)
def _lookup_input_type(class_type: str, input_name: str):
    try:
        import nodes as comfy_nodes
        from comfy_execution.graph import get_input_info
    except Exception:
        return None

    class_def = comfy_nodes.NODE_CLASS_MAPPINGS.get(class_type)
    if class_def is None:
        return None

    input_type, _, _ = get_input_info(class_def, input_name)
    return input_type


def _is_model_input(class_type: str, input_name: str) -> bool:
    input_type = _lookup_input_type(class_type, input_name)
    if input_type is not None:
        return input_type == "MODEL"

    lowered = input_name.lower()
    return lowered == "model" or lowered.startswith("model") or lowered.endswith("model")


def _resolve_model_name_from_graph(dynprompt, unique_id: str, input_name: str = "model") -> str:
    if dynprompt is None or not unique_id:
        return UNKNOWN_MODEL_NAME

    try:
        node_info = dynprompt.get_node(unique_id)
    except Exception:
        return UNKNOWN_MODEL_NAME

    link = node_info.get("inputs", {}).get(input_name)
    if not _is_link(link):
        return UNKNOWN_MODEL_NAME

    return _resolve_model_name_from_node(dynprompt, link[0], visited=set())


def _resolve_model_name_from_node(dynprompt, node_id: str, visited: set[str]) -> str:
    if node_id in visited:
        return UNKNOWN_MODEL_NAME
    visited.add(node_id)

    try:
        node_info = dynprompt.get_node(node_id)
    except Exception:
        return UNKNOWN_MODEL_NAME

    class_type = node_info.get("class_type", "")
    inputs = node_info.get("inputs", {})

    source_field = SUPPORTED_LOADER_FIELDS.get(class_type)
    if source_field is not None:
        source_value = inputs.get(source_field)
        if isinstance(source_value, str):
            return _normalize_model_source_name(source_value)
        return UNKNOWN_MODEL_NAME

    upstream_model_nodes = []
    for current_input_name, current_value in inputs.items():
        if not _is_link(current_value):
            continue
        if not _is_model_input(class_type, current_input_name):
            continue
        upstream_model_nodes.append(current_value[0])

    unique_upstream_nodes = list(dict.fromkeys(upstream_model_nodes))
    if len(unique_upstream_nodes) != 1:
        return UNKNOWN_MODEL_NAME

    return _resolve_model_name_from_node(dynprompt, unique_upstream_nodes[0], visited)


class ModelNameFromModel:
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("model_name",)
    FUNCTION = "run"
    CATEGORY = "LFGG / Text"
    DESCRIPTION = (
        "Trace the incoming MODEL connection back to a supported loader and return the model filename stem.\n\n"
        "- Follows upstream MODEL links instead of inspecting the runtime model object\n"
        "- Returns only the filename stem, not subfolders, extension, or absolute paths\n"
        "- Unsupported or ambiguous graphs return unknown_model"
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL", {"tooltip": "Model connection to trace back to its loader source."}),
            },
            "hidden": {
                "dynprompt": "DYNPROMPT",
                "unique_id": "UNIQUE_ID",
            },
        }

    def run(self, model, dynprompt=None, unique_id=None):
        _ = model
        model_name = _resolve_model_name_from_graph(dynprompt, unique_id)
        return (model_name,)


NODE_CLASS_MAPPINGS = {
    "LfggModelNameFromModel": ModelNameFromModel,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LfggModelNameFromModel": "LFGG Model Name From Model",
}

"""Image batch selection node for LFGG workflows."""

from __future__ import annotations


SELECTION_MODES = ("last", "first", "index")


def _batch_size(images) -> int:
    shape = getattr(images, "shape", None)
    if shape is None or len(shape) != 4:
        raise ValueError("IMAGE tensors must be 4D: (batch, height, width, channels)")

    batch = int(shape[0])
    if batch < 1:
        raise ValueError("images must contain at least one IMAGE")

    return batch


def _selection_index(mode: str, batch_index: int, batch_size: int) -> int:
    if mode == "first":
        return 0
    if mode == "last":
        return batch_size - 1
    if mode == "index":
        requested_index = max(0, int(batch_index))
        return min(requested_index, batch_size - 1)

    raise ValueError(f"mode must be one of: {', '.join(SELECTION_MODES)}")


def _clone_or_copy(value):
    clone = getattr(value, "clone", None)
    if callable(clone):
        return clone()

    copy = getattr(value, "copy", None)
    if callable(copy):
        return copy()

    return value


class ImageBatchSelect:
    """Select one image from an IMAGE batch while preserving batch shape."""

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "select_image"
    CATEGORY = "LFGG / Image"
    DESCRIPTION = (
        "Selects a single image from an IMAGE batch.\n\n"
        "- mode=last returns the final image in the batch\n"
        "- mode=first returns the first image in the batch\n"
        "- mode=index returns batch_index, clamped to the last available image\n"
        "- Output remains an IMAGE batch with one image"
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "Input IMAGE batch to select from."}),
                "mode": (
                    SELECTION_MODES,
                    {
                        "default": "last",
                        "tooltip": "Select the first image, last image, or a zero-based batch_index.",
                    },
                ),
                "batch_index": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 4095,
                        "step": 1,
                        "tooltip": "Zero-based image index used when mode is index.",
                    },
                ),
            }
        }

    def select_image(self, images, mode: str = "last", batch_index: int = 0):
        batch = _batch_size(images)
        selected_index = _selection_index(str(mode), int(batch_index), batch)
        selected = images[selected_index : selected_index + 1]
        return (_clone_or_copy(selected),)


NODE_CLASS_MAPPINGS = {
    "LfggImageBatchSelect": ImageBatchSelect,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LfggImageBatchSelect": "LFGG Image Batch Select",
}

__all__ = ["ImageBatchSelect", "NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

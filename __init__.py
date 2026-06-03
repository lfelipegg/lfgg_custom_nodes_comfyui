# File: custom_nodes/lfgg_nodes/__init__.py

from . import latent_size_by_ratio
from . import image_resolution_by_ratio
from . import pixel_budget_latent_size
from . import prompt_library
from . import prompt_wildcard
from . import lora_loader_by_path

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

NODE_CLASS_MAPPINGS.update(latent_size_by_ratio.NODE_CLASS_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(latent_size_by_ratio.NODE_DISPLAY_NAME_MAPPINGS)

NODE_CLASS_MAPPINGS.update(image_resolution_by_ratio.NODE_CLASS_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(image_resolution_by_ratio.NODE_DISPLAY_NAME_MAPPINGS)

NODE_CLASS_MAPPINGS.update(pixel_budget_latent_size.NODE_CLASS_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(pixel_budget_latent_size.NODE_DISPLAY_NAME_MAPPINGS)
NODE_CLASS_MAPPINGS.update(prompt_library.NODE_CLASS_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(prompt_library.NODE_DISPLAY_NAME_MAPPINGS)
NODE_CLASS_MAPPINGS.update(prompt_wildcard.NODE_CLASS_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(prompt_wildcard.NODE_DISPLAY_NAME_MAPPINGS)
NODE_CLASS_MAPPINGS.update(lora_loader_by_path.NODE_CLASS_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(lora_loader_by_path.NODE_DISPLAY_NAME_MAPPINGS)

WEB_DIRECTORY = "./web"

__all__ = []
__all__ += getattr(latent_size_by_ratio, "__all__", [])
__all__ += getattr(image_resolution_by_ratio, "__all__", [])
__all__ += getattr(pixel_budget_latent_size, "__all__", [])
__all__ += getattr(prompt_library, "__all__", [])
__all__ += getattr(prompt_wildcard, "__all__", [])
__all__ += getattr(lora_loader_by_path, "__all__", [])
__all__ += ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]

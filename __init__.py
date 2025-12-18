# File: custom_nodes/lfgg_nodes/__init__.py

from . import latent_size_by_ratio
from . import image_resolution_by_ratio
from . import pixel_budget_latent_size

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

NODE_CLASS_MAPPINGS.update(latent_size_by_ratio.NODE_CLASS_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(latent_size_by_ratio.NODE_DISPLAY_NAME_MAPPINGS)

NODE_CLASS_MAPPINGS.update(image_resolution_by_ratio.NODE_CLASS_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(image_resolution_by_ratio.NODE_DISPLAY_NAME_MAPPINGS)

NODE_CLASS_MAPPINGS.update(pixel_budget_latent_size.NODE_CLASS_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(pixel_budget_latent_size.NODE_DISPLAY_NAME_MAPPINGS)

__all__ = []
__all__ += getattr(latent_size_by_ratio, "__all__", [])
__all__ += getattr(image_resolution_by_ratio, "__all__", [])
__all__ += getattr(pixel_budget_latent_size, "__all__", [])

# LFGG Node Catalog
- **LFGG Latent Size by Ratio** - Compute ratio-correct width/height pairs and allocate matching latent tensors with optional custom ratios, divisibility control, batching, plus a live ratio preview box.
- **LFGG Image Resolution by Ratio** - Rescale an IMAGE input to a target max size, snap to divisible-by requirements, and emit a matching zero latent plus original/new dimension metadata.
- **LFGG Pixel Budget Latent Size** - Clamp an IMAGE-derived aspect ratio to a pixel budget, snap to safe latent-friendly multiples, and output the resized width/height plus a zeroed latent tensor.
- **LFGG Prompt Library** - Browse stored prompt snippets under a configurable folder and emit the selected text to downstream nodes.
- **LFGG Prompt Wildcard** - Expand inline `{a|b}` and `__file__` wildcards into randomized prompt text using a seed.
- **LFGG Load LoRA (Path)** - Load a LoRA from a specific subfolder under `loras/` with a filtered dropdown.

# LFGG Node Catalog
- **LFGG Latent Size by Ratio** - Compute ratio-correct width/height pairs and allocate matching latent tensors with optional custom ratios, divisibility control, batching, plus a live ratio preview box.
- **LFGG Image Resolution by Ratio** - Rescale an IMAGE input to a target max size, snap to divisible-by requirements, and emit a matching zero latent plus original/new dimension metadata.
- **LFGG Image Batch Select** - Extract the first, last, or indexed image from an IMAGE batch while preserving a one-image batch output.
- **LFGG Pixel Budget Latent Size** - Clamp an IMAGE-derived aspect ratio to a pixel budget, snap to safe latent-friendly multiples, and output the resized width/height plus a zeroed latent tensor.
- **LFGG Prompt Library** - Browse stored prompt snippets under a configurable folder and emit the selected text to downstream nodes.
- **LFGG Prompt Wildcard** - Expand inline `{a|b}` and `__file__` wildcards into randomized prompt text using a seed.
- **LFGG Load LoRA (Path)** - Load a LoRA from a specific subfolder under `loras/` with a filtered dropdown.
- **LFGG Model Name From Model** - Trace a `MODEL` connection back to a supported loader and emit the source filename stem as text.
- **LFGG Save Image Dynamic** - Save IMAGE batches under ComfyUI's output directory with dynamic path/name tokens, model-name input, UI previews, and absolute saved path output.

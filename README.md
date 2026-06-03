# LFGG Custom Nodes for ComfyUI

Utility nodes that make it easier to keep Stable Diffusion workflows on-model with clean resolution math, predictable aspect ratios, and latent tensors that are sized correctly from the start. Everything inside this folder follows the registration and documentation guide in `AGENTS.md`.

## Highlights
- Resolution-first nodes: derive latents from aspect ratios, pixel budgets, or the size of incoming images.
- Battle-tested metadata: every node exposes tooltips, sensible defaults, and divisibility guards to stay sampler-friendly.
- Documentation baked in: each node ships with a dedicated file inside `docs/` plus a quick blurb in `docs/nodes.md`.

## Installation
1. Clone or copy `lfgg_nodes` into `ComfyUI/custom_nodes/` (the folder you are looking at now).
2. Launch or reload ComfyUI; it will auto-discover any modules exported in `lfgg_nodes/__init__.py`.
3. Search the graph editor for the `LFGG / ...` categories to drop nodes into a workflow.

## Provided Nodes
| Node | Category | What it does | Docs |
| --- | --- | --- | --- |
| **LFGG Latent Size by Ratio** | `LFGG / Latents` | Turns an aspect-ratio preset (or custom values) plus a base size into width/height integers and an empty `LATENT`, honoring divisibility constraints and optional batching. | [`docs/latent_size_by_ratio.md`](docs/latent_size_by_ratio.md) |
| **LFGG Image Resolution by Ratio** | `LFGG / Image` | Reads the size of an `IMAGE`, caps the longest edge to `base_size`, snaps to `lcm(8, divisible_by)`, and emits a zeroed latent plus original/new dimensions. | [`docs/image_resolution_by_ratio.md`](docs/image_resolution_by_ratio.md) |
| **LFGG Pixel Budget Latent Size** | `LFGG / Image Size` | Preserves the aspect ratio from an `IMAGE` while scaling down so `width * height <= max_pixels`, returns the resized size, and allocates the matching latent tensor. | [`docs/pixel_budget_latent_size.md`](docs/pixel_budget_latent_size.md) |
| **LFGG Prompt Library** | `LFGG / Text` | Browses prompt snippet files from a configurable folder (see `config.ini`) and emits the selected file contents as a `STRING`. | [`docs/prompt_library.md`](docs/prompt_library.md) |
See [`docs/nodes.md`](docs/nodes.md) for a catalog-style overview.

## Typical Workflows
- **Latent-first text-to-image** – Use *Latent Size by Ratio* at the top of a graph to set `width/height` for your sampler and skip separate “Empty Latent Image” nodes.
- **Image resizing with metadata** – Combine *Image Resolution by Ratio* with upscalers or ControlNet branches to clamp camera assets without guessing divisibility-safe numbers.
- **VRAM-aware batches** – Drop *Pixel Budget Latent Size* before image-to-image or video pipelines to keep resolutions inside a known pixel budget.

## Development Notes
- Follow the conventions documented in [`AGENTS.md`](AGENTS.md): snake_case module names, `Lfgg` IDs, `LFGG ...` display names, and category strings under `LFGG / ...`.
- Export each module in `__init__.py`, keep `NODE_CLASS_MAPPINGS` and `NODE_DISPLAY_NAME_MAPPINGS` synchronized, and add docs in `docs/<module>.md` plus an entry in `docs/nodes.md`.
- Frontend extensions (when needed) live under `web/` and are exposed to ComfyUI via `WEB_DIRECTORY` in `__init__.py`.
- Validate ranges via `INPUT_TYPES` metadata (min/max/step/tooltips) instead of runtime asserts wherever possible.
- Before shipping a change, verify it in ComfyUI and run a lightweight `python -m compileall .` to catch syntax errors.
- If ComfyUI shows "Invalid workflow against zod schema: Invalid aux_id", ComfyUI-Manager is attaching `aux_id` from the first git remote it finds; make sure the first remote URL is parseable as `https://github.com/<owner>/<repo>` (or add a separate remote for that).

## Need Another Node?
Use the checklist at the bottom of `AGENTS.md`:
1. Create a new module inside `lfgg_nodes/` using snake_case.
2. Copy the class structure (constants, `INPUT_TYPES`, `RETURN_TYPES`, `FUNCTION`, implementation).
3. Document inputs/outputs/constraints, export the module, and update `docs/nodes.md`.
4. Mention manual test coverage (a saved workflow or notes) in your commit or PR description.

Keeping these steps consistent ensures LFGG nodes stay recognizable, conflict-free, and easy to maintain across different ComfyUI installations.

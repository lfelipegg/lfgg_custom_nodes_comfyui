# LFGG Custom Nodes Agent Guide

This document captures the conventions and lightweight processes we follow when creating or updating ComfyUI nodes in `lfgg_nodes`. Treat it as the checklist the "agent" inside your editor should keep nearby.

## Repository Snapshot
- `__init__.py` exposes every node submodule via `from .<module> import *`. Import new node modules here so ComfyUI can discover them.
- `latent_size_by_ratio.py` shows the current pattern: declare a node class, define metadata constants, and finish with `NODE_CLASS_MAPPINGS` and `NODE_DISPLAY_NAME_MAPPINGS`.
- `docs/` stores node documentation. Each node gets a dedicated Markdown file plus an entry in `docs/nodes.md`.
- `.gitignore` is already configured for common Python artifacts; keep it updated when new tooling is added.

## Naming & Registration Rules
Keeping our namespace unique prevents conflicts with other custom-pack repositories installed in ComfyUI.
- **Node ID key** (the key inside `NODE_CLASS_MAPPINGS`) **must start with `Lfgg`**. Example: `"LfggLatentSizeByRatio": LatentSizeByRatio`.
- **Display names** **must start with `LFGG`** and quickly describe the feature, e.g. `"LFGG Latent Size by Ratio"`.
- **Class names** stay readable PascalCase and usually mirror the display name without the prefix.
- **Category strings** should live under the `LFGG / ...` tree so all nodes stay grouped inside the ComfyUI UI.
- Export every new module in `__init__.py` and keep `NODE_CLASS_MAPPINGS` plus `NODE_DISPLAY_NAME_MAPPINGS` synchronized.

## Documentation Requirements
- Every node module must have a Markdown file in `docs/` that mirrors the Python filename (for example `latent_size_by_ratio.py` -> `docs/latent_size_by_ratio.md`). Create it if it does not exist.
- Each node doc should explain the purpose, show all inputs/outputs (tables or bullet lists are fine), illustrate a usage example or workflow snippet, and highlight any constraints such as divisibility or batching limits.
- Add a concise bullet (node name + one-line summary) to `docs/nodes.md` whenever you add or change a node so readers can scan the catalog quickly.
- When behavior changes, update both the node-specific doc and the summary entry.

## Coding Guidelines
- Follow the structure from `LatentSizeByRatio`: constants up top, `INPUT_TYPES`/`RETURN_TYPES`/`RETURN_NAMES`, the callable `FUNCTION`, and the implementation method.
- Keep `DESCRIPTION` strings informative so the node tooltip teaches users how to use it; line breaks become bullet-style lines inside ComfyUI.
- Use torch or comfy APIs for tensors/latents; keep any device assumptions explicit (for example `device="cpu"`).
- Validate input ranges via the metadata dictionaries (min/max/step/tooltips) instead of ad hoc logic whenever possible.
- Keep tensors divisible by downstream requirements (for example latent channels multiple of 8) and document any hidden constraints.
- Prefer small helper functions above the class definition if logic grows complex.

## Testing & QA Flow
1. Implement or modify the node.
2. Run the node inside ComfyUI with a minimal workflow to verify inputs, outputs, and metadata appear correctly.
3. Run a quick `python -m compileall .` or lint (ruff, mypy, etc.) before committing when available.
4. Update this guide whenever you introduce a new pattern (for example custom resource loaders or caching helpers).

## New Node Checklist
- [ ] File created under `lfgg_nodes/` using `snake_case`.
- [ ] Node class implemented with docstrings and `DESCRIPTION`.
- [ ] `INPUT_TYPES`, outputs, and batch handling documented.
- [ ] `CATEGORY` starts with `LFGG /`.
- [ ] `NODE_CLASS_MAPPINGS` key uses the `Lfgg` prefix.
- [ ] `NODE_DISPLAY_NAME_MAPPINGS` value starts with `LFGG`.
- [ ] Module exported in `__init__.py`.
- [ ] Dedicated doc created or updated at `docs/<node_name>.md` with full details.
- [ ] Short summary bullet added or updated in `docs/nodes.md`.
- [ ] Manual test in ComfyUI workflow saved (or at least noted in commit message).

Keeping these conventions consistent ensures users installing multiple node packs never collide with our IDs and can recognize LFGG utilities instantly.

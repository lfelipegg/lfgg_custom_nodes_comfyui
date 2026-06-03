Below is a **clean, fully rewritten AGENTS.md**, integrating the suggested improvements while preserving your original intent, tone, and structure. It stays practical, ComfyUI-specific, and agent-friendly.

---

# LFGG Custom Nodes — Agent Guide

This document defines the conventions, constraints, and lightweight processes used when creating or updating ComfyUI custom nodes in `lfgg_nodes`.
Treat it as the authoritative checklist the editor agent should follow before, during, and after making changes.

---

## Repository Structure

* `__init__.py`
  Exposes every node module via `from .<module> import *`.
  **Every new node module must be imported here** for ComfyUI discovery.

* `*.py` node modules
  Each file defines one or more node classes plus:

  * `NODE_CLASS_MAPPINGS`
  * `NODE_DISPLAY_NAME_MAPPINGS`

* `docs/`

  * One Markdown file per node (same filename as the Python module).
  * `docs/nodes.md` contains a catalog-style summary of all nodes.

* `examples/` (recommended)
  Minimal ComfyUI workflow JSONs used for manual testing and regression checks.

* `.gitignore`
  Keep updated when introducing new tooling or caches.

---

## Naming & Registration Rules

To avoid collisions with other ComfyUI node packs:

* **Node ID keys** (in `NODE_CLASS_MAPPINGS`)
  Must start with `Lfgg`
  Example:

  ```python
  "LfggLatentSizeByRatio": LatentSizeByRatio
  ```

* **Display names**
  Must start with `LFGG` and describe the function clearly.
  Example:
  `LFGG Latent Size by Ratio`

* **Class names**
  PascalCase, readable, usually matching the display name without the prefix.

* **Categories**
  Must live under the `LFGG / ...` tree so nodes stay grouped in the UI.

* `NODE_CLASS_MAPPINGS` and `NODE_DISPLAY_NAME_MAPPINGS` must always stay in sync.

---

## ComfyUI Constraints & Gotchas

These rules prevent subtle UI or runtime bugs:

* `INPUT_TYPES` schemas must match ComfyUI expectations exactly.
* `CHOICE` inputs **must be lists/tuples**, never dicts.
* Default values must exist in the choice list.
* If an input is conditionally ignored (e.g. “Custom”), document it explicitly.
* Output names and output types are **part of the public API**.

  * Changing them is a breaking change → create a new Node ID.
* Native nodes **cannot embed custom UI previews** (buttons, text panels, etc.).

  * Any “preview” must be implemented via standard outputs or helper nodes.

---

## Documentation Requirements

Every node must be documented.

* Create or update `docs/<node_name>.md`:

  * Purpose and overview
  * Inputs and outputs (tables preferred)
  * Constraints (divisibility, batching, device assumptions)
  * Example usage or workflow snippet

* Update `docs/nodes.md`:

  * Add or update a one-line summary entry for the node

* When behavior changes:

  * Update both the node doc and the catalog entry

Documentation is not optional; it ships with the node.

---

## Coding Guidelines

* Follow the established structure:

  1. Constants and presets
  2. Node class definition
  3. `INPUT_TYPES`, `RETURN_TYPES`, `RETURN_NAMES`
  4. `FUNCTION`
  5. Implementation method

* `DESCRIPTION` strings should:

  * Be concise but instructive
  * Use line breaks (rendered as bullets in ComfyUI)
  * Explain non-obvious behavior

* Prefer metadata validation (min/max/step/tooltips) over ad hoc checks.

* Be explicit about device placement (`cpu` / `cuda`).

* Respect downstream constraints (e.g. multiples of 8 or 16) and document them.

* If logic grows complex, extract helper functions above the class.

---

## UI / UX Consistency Rules

To keep the node pack predictable and user-friendly:

* Prefer `CHOICE` over free text whenever the domain is bounded.
* Group related inputs via naming (`ratio_*`, `latent_*`, `preview_*`).
* Defaults must always produce a valid output.
* Avoid “magic” behavior—if something auto-adjusts, explain it in `DESCRIPTION`.

---

## Error Handling Policy

* Never crash ComfyUI on bad user input if recovery is possible.
* Clamp, normalize, or fallback instead of failing silently.
* Raise explicit errors only when continuing would corrupt results.
* Use warnings (not prints) when auto-correcting values.

---

## Performance & Resource Guidelines

* Avoid reallocating tensors unnecessarily.
* Cache derived values when inputs do not change.
* Be clear about CPU vs GPU execution cost.
* Document VRAM-sensitive behavior in the node doc.

---

## Versioning, Compatibility & Deprecation

* Nodes follow **behavioral stability**, not strict semantic versioning.
* Rules:

  * Breaking behavior change → **new Node ID**
  * UI or metadata-only change → same Node ID
* Deprecated inputs:

  * Must remain for at least one release cycle
  * Must be clearly marked in `DESCRIPTION`
  * Migration steps go in the node doc

---

## Testing & QA Flow

1. Implement or modify the node.
2. Test inside ComfyUI using a minimal workflow.
3. Save example workflows under `examples/` when possible.
4. Run `python -m compileall .` or lint tools when available.
5. Update docs and this guide if a new pattern is introduced.

---

## New Node Checklist

* [ ] File created under `lfgg_nodes/` using `snake_case`
* [ ] Node class implemented with docstrings and `DESCRIPTION`
* [ ] `INPUT_TYPES`, outputs, and batch behavior defined
* [ ] `CATEGORY` starts with `LFGG /`
* [ ] `NODE_CLASS_MAPPINGS` key starts with `Lfgg`
* [ ] `NODE_DISPLAY_NAME_MAPPINGS` value starts with `LFGG`
* [ ] Module exported in `__init__.py`
* [ ] `docs/<node_name>.md` created or updated
* [ ] Summary entry updated in `docs/nodes.md`
* [ ] Node tested in ComfyUI (workflow saved or noted)

---

## Agent-Specific Rules

When acting as the editor agent:

* Do not invent undocumented ComfyUI APIs.
* Mirror existing node patterns before introducing new ones.
* Never modify mappings, code, or docs in isolation—update all together.
* Ask before introducing new dependencies or architectural patterns.
* Prefer consistency over cleverness.

---

## Non-Goals

* No custom ComfyUI UI widgets
* No monkey-patching ComfyUI internals
* No hidden side effects or global state

---

Keeping these rules consistent ensures LFGG nodes remain predictable, stable, and interoperable alongside other custom node packs.

# LFGG Custom Nodes Agent Guide

This document captures the conventions and lightweight processes we follow when creating or updating ComfyUI nodes in `lfgg_nodes`. Treat it as the checklist the "agent" inside your editor should keep nearby.

## Repository Snapshot
- `__init__.py` exposes every node submodule via `from .<module> import *`. Import new node modules here so ComfyUI can discover them.
- `latent_size_by_ratio.py` shows the current pattern: declare a node class, define metadata constants, and finish with `NODE_CLASS_MAPPINGS` and `NODE_DISPLAY_NAME_MAPPINGS`.
- `docs/` stores node documentation. Each node gets a dedicated Markdown file plus an entry in `docs/nodes.md`.
- `.gitignore` is already configured for common Python artifacts; keep it updated when new tooling is added.

## Examples & References
Use the `/examples` folder as a reference source depending on the task at hand.
- `/examples/ComfyUI_frontend_vue_basic-main`: works for the UI of the node.
- `/examples/ComfyUI-React-Extension-Template-main`: works for the UI of ComfyUI.
- `/examples/cookiecutter-comfy-extension-main`: general node reference.
- `/examples/ComfyUI_windows_portable`: the ComfyUI library (without the Python dependencies).

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

## Agents

The following agents define who is responsible for what during development. Agents must operate within their declared scope and must not silently override responsibilities owned by another agent.

### 1. Node Planning Agent (Mandatory when proposing new nodes)

**Purpose**  
Assess the need for a new node, capture requirements, and define the initial design before implementation starts.

**Responsibilities**
- Identify the user problem the node solves and validate it against existing nodes
- Draft inputs, outputs, and expected behavior at a high level
- Outline dependencies, device constraints, and potential risks
- Coordinate with docs and QA to ensure feasibility

**Must Not**
- Start implementation or change existing code
- Commit to incompatible requirements without technical validation

**Required When**
- Proposing a brand-new node concept
- Replacing or significantly expanding an existing node

### 2. Node Authoring Agent (Mandatory)

**Purpose**  
Implement new ComfyUI nodes or extend existing ones while strictly following LFGG conventions.

**Responsibilities**
- Create node classes and module files
- Define `INPUT_TYPES`, outputs, categories, and mappings
- Enforce naming, prefix, and category rules
- Write accurate `DESCRIPTION` text
- Ensure defaults produce valid outputs

**Must Not**
- Invent undocumented ComfyUI APIs
- Change existing Node IDs without instruction

**Required When**
- Adding a new node
- Modifying node behavior or outputs

### 3. UI & Metadata Consistency Agent (Mandatory)

**Purpose**  
Guarantee that nodes render and behave correctly in the ComfyUI interface.

**Responsibilities**
- Validate `INPUT_TYPES` schemas
- Ensure `CHOICE` inputs render as selects
- Verify defaults exist in allowed ranges
- Confirm conditional inputs are clearly documented
- Enforce `LFGG / ...` category structure

**Must Not**
- Modify execution logic
- Change output types or names

**Required When**
- Any input, output, or UI metadata changes

### 4. Documentation Sync Agent (Mandatory)

**Purpose**  
Keep documentation fully aligned with code.

**Responsibilities**
- Create or update `docs/<node>.md`
- Update `docs/nodes.md` summary entries
- Verify documented inputs/outputs match the code
- Flag undocumented constraints or behavior

**Must Not**
- Change code logic
- Infer behavior not present in implementation

**Required When**
- Any node is added or modified

### 5. QA & Workflow Validation Agent (Mandatory)

**Purpose**  
Ensure nodes load and execute correctly in real ComfyUI workflows.

**Responsibilities**
- Test nodes inside ComfyUI
- Validate inputs, outputs, and execution paths
- Test edge cases (min/max, custom modes, invalid inputs)
- Detect breaking vs non-breaking changes

**Must Not**
- Refactor or optimize code unless instructed
- Change Node IDs autonomously

**Required When**
- Before merging or publishing changes

### 6. Debugging Agent (Optional, use when fixing issues)

**Purpose**  
Reproduce and isolate failures (UI issues, runtime exceptions, wrong outputs) and drive fixes with minimal regressions.

**Responsibilities**
- Reproduce the issue with a minimal ComfyUI workflow
- Reduce the case to the smallest set of nodes and inputs
- Verify shapes/types/devices and common ComfyUI schema pitfalls
- Confirm the fix with both the minimal workflow and at least one realistic workflow
- Record troubleshooting notes (root cause + how to verify) in the PR/commit message or issue thread

**Must Not**
- Mask errors with silent fallbacks that change results unexpectedly
- Introduce new dependencies without approval
- Change public outputs or Node IDs unless explicitly required

**Use When**
- A node fails to load, throws exceptions, or produces incorrect results
- UI controls render incorrectly (choices, defaults, ranges)
- A change breaks existing workflows

### 7. Performance & Resource Agent (Optional)

**Purpose**  
Prevent unnecessary slowdowns and excessive VRAM usage.

**Responsibilities**
- Review tensor allocation patterns
- Identify unnecessary recomputation
- Flag VRAM-heavy operations
- Recommend caching or simplifications

**Must Not**
- Sacrifice correctness for speed
- Rewrite logic unless requested

**Use When**
- Nodes operate on latents or batches
- Performance regressions are suspected
- Introducing loops or large tensor ops

### 8. Compatibility & Migration Agent (Optional but strongly recommended)

**Purpose**  
Protect existing user workflows from silent breakage.

**Responsibilities**
- Identify breaking changes
- Recommend new Node IDs when required
- Draft deprecation and migration notes
- Ensure deprecated inputs remain usable

**Must Not**
- Remove deprecated inputs early
- Change mappings without approval

**Use When**
- Refactoring existing nodes
- Renaming inputs or outputs
- Changing behavior of released nodes

### 9. Release Readiness Agent (Optional)

**Purpose**  
Final verification before sharing or tagging a release.

**Responsibilities**
- Verify checklist completion
- Ensure mappings, exports, and docs are aligned
- Confirm example workflows load
- Detect missing or stale files

**Must Not**
- Introduce new features
- Change public APIs

**Use When**
- Publishing or distributing the node pack

### 10. Experimental / R&D Agent (Optional)

**Purpose**  
Explore new ideas without destabilizing stable nodes.

**Responsibilities**
- Prototype experimental node concepts
- Explore advanced ComfyUI patterns
- Isolate unstable or exploratory code
- Clearly mark experimental behavior

**Must Not**
- Ship experimental features as stable
- Modify released nodes directly

**Use When**
- Testing new concepts
- Risky or uncertain features

## Mandatory vs Optional Summary

**Mandatory Agents (Always Active)**
- Node Planning Agent (when proposing new nodes)
- Node Authoring Agent
- UI & Metadata Consistency Agent
- Documentation Sync Agent
- QA & Workflow Validation Agent

These agents form the minimum safety net. Skipping them risks broken UI, undocumented behavior, or unusable nodes.

**Optional Agents (Context-Driven)**
- Debugging Agent
- Performance & Resource Agent
- Compatibility & Migration Agent (strongly recommended for existing nodes)
- Release Readiness Agent
- Experimental / R&D Agent

## Recommended Agent Execution Order

```
Node Planning
 -> Node Authoring
 -> UI & Metadata Consistency
 -> QA & Workflow Validation
 -> (Optional) Debugging
 -> Documentation Sync
 -> (Optional) Performance Review
 -> (Optional) Compatibility & Migration
 -> (Optional) Release Readiness
```

Keeping these conventions consistent ensures users installing multiple node packs never collide with our IDs and can recognize LFGG utilities instantly.

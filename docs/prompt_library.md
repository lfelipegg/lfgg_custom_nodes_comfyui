# LFGG Prompt Library

Store prompt snippets on disk, browse them from inside ComfyUI, and emit the selected text to downstream nodes. This node is read-only by design; it previews existing files so you can copy or route their contents into other nodes.

## Configuration

- Edit `config.ini` next to the node files and set `prompt_library.library_path` to the folder that should hold prompts.
- Relative values resolve from the `lfgg_nodes` directory. The node creates the folder automatically the first time it runs.
- Every file in that folder (and its subfolders) is offered inside the selector as `subfolder/prompt.txt`.

## Inputs

| Name | Type | Notes |
| ---- | ---- | ----- |
| `selected_prompt` | select widget | Relative prompt file path pulled from the configured folder and all of its subdirectories. The node emits the file contents; use another viewer node if you need an on-screen preview. |

## Outputs

| Name | Type | Description |
| ---- | ---- | ----------- |
| `prompt` | `STRING` | The loaded prompt text mirrored to downstream nodes and the preview panel. |

## Workflow Tips

1. Configure `prompt_library.library_path` and drop text files anywhere under that directory tree.
2. Place the node, pick a prompt from the dropdown, and queue it to emit the file contents as a string.
3. Feed the output into CLIPTextEncode, prompt combiners, or a separate preview/utility node.
4. Restart ComfyUI (or reload the custom node) if you add or remove files and need the dropdown to refresh.

## Constraints & Notes

- Paths are sanitized to keep all reads inside the configured prompt directory.
- Outputs are plain strings, so you can feed them directly into text encoders or any node that accepts text.

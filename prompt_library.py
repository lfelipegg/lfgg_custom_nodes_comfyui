"""Prompt library node implementation."""

from __future__ import annotations

import configparser
from pathlib import Path
from typing import List

# ---- Configuration defaults ----
MODULE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = MODULE_DIR / "config.ini"
CONFIG_SECTION = "prompt_library"
CONFIG_KEY = "library_path"
DEFAULT_LIBRARY_SUBDIR = "prompts"
NO_SELECTION = "<select prompt>"


def _load_config() -> configparser.ConfigParser:
    """Read config.ini and make sure the prompt section exists."""

    parser = configparser.ConfigParser()
    if CONFIG_PATH.exists():
        parser.read(CONFIG_PATH, encoding="utf-8")
    if not parser.has_section(CONFIG_SECTION):
        parser.add_section(CONFIG_SECTION)
    if not parser[CONFIG_SECTION].get(CONFIG_KEY):
        parser[CONFIG_SECTION][CONFIG_KEY] = DEFAULT_LIBRARY_SUBDIR
        with CONFIG_PATH.open("w", encoding="utf-8") as fh:
            parser.write(fh)
    return parser


def _resolve_library_dir() -> Path:
    """Return the absolute prompt library directory, creating it if needed."""

    parser = _load_config()
    configured_path = parser.get(CONFIG_SECTION, CONFIG_KEY, fallback=DEFAULT_LIBRARY_SUBDIR).strip()
    base_path = Path(configured_path)
    if not base_path.is_absolute():
        base_path = (MODULE_DIR / base_path).resolve()
    base_path.mkdir(parents=True, exist_ok=True)
    return base_path


class PromptLibrary:
    """
    Browse stored prompt snippets and preview their contents.
    """

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "run"
    CATEGORY = "LFGG / Text"
    DESCRIPTION = (
        "Load prompt snippets from the configured library folder.\n\n"
        "- Uses config.ini[prompt_library]::library_path as the base folder\n"
        "- Lists files recursively so subfolder/prompt.txt stays accessible\n"
        "- Displays the file content as a preview text block\n"
        "- Returns the preview text so you can wire it directly to encoders"
    )

    _PROMPT_CHOICES: List[str] | None = None

    @classmethod
    def _discover_prompt_choices(cls) -> List[str]:
        base_dir = _resolve_library_dir()
        entries: List[str] = []
        for file_path in sorted(base_dir.rglob("*")):
            if file_path.is_file():
                entries.append(file_path.relative_to(base_dir).as_posix())
        return entries or [NO_SELECTION]

    @classmethod
    def _prompt_choices(cls) -> List[str]:
        if cls._PROMPT_CHOICES is None:
            cls._PROMPT_CHOICES = cls._discover_prompt_choices()
        return cls._PROMPT_CHOICES

    @classmethod
    def _invalidate_choices(cls) -> None:
        cls._PROMPT_CHOICES = None

    @classmethod
    def INPUT_TYPES(cls):  # noqa: N802 - ComfyUI API
        choices = cls._prompt_choices()
        choice_tuple = tuple(choices)
        default_choice = choice_tuple[0] if choice_tuple else NO_SELECTION
        return {
            "required": {},
            "optional": {
                "selected_prompt": (
                    choice_tuple,
                    {
                        "default": default_choice,
                        "tooltip": "Relative path of the prompt file whose contents should be emitted.",
                    },
                ),
            },
        }

    def run(
        self,
        selected_prompt: str = NO_SELECTION,
    ):
        base_dir = _resolve_library_dir()
        if not selected_prompt or selected_prompt == NO_SELECTION:
            return {"ui": {"text": ("",)}, "result": ("",)}

        text = self._read_prompt_file(base_dir, selected_prompt)
        return {"ui": {"text": (text,)}, "result": (text,)}

    def _read_prompt_file(self, base_dir: Path, relative_path: str) -> str:
        target = self._normalize_relative_path(relative_path)
        file_path = base_dir / target
        if not file_path.is_file():
            raise FileNotFoundError(f"Prompt file '{target}' was not found under {base_dir}")
        return file_path.read_text(encoding="utf-8")

    @staticmethod
    def _normalize_relative_path(path_value: str) -> str:
        normalized = path_value.replace("\\", "/").strip().strip("/")
        return normalized


# ---- Registration ----
NODE_CLASS_MAPPINGS = {
    "LfggPromptLibrary": PromptLibrary,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LfggPromptLibrary": "LFGG Prompt Library",
}

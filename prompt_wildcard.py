"""Prompt wildcard node implementation."""

from __future__ import annotations

import configparser
import random
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

MODULE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = MODULE_DIR / "config.ini"
CONFIG_SECTION = "prompt_library"
CONFIG_KEY = "wildcard_path"
DEFAULT_WILDCARD_SUBDIR = "wildcards"
NO_SELECTION = "<select wildcard>"
MAX_EXPANSION_PASSES = 128


def _load_config() -> configparser.ConfigParser:
    """Read config.ini and make sure the wildcard section exists."""

    parser = configparser.ConfigParser()
    if CONFIG_PATH.exists():
        parser.read(CONFIG_PATH, encoding="utf-8")
    if not parser.has_section(CONFIG_SECTION):
        parser.add_section(CONFIG_SECTION)
    if not parser[CONFIG_SECTION].get(CONFIG_KEY):
        parser[CONFIG_SECTION][CONFIG_KEY] = DEFAULT_WILDCARD_SUBDIR
        with CONFIG_PATH.open("w", encoding="utf-8") as fh:
            parser.write(fh)
    return parser


def _resolve_wildcard_dir() -> Path:
    """Return the absolute wildcard directory, creating it if needed."""

    parser = _load_config()
    configured_path = parser.get(CONFIG_SECTION, CONFIG_KEY, fallback=DEFAULT_WILDCARD_SUBDIR).strip()
    base_path = Path(configured_path)
    if not base_path.is_absolute():
        base_path = (MODULE_DIR / base_path).resolve()
    base_path.mkdir(parents=True, exist_ok=True)
    return base_path


def _normalize_relative_path(path_value: str) -> str:
    return path_value.replace("\\", "/").strip().strip("/")


def _candidate_wildcard_files(base_dir: Path, relative_path: str) -> Iterable[Path]:
    clean_path = _normalize_relative_path(relative_path)
    if not clean_path:
        return []
    path = Path(clean_path)
    if path.suffix:
        return [base_dir / path]
    return [base_dir / path, base_dir / f"{clean_path}.txt"]


def _read_wildcard_file(base_dir: Path, relative_path: str) -> List[str]:
    candidates = list(_candidate_wildcard_files(base_dir, relative_path))
    for candidate in candidates:
        if candidate.is_file():
            lines = candidate.read_text(encoding="utf-8").splitlines()
            entries: List[str] = []
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue
                if stripped.startswith("#") or stripped.startswith("//"):
                    continue
                entries.append(stripped)
            return entries
    raise FileNotFoundError(f"Wildcard file '{relative_path}' not found under {base_dir}")


def _discover_wildcard_choices() -> List[str]:
    base_dir = _resolve_wildcard_dir()
    entries: List[str] = []
    for file_path in sorted(base_dir.rglob("*")):
        if not file_path.is_file():
            continue
        rel_path = file_path.relative_to(base_dir).as_posix()
        if file_path.suffix.lower() == ".txt":
            rel_path = rel_path[: -len(file_path.suffix)]
        entries.append(rel_path)
    return entries or [NO_SELECTION]


def _split_choices(content: str) -> List[str]:
    parts: List[str] = []
    buf: List[str] = []
    depth = 0
    escape = False
    for ch in content:
        if escape:
            buf.append(ch)
            escape = False
            continue
        if ch == "\\":
            escape = True
            continue
        if ch == "{":
            depth += 1
            buf.append(ch)
            continue
        if ch == "}" and depth > 0:
            depth -= 1
            buf.append(ch)
            continue
        if ch == "|" and depth == 0:
            parts.append("".join(buf))
            buf = []
            continue
        buf.append(ch)
    parts.append("".join(buf))
    return parts


def _find_next_brace(text: str) -> Optional[Tuple[int, int]]:
    escape = False
    start = None
    depth = 0
    for idx, ch in enumerate(text):
        if escape:
            escape = False
            continue
        if ch == "\\":
            escape = True
            continue
        if ch == "{":
            if depth == 0:
                start = idx
            depth += 1
            continue
        if ch == "}" and depth > 0:
            depth -= 1
            if depth == 0 and start is not None:
                return start, idx
    return None


def _replace_wildcard_files(text: str, base_dir: Path) -> str:
    out: List[str] = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == "\\" and i + 1 < len(text):
            out.append(text[i : i + 2])
            i += 2
            continue
        if ch == "_" and i + 1 < len(text) and text[i + 1] == "_":
            end = i + 2
            while end + 1 < len(text):
                if text[end] == "\\":
                    end += 2
                    continue
                if text[end] == "_" and text[end + 1] == "_":
                    token = text[i + 2 : end]
                    choices = _read_wildcard_file(base_dir, token)
                    replacement = "{" + "|".join(choices) + "}"
                    out.append(replacement)
                    i = end + 2
                    break
                end += 1
            else:
                out.append(ch)
                i += 1
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def _unescape_text(text: str) -> str:
    escape = False
    out: List[str] = []
    for ch in text:
        if escape:
            out.append(ch)
            escape = False
            continue
        if ch == "\\":
            escape = True
            continue
        out.append(ch)
    return "".join(out)


def _expand_wildcards(text: str, rng: random.Random, base_dir: Path) -> str:
    if not text:
        return ""
    expanded = _replace_wildcard_files(text, base_dir)
    for _ in range(MAX_EXPANSION_PASSES):
        span = _find_next_brace(expanded)
        if span is None:
            return _unescape_text(expanded)
        start, end = span
        content = expanded[start + 1 : end]
        choices = _split_choices(content)
        choice = rng.choice(choices) if choices else ""
        replacement = _expand_wildcards(choice, rng, base_dir)
        expanded = expanded[:start] + replacement + expanded[end + 1 :]
    return _unescape_text(expanded)


class PromptWildcard:
    """
    Expand inline and file-backed wildcards into randomized text.
    """

    MODE_CHOICES = ("populate", "fixed", "reproduce")
    DESCRIPTION = (
        "Generate randomized text from inline or file-backed wildcards.\n\n"
        "- Inline wildcard: {one|two|three}\n"
        "- File wildcard: __path/to/file__ (uses config.ini wildcard_path)\n"
        "- Escape literal braces with \\{ and \\}\n"
        "- populate: overwrite output from wildcard_text\n"
        "- fixed: return populated_text as-is\n"
        "- reproduce: use populated_text once, then switch to populate"
    )

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "run"
    CATEGORY = "LFGG / Text"

    _WILDCARD_CHOICES: List[str] | None = None

    def __init__(self) -> None:
        self._reproduce_used = False

    @classmethod
    def _wildcard_choices(cls) -> List[str]:
        if cls._WILDCARD_CHOICES is None:
            cls._WILDCARD_CHOICES = _discover_wildcard_choices()
        return cls._WILDCARD_CHOICES

    @classmethod
    def INPUT_TYPES(cls):
        choices = cls._wildcard_choices()
        choice_tuple = tuple(choices)
        default_choice = choice_tuple[0] if choice_tuple else NO_SELECTION
        return {
            "required": {},
            "optional": {
                "wildcard_text": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "tooltip": "Template prompt supporting {one|two} and __file__ syntax.",
                    },
                ),
                "populated_text": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True,
                        "tooltip": "Manual prompt text used when mode is fixed or reproduce.",
                    },
                ),
                "mode": (
                    cls.MODE_CHOICES,
                    {
                        "default": "populate",
                        "tooltip": "populate=randomize wildcard_text, fixed=use populated_text, reproduce=fixed once then populate",
                    },
                ),
                "seed": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 0xFFFFFFFFFFFFFFFF,
                        "control_after_generate": True,
                        "tooltip": "Seed controlling wildcard selection.",
                    },
                ),
                "add_wildcard": (
                    choice_tuple,
                    {
                        "default": default_choice,
                        "tooltip": "Optional wildcard file to append as __path__ before expansion.",
                    },
                ),
            },
        }

    def run(
        self,
        wildcard_text: str = "",
        populated_text: str = "",
        mode: str = "populate",
        seed: int = 0,
        add_wildcard: str = NO_SELECTION,
    ):
        base_dir = _resolve_wildcard_dir()
        rng = random.Random(int(seed))

        if mode != "reproduce":
            self._reproduce_used = False

        template_text = wildcard_text
        if add_wildcard and add_wildcard != NO_SELECTION:
            token = f"__{add_wildcard}__"
            if template_text and not template_text.endswith(" "):
                template_text = f"{template_text} {token}"
            else:
                template_text = f"{template_text}{token}"

        if mode == "fixed":
            result_text = populated_text
        elif mode == "reproduce" and not self._reproduce_used:
            result_text = populated_text
            self._reproduce_used = True
        else:
            result_text = _expand_wildcards(template_text, rng, base_dir)

        return {
            "ui": {
                "text": (result_text,),
                "template": (template_text,),
            },
            "result": (result_text,),
        }


# ---- Registration ----
NODE_CLASS_MAPPINGS = {
    "LfggPromptWildcard": PromptWildcard,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LfggPromptWildcard": "LFGG Prompt Wildcard",
}

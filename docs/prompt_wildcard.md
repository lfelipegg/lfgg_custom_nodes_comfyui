# LFGG Prompt Wildcard

Generate randomized prompt text by expanding inline `{a|b}` choices and wildcard files referenced as `__path__`.

## Inputs
- **wildcard_text** (string, multiline): Template prompt that supports `{one|two}` and `__file__` syntax.
- **populated_text** (string, multiline): Manual text used when mode is `fixed` or the first run of `reproduce`.
- **mode** (choice): `populate`, `fixed`, `reproduce`.
- **seed** (int): Random seed used to pick wildcard options.
- **add_wildcard** (choice): Appends the selected wildcard as `__path__` to the template input.

## Outputs
- **text** (string): The expanded prompt text.

## Wildcard rules
- Inline wildcard: `{one|two|three}` selects one option.
- File wildcard: `__animals/cats__` loads a file under `config.ini` `wildcard_path`.
- `.txt` files can be referenced without the extension.
- Escape literal braces with `\{` and `\}`; escape `|` with `\|`.

## Modes
- **populate**: Expands `wildcard_text` and returns the randomized result.
- **fixed**: Ignores wildcards and returns `populated_text` as-is.
- **reproduce**: Returns `populated_text` once, then switches to `populate`.

## Example
Input `wildcard_text`:
```
portrait of a {knight|mage} in __backgrounds__
```

If `backgrounds.txt` contains:
```
forest
city at night
```

Then possible outputs include:
- `portrait of a knight in forest`
- `portrait of a mage in city at night`

## Constraints
- Missing wildcard files raise a `FileNotFoundError`.
- Wildcard entries are trimmed; empty lines and comment lines starting with `#` or `//` are ignored.

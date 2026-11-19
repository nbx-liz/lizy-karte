# lizy-karte

A zero-dependency Python package containing generic light and dark karte theme
tokens, extracted from a private viewer. It ships CSS custom properties, without
components or a command-line interface. Requires Python 3.12 or later.

Install from Git with a full commit pin. Replace `FULL_COMMIT_SHA` with the
40-character commit hash containing the kit version you want:

```sh
python -m pip install "lizy-karte @ git+https://github.com/nbx-liz/lizy-karte.git@FULL_COMMIT_SHA"
```

Inline the bundled CSS into an HTML document:

```python
from lizy_karte import THEME_CSS

html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <style>{THEME_CSS}</style>
</head>
<body style="background:var(--bg);color:var(--ink);font-family:var(--sans)">
  <p style="color:var(--accent)">Karte viewer</p>
</body>
</html>
"""
```

`THEME_CSS` contains the entire UTF-8 resource, read once at import.
`TOKEN_NAMES` is a `frozenset` of the 19 custom-property names, including their
leading `--`. The CSS also declares `color-scheme`, which is not a custom property.

The four contexts occur in this order:

| Selector and wrapper | Meaning |
| --- | --- |
| `:root` | Base light theme, including the shared radius and font stacks. |
| `@media (prefers-color-scheme:dark)` wrapping `:root:not([data-theme="light"])` | Follow the system dark preference unless light is explicitly selected. |
| `:root[data-theme="dark"]` | Force dark regardless of the system preference. |
| `:root[data-theme="light"]` | Force light regardless of the system preference. |

Set `data-theme="dark"` or `data-theme="light"` on the document's `<html>` element
to select a theme, or omit the attribute to follow the system preference.
Both dark contexts inherit `--radius`, `--mono`, and `--sans` from the base.
The explicit light context inherits the base `--shadow`.

The tokens are grouped as follows:

| Group | Tokens |
| --- | --- |
| Colour | `--accent`, `--accent-soft`, `--good`, `--good-soft`, `--warn`, `--warn-soft`, `--ko`, `--ko-soft` |
| Surface/ink | `--bg`, `--surface`, `--surface-2`, `--ink`, `--muted`, `--faint`, `--border`, `--shadow` |
| Shape/type | `--radius`, `--mono`, `--sans` |

Licensed under Apache-2.0. See [LICENSE](LICENSE).

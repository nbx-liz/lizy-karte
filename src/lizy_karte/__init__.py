"""Generic karte theme tokens for inlining into a viewer's style element."""

from __future__ import annotations

from importlib.resources import files as _files

__version__ = "0.1.0"
__all__ = ["THEME_CSS", "TOKEN_NAMES", "__version__"]

THEME_CSS: str = _files(__package__).joinpath("tokens.css").read_text(encoding="utf-8")
TOKEN_NAMES: frozenset[str] = frozenset(
    {
        "--accent",
        "--accent-soft",
        "--good",
        "--good-soft",
        "--warn",
        "--warn-soft",
        "--ko",
        "--ko-soft",
        "--bg",
        "--surface",
        "--surface-2",
        "--ink",
        "--muted",
        "--faint",
        "--border",
        "--shadow",
        "--radius",
        "--mono",
        "--sans",
    }
)

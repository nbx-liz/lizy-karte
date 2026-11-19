"""Pin each generic block to the definitions before extraction."""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path

import pytest

from css_blocks import parse_css_blocks
from lizy_karte import THEME_CSS, TOKEN_NAMES

# Source: the generic declarations of the private viewer's theme block at extraction time.
EXPECTED = {
    "root": (
        ("color-scheme", "light"),
        ("--accent", "#3a6ea5"),
        ("--accent-soft", "#3a6ea51f"),
        ("--good", "#2f8f5b"),
        ("--good-soft", "#2f8f5b1c"),
        ("--warn", "#b9791a"),
        ("--warn-soft", "#b9791a1f"),
        ("--ko", "#c0453b"),
        ("--ko-soft", "#c0453b1f"),
        ("--bg", "#f6f8fb"),
        ("--surface", "#ffffff"),
        ("--surface-2", "#eef2f7"),
        ("--ink", "#1a2331"),
        ("--muted", "#5b6676"),
        ("--faint", "#8a94a4"),
        ("--border", "#e1e6ee"),
        ("--shadow", "0 1px 2px rgba(20,30,50,.04),0 6px 20px rgba(20,30,50,.05)"),
        ("--radius", "12px"),
        ("--mono", 'ui-monospace,"SFMono-Regular",Menlo,Consolas,monospace'),
        (
            "--sans",
            'ui-sans-serif,system-ui,-apple-system,"Hiragino Kaku Gothic ProN",'
            '"Noto Sans JP","Meiryo",sans-serif',
        ),
    ),
    "media-dark": (
        ("color-scheme", "dark"),
        ("--bg", "#0f141b"),
        ("--surface", "#161d27"),
        ("--surface-2", "#1d2632"),
        ("--ink", "#e7ecf3"),
        ("--muted", "#98a5b6"),
        ("--faint", "#6f7c8e"),
        ("--border", "#26303d"),
        ("--accent", "#6ea3d6"),
        ("--accent-soft", "#6ea3d626"),
        ("--good", "#57b585"),
        ("--good-soft", "#57b58522"),
        ("--warn", "#d8a24a"),
        ("--warn-soft", "#d8a24a22"),
        ("--ko", "#e0655b"),
        ("--ko-soft", "#e0655b22"),
        ("--shadow", "0 1px 2px rgba(0,0,0,.3),0 8px 24px rgba(0,0,0,.35)"),
    ),
    "explicit-dark": (
        ("color-scheme", "dark"),
        ("--bg", "#0f141b"),
        ("--surface", "#161d27"),
        ("--surface-2", "#1d2632"),
        ("--ink", "#e7ecf3"),
        ("--muted", "#98a5b6"),
        ("--faint", "#6f7c8e"),
        ("--border", "#26303d"),
        ("--accent", "#6ea3d6"),
        ("--accent-soft", "#6ea3d626"),
        ("--good", "#57b585"),
        ("--good-soft", "#57b58522"),
        ("--warn", "#d8a24a"),
        ("--warn-soft", "#d8a24a22"),
        ("--ko", "#e0655b"),
        ("--ko-soft", "#e0655b22"),
        ("--shadow", "0 1px 2px rgba(0,0,0,.3),0 8px 24px rgba(0,0,0,.35)"),
    ),
    "explicit-light": (
        ("color-scheme", "light"),
        ("--bg", "#f6f8fb"),
        ("--surface", "#ffffff"),
        ("--surface-2", "#eef2f7"),
        ("--ink", "#1a2331"),
        ("--muted", "#5b6676"),
        ("--faint", "#8a94a4"),
        ("--border", "#e1e6ee"),
        ("--accent", "#3a6ea5"),
        ("--accent-soft", "#3a6ea51f"),
        ("--good", "#2f8f5b"),
        ("--good-soft", "#2f8f5b1c"),
        ("--warn", "#b9791a"),
        ("--warn-soft", "#b9791a1f"),
        ("--ko", "#c0453b"),
        ("--ko-soft", "#c0453b1f"),
    ),
}

# The whole file, byte for byte. Generated from the source block (domain-specific lines
# dropped, two-space dedent, blank lines dropped), not copied from tokens.css. This pin
# bounds the input: the structural reader below only ever has to read this one text.
EXPECTED_TEXT = (
    ":root {\n"
    "  color-scheme:light;\n"
    "  --accent:#3a6ea5; --accent-soft:#3a6ea51f;\n"
    "  --good:#2f8f5b; --good-soft:#2f8f5b1c;\n"
    "  --warn:#b9791a; --warn-soft:#b9791a1f;\n"
    "  --ko:#c0453b;   --ko-soft:#c0453b1f;\n"
    "  --bg:#f6f8fb; --surface:#ffffff; --surface-2:#eef2f7;\n"
    "  --ink:#1a2331; --muted:#5b6676; --faint:#8a94a4; --border:#e1e6ee;\n"
    "  --shadow:0 1px 2px rgba(20,30,50,.04),0 6px 20px rgba(20,30,50,.05);\n"
    "  --radius:12px;\n"
    '  --mono:ui-monospace,"SFMono-Regular",Menlo,Consolas,monospace;\n'
    '  --sans:ui-sans-serif,system-ui,-apple-system,"Hiragino Kaku Gothic ProN",'
    '"Noto Sans JP","Meiryo",sans-serif;\n'
    "}\n"
    "@media (prefers-color-scheme:dark){\n"
    '  :root:not([data-theme="light"]){\n'
    "    color-scheme:dark;\n"
    "    --bg:#0f141b; --surface:#161d27; --surface-2:#1d2632;\n"
    "    --ink:#e7ecf3; --muted:#98a5b6; --faint:#6f7c8e; --border:#26303d;\n"
    "    --accent:#6ea3d6; --accent-soft:#6ea3d626;\n"
    "    --good:#57b585; --good-soft:#57b58522;\n"
    "    --warn:#d8a24a; --warn-soft:#d8a24a22;\n"
    "    --ko:#e0655b; --ko-soft:#e0655b22;\n"
    "    --shadow:0 1px 2px rgba(0,0,0,.3),0 8px 24px rgba(0,0,0,.35);\n"
    "  }\n"
    "}\n"
    ':root[data-theme="dark"]{\n'
    "  color-scheme:dark;\n"
    "  --bg:#0f141b; --surface:#161d27; --surface-2:#1d2632;\n"
    "  --ink:#e7ecf3; --muted:#98a5b6; --faint:#6f7c8e; --border:#26303d;\n"
    "  --accent:#6ea3d6; --accent-soft:#6ea3d626;\n"
    "  --good:#57b585; --good-soft:#57b58522;\n"
    "  --warn:#d8a24a; --warn-soft:#d8a24a22;\n"
    "  --ko:#e0655b; --ko-soft:#e0655b22;\n"
    "  --shadow:0 1px 2px rgba(0,0,0,.3),0 8px 24px rgba(0,0,0,.35);\n"
    "}\n"
    ':root[data-theme="light"]{\n'
    "  color-scheme:light;\n"
    "  --bg:#f6f8fb; --surface:#ffffff; --surface-2:#eef2f7;\n"
    "  --ink:#1a2331; --muted:#5b6676; --faint:#8a94a4; --border:#e1e6ee;\n"
    "  --accent:#3a6ea5; --accent-soft:#3a6ea51f;\n"
    "  --good:#2f8f5b; --good-soft:#2f8f5b1c;\n"
    "  --warn:#b9791a; --warn-soft:#b9791a1f;\n"
    "  --ko:#c0453b; --ko-soft:#c0453b1f;\n"
    "}\n"
)


def token_file_bytes() -> bytes:
    return files("lizy_karte").joinpath("tokens.css").read_bytes()


def token_file_text() -> str:
    return files("lizy_karte").joinpath("tokens.css").read_text(encoding="utf-8")


def test_token_file_is_byte_pinned() -> None:
    """The authoritative pin: any change to tokens.css, of any kind, fails here.

    It compares raw bytes, because text-mode reading translates line endings and
    would let a CRLF or CR variant of the file pass.
    """
    assert token_file_bytes() == EXPECTED_TEXT.encode("utf-8")


@pytest.mark.parametrize("newline", ["\r\n", "\r"], ids=["crlf", "cr"])
def test_byte_pin_rejects_line_ending_variants(tmp_path: Path, newline: str) -> None:
    variant = tmp_path / "tokens.css"
    variant.write_bytes(EXPECTED_TEXT.replace("\n", newline).encode("utf-8"))
    # Text mode hides the variant; the byte comparison the pin uses does not.
    assert variant.read_text(encoding="utf-8") == EXPECTED_TEXT
    assert variant.read_bytes() != EXPECTED_TEXT.encode("utf-8")


def test_blocks_match_literal_source_table() -> None:
    """Structural view of the byte-pinned text: contexts, order and values."""
    assert token_file_text() == EXPECTED_TEXT
    assert parse_css_blocks(EXPECTED_TEXT) == EXPECTED


@pytest.mark.parametrize(
    "replacements",
    [
        pytest.param(((":root {", ":root\u00a0{"),), id="nbsp-after-root"),
        pytest.param((("--bg:#f6f8fb;", "--bg:\u00a0#f6f8fb;"),), id="nbsp-after-bg"),
        pytest.param((("--bg:#f6f8fb;", "--bg:#000000;"),), id="changed-value"),
        pytest.param(
            (
                (
                    "--accent:#3a6ea5; --accent-soft:#3a6ea51f;",
                    "--accent-soft:#3a6ea51f; --accent:#3a6ea5;",
                ),
            ),
            id="swapped-adjacent-declarations",
        ),
        pytest.param(
            (
                ("--radius:12px;", ""),
                (':root[data-theme="light"]{', ':root[data-theme="light"]{--radius:12px;'),
            ),
            id="declaration-moved-to-another-block",
        ),
    ],
)
def test_source_pin_detects_mutations(replacements: tuple[tuple[str, str], ...]) -> None:
    source = token_file_text()
    mutated = source
    for original, replacement in replacements:
        assert original in mutated
        mutated = mutated.replace(original, replacement, 1)
    assert mutated != source
    try:
        blocks = parse_css_blocks(mutated)
    except ValueError:
        return
    assert blocks != EXPECTED


def test_token_names_match_file_union() -> None:
    blocks = parse_css_blocks(token_file_text())
    names = frozenset(
        name for pairs in blocks.values() for name, _ in pairs if name.startswith("--")
    )
    assert TOKEN_NAMES == names
    assert len(TOKEN_NAMES) == 19


def test_export_is_exact_file_text() -> None:
    assert THEME_CSS
    assert THEME_CSS == token_file_text()


def test_context_counts_and_color_schemes() -> None:
    blocks = parse_css_blocks(token_file_text())
    assert tuple(blocks) == ("root", "media-dark", "explicit-dark", "explicit-light")
    assert tuple(sum(name.startswith("--") for name, _ in pairs) for pairs in blocks.values()) == (
        19,
        16,
        16,
        15,
    )
    schemes = tuple(
        tuple(value for name, value in pairs if name == "color-scheme") for pairs in blocks.values()
    )
    assert schemes == (("light",), ("dark",), ("dark",), ("light",))

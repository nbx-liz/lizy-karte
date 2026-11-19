"""Exercise the closed grammar, including every required refusal."""

from __future__ import annotations

import pytest

from css_blocks import parse_css_blocks

ROOT = ":root {color-scheme:light;}"
MEDIA = '@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){color-scheme:dark;}}'
DARK = ':root[data-theme="dark"]{color-scheme:dark;}'
LIGHT = ':root[data-theme="light"]{color-scheme:light;}'
VALID = ROOT + MEDIA + DARK + LIGHT


def test_valid_minimal_four_blocks() -> None:
    assert parse_css_blocks(VALID) == {
        "root": (("color-scheme", "light"),),
        "media-dark": (("color-scheme", "dark"),),
        "explicit-dark": (("color-scheme", "dark"),),
        "explicit-light": (("color-scheme", "light"),),
    }


def test_declaration_order_and_surrounding_whitespace() -> None:
    css = VALID.replace("color-scheme:light;", " color-scheme : light ; --x-1 :  a  b ;", 1)
    assert parse_css_blocks(css)["root"] == (("color-scheme", "light"), ("--x-1", "a  b"))


@pytest.mark.parametrize(
    "css",
    [
        pytest.param(VALID.replace(":root {", "body {", 1), id="unknown-selector"),
        pytest.param(ROOT + ROOT + MEDIA + DARK + LIGHT, id="extra-selector"),
        pytest.param(ROOT + MEDIA + DARK, id="missing-block"),
        pytest.param(
            ROOT + ':root:not([data-theme="light"]){color-scheme:dark;}' + DARK + LIGHT,
            id="block-outside-media",
        ),
        pytest.param(
            ROOT + "@media (prefers-color-scheme:dark){" + DARK + "}" + DARK + LIGHT,
            id="wrong-block-inside-media",
        ),
        pytest.param(
            ROOT + "@media (prefers-color-scheme:light){" + DARK + "}" + LIGHT, id="wrong-media"
        ),
        pytest.param(VALID.replace("@media", "@supports", 1), id="other-at-rule"),
        pytest.param('@import "other.css";' + VALID, id="extra-at-rule"),
        pytest.param(VALID.replace("light;", "light; @import url(x);", 1), id="at-rule-in-block"),
        pytest.param("/* comment */" + VALID, id="comment"),
        pytest.param(VALID.replace("light;", "li/* comment */ght;", 1), id="comment-in-value"),
        pytest.param(VALID[:-1], id="unclosed-brace"),
        pytest.param(ROOT + "}" + MEDIA + DARK + LIGHT, id="extra-closing-brace"),
        pytest.param(VALID.replace("light;", "light; {--x:1;}", 1), id="nested-brace"),
        pytest.param(
            VALID.replace("color-scheme:light;", "color-scheme light;", 1), id="missing-colon"
        ),
        pytest.param(VALID.replace("color-scheme:light;", "color-scheme: ;", 1), id="empty-value"),
        pytest.param(
            VALID.replace("color-scheme:light;", "background:white;", 1), id="ordinary-property"
        ),
        pytest.param(VALID.replace("color-scheme:light;", "--Bad:1;", 1), id="uppercase-property"),
        pytest.param(VALID.replace("color-scheme:light;", "--:1;", 1), id="empty-custom-name"),
        pytest.param(
            VALID.replace("color-scheme:light;", "--bad_name:1;", 1), id="invalid-custom-name"
        ),
        pytest.param(
            VALID.replace("color-scheme:light;", "color-scheme-extra:light;", 1),
            id="property-superstring",
        ),
        pytest.param(
            VALID.replace("color-scheme:light;", "color-scheme:light;color-scheme:dark;", 1),
            id="duplicate-property",
        ),
        pytest.param(
            VALID.replace("color-scheme:light;", "--x:1;--x:2;", 1), id="duplicate-custom-property"
        ),
        pytest.param(VALID + "trailing text", id="trailing-text"),
        pytest.param(VALID + ROOT, id="trailing-block"),
        pytest.param(VALID.replace("light;", "light", 1), id="missing-semicolon"),
        pytest.param(VALID.replace("light;", "light;;", 1), id="empty-declaration"),
    ],
)
def test_refuses_malformed_css(css: str) -> None:
    with pytest.raises(ValueError, match=r"\S"):
        parse_css_blocks(css)


@pytest.mark.parametrize(
    "css",
    [
        pytest.param(VALID.replace(":root {", ":root\u00a0{", 1), id="nbsp-in-selector"),
        pytest.param(VALID.replace("color-scheme:light;", "--x:\u00a0a;", 1), id="nbsp-in-value"),
        pytest.param(
            VALID.replace("color-scheme:light;", "--x:\u00e9;", 1), id="non-ascii-in-value"
        ),
        pytest.param(
            VALID.replace("color-scheme:light;", '--x:"a;--y:b";', 1), id="quoted-semicolon"
        ),
        pytest.param(
            VALID.replace("color-scheme:light;", '--x:"a}";', 1), id="quoted-closing-brace"
        ),
        pytest.param(
            VALID.replace("color-scheme:light;", 'color-scheme:"light;', 1).replace(
                "color-scheme:dark;", 'color-scheme:dark";', 1
            ),
            id="quote-spanning-blocks",
        ),
        pytest.param(
            VALID.replace("color-scheme:light;", "--x:'a';", 1), id="single-quote-in-value"
        ),
        pytest.param(VALID.replace("color-scheme:light;", r"--x:a\b;", 1), id="backslash-in-value"),
    ],
)
def test_refuses_unsupported_characters_and_quotes(css: str) -> None:
    with pytest.raises(ValueError, match=r"\S"):
        parse_css_blocks(css)


@pytest.mark.parametrize(
    "css",
    [
        pytest.param(
            VALID.replace("color-scheme:light;", "--x:func(a;--y:b);", 1), id="paren-spanning-semi"
        ),
        pytest.param(VALID.replace("color-scheme:light;", "--x:func(a;", 1), id="unclosed-paren"),
        pytest.param(VALID.replace("color-scheme:light;", "--x:a);", 1), id="unmatched-close"),
        pytest.param(
            VALID.replace("color-scheme:light;", '--x:"a;b";--y:"c";', 1),
            id="balanced-quote-spanning-semi",
        ),
        pytest.param(
            VALID.replace("color-scheme:light;", '--x:func("a)";', 1), id="paren-in-string"
        ),
        pytest.param(VALID.replace("color-scheme:light;", "--x:func(a}", 1), id="brace-in-paren"),
    ],
)
def test_refuses_delimiters_spanning_declarations(css: str) -> None:
    with pytest.raises(ValueError, match=r"\S"):
        parse_css_blocks(css)


def test_parenthesised_comma_value_is_one_declaration() -> None:
    value = "rgba(0,0,0,.3),0 8px 24px rgba(0,0,0,.35)"
    css = VALID.replace("color-scheme:light;", f"--x:{value};", 1)
    assert parse_css_blocks(css)["root"] == (("--x", value),)

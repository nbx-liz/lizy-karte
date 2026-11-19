"""Structural reader for the byte-pinned token file.

tests/test_tokens.py pins tokens.css byte for byte (EXPECTED_TEXT), so this reader only ever
reads that one text in the suite. It is not a general CSS parser: it reads the four ordered
blocks of that file and refuses, without recovery, anything outside its small grammar.
"""

from __future__ import annotations

import re

type Declarations = tuple[tuple[str, str], ...]

_PROPERTY = re.compile(r"(?:color-scheme|--[a-z0-9-]+)")
_VALUE = re.compile(r'[A-Za-z0-9#.,() "-]+')
_CSS_WHITESPACE = " \t\n\r\f"


def _consume(text: str, expected: str) -> str:
    remaining = text.lstrip(_CSS_WHITESPACE)
    if not remaining.startswith(expected):
        raise ValueError(f"Expected {expected!r}, found {remaining[:60]!r}")
    return remaining[len(expected) :]


def _declaration(text: str) -> tuple[str, str]:
    name, separator, value = text.partition(":")
    name, value = name.strip(_CSS_WHITESPACE), value.strip(_CSS_WHITESPACE)
    if not separator:
        raise ValueError(f"Declaration has no colon: {text!r}")
    if _PROPERTY.fullmatch(name) is None:
        raise ValueError(f"Invalid property name: {name!r}")
    if not value:
        raise ValueError(f"Empty value for {name!r}")
    if _VALUE.fullmatch(value) is None or value.count('"') % 2:
        raise ValueError(f"Invalid value for {name!r}: {value!r}")
    return name, value


def _scan_body(text: str, selector: str) -> tuple[list[str], str]:
    """Split one block body on top-level semicolons and return it with the tail.

    One left-to-right pass tracks the string state and the parenthesis depth, so a
    delimiter inside a string or parentheses never splits or ends anything.
    """
    parts: list[str] = []
    start = 0
    depth = 0
    in_string = False
    for index, char in enumerate(text):
        if char == "{":
            raise ValueError(f"Unexpected nested block inside {selector!r}")
        if char == '"':
            in_string = not in_string
        elif in_string:
            if char == "}":
                raise ValueError(f"Closing brace inside a string in {selector!r}")
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth < 0:
                raise ValueError(f"Unmatched closing parenthesis in {selector!r}")
        elif char == ";" and depth == 0:
            parts.append(text[start:index])
            start = index + 1
        elif char == "}":
            if depth:
                raise ValueError(f"Unclosed parenthesis in {selector!r}")
            parts.append(text[start:index])
            return parts, text[index + 1 :]
    if in_string:
        raise ValueError(f"Unclosed string in {selector!r}")
    raise ValueError(f"Unbalanced braces: missing closing brace for {selector!r}")


def _read_block(text: str, selector: str) -> tuple[Declarations, str]:
    parts, tail = _scan_body(_consume(_consume(text, selector), "{"), selector)
    if parts[-1].strip(_CSS_WHITESPACE):
        raise ValueError(f"Missing final declaration semicolon in {selector!r}")
    if not parts[:-1] or any(not part.strip(_CSS_WHITESPACE) for part in parts[:-1]):
        raise ValueError(f"Empty declaration in {selector!r}")
    pairs = tuple(_declaration(part) for part in parts[:-1])
    names = tuple(name for name, _ in pairs)
    if len(names) != len(frozenset(names)):
        raise ValueError(f"Duplicate property inside {selector!r}")
    return pairs, tail


def parse_css_blocks(text: str) -> dict[str, Declarations]:
    """Return ordered declarations by context; reject every unread fragment."""
    if any(not (" " <= char <= "~" or char in _CSS_WHITESPACE) for char in text):
        raise ValueError("Only printable ASCII and CSS whitespace are allowed")
    if "/*" in text or "*/" in text:
        raise ValueError("Comments are not allowed")
    root, remaining = _read_block(text, ":root")
    remaining = _consume(remaining, "@media (prefers-color-scheme:dark){")
    media_dark, remaining = _read_block(remaining, ':root:not([data-theme="light"])')
    remaining = _consume(remaining, "}")
    explicit_dark, remaining = _read_block(remaining, ':root[data-theme="dark"]')
    explicit_light, remaining = _read_block(remaining, ':root[data-theme="light"]')
    if remaining.strip(_CSS_WHITESPACE):
        raise ValueError(f"Trailing text after the last block: {remaining[:60]!r}")
    return {
        "root": root,
        "media-dark": media_dark,
        "explicit-dark": explicit_dark,
        "explicit-light": explicit_light,
    }

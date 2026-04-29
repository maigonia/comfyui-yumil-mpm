"""
Yumil Parser Block Parser

Parses ###_Path(...).Value(...).Text(...)_### blocks from prompt text.
Uses the same bracket-depth positional parsing approach as MPM's
Category Identifier (CI) parser.
"""

import json
import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


START_MARKER = "###_"
END_MARKER = "_###"

# Chain methods to search for (with leading dot)
CHAIN_METHODS = [".Path(", ".Value(", ".Text("]


@dataclass
class ParsedBlock:
    """A single parsed ###_..._### block."""
    path: str = ""
    value: Optional[str] = None
    text: Optional[str] = None
    full_match: str = ""
    start_index: int = 0
    length: int = 0


@dataclass
class ParseResult:
    """Result of parsing a prompt string."""
    clean_text: str
    blocks: List[ParsedBlock] = field(default_factory=list)


def find_parameter_end(input_str: str, param_start: int) -> int:
    """
    Find the closing parenthesis position using bracket-depth tracking.

    Ported from CategoryIdentifierParser.ts findParameterEnd().
    No quote-awareness needed: Path() and Text() values are raw content.
    """
    depth = 1
    i = param_start

    while i < len(input_str) and depth > 0:
        char = input_str[i]

        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return i

        i += 1

    return len(input_str)


def find_next_chain_method(
    input_str: str, start_pos: int
) -> Optional[Tuple[str, int]]:
    """
    Find the nearest chain method (.Path(, .Value(, or .Text() from start_pos.
    Returns (method_pattern, position) or None.
    """
    nearest_method = None
    nearest_pos = len(input_str)

    for pattern in CHAIN_METHODS:
        pos = input_str.find(pattern, start_pos)
        if pos != -1 and pos < nearest_pos:
            nearest_pos = pos
            nearest_method = pattern

    if nearest_method is None:
        return None

    return (nearest_method, nearest_pos)


def parse_single_block(block_content: str) -> ParsedBlock:
    """
    Parse the content between ###_ and _### into a ParsedBlock.

    block_content example: "Path(C:/img/girl.png).Value(strength=0.8).Text(a beautiful girl)"

    Prepends '.' to normalize since block content starts with 'Path('
    but chain methods search for '.Path('.
    """
    block = ParsedBlock()

    # Normalize: prepend '.' so "Path(...)" becomes ".Path(...)"
    normalized = "." + block_content
    current_pos = 0

    while current_pos < len(normalized):
        result = find_next_chain_method(normalized, current_pos)
        if result is None:
            break

        method_pattern, method_pos = result
        # ".Path(" -> "Path", ".Value(" -> "Value", ".Text(" -> "Text"
        method_name = method_pattern[1:-1]

        param_start = method_pos + len(method_pattern)
        param_end = find_parameter_end(normalized, param_start)

        param_value = normalized[param_start:param_end]

        if method_name == "Path":
            block.path = param_value.strip().strip('"')
        elif method_name == "Value":
            block.value = param_value.strip()
        elif method_name == "Text":
            block.text = param_value.strip()

        current_pos = param_end + 1

    return block


def find_all_blocks(prompt: str) -> List[ParsedBlock]:
    """
    Find all ###_..._### blocks in the prompt string.
    """
    blocks: List[ParsedBlock] = []
    search_start = 0

    while search_start < len(prompt):
        start_idx = prompt.find(START_MARKER, search_start)
        if start_idx == -1:
            break

        end_idx = prompt.find(END_MARKER, start_idx + len(START_MARKER))
        if end_idx == -1:
            break

        full_match = prompt[start_idx : end_idx + len(END_MARKER)]
        inner = prompt[start_idx + len(START_MARKER) : end_idx]

        block = parse_single_block(inner)
        block.full_match = full_match
        block.start_index = start_idx
        block.length = len(full_match)

        if block.path or block.value is not None or block.text is not None:
            blocks.append(block)

        search_start = end_idx + len(END_MARKER)

    return blocks


def parse_prompt(prompt: str) -> ParseResult:
    """
    Parse a full prompt string: extract blocks and produce clean text.

    Blocks with Text() are replaced by their text value.
    Blocks without Text() are removed entirely.
    Cleans up leftover comma/whitespace artifacts.
    """
    blocks = find_all_blocks(prompt)

    if not blocks:
        return ParseResult(clean_text=prompt, blocks=[])

    # Replace blocks from right to left to preserve indices
    clean = prompt
    for block in reversed(blocks):
        replacement = block.text if block.text else ""
        clean = clean[: block.start_index] + replacement + clean[block.start_index + block.length :]

    # Clean up artifacts
    clean = re.sub(r",\s*,", ",", clean)
    clean = re.sub(r"^\s*,\s*", "", clean)
    clean = re.sub(r"\s*,\s*$", "", clean)
    clean = re.sub(r"\s{2,}", " ", clean)
    clean = clean.strip()

    return ParseResult(clean_text=clean, blocks=blocks)


def serialize_parsed_data(blocks: List[ParsedBlock]) -> str:
    """Serialize blocks to JSON for inter-node communication."""
    data = [{"path": block.path, "value": block.value, "text": block.text} for block in blocks]
    return json.dumps(data, ensure_ascii=False)


def deserialize_parsed_data(parsed_data: str) -> List[ParsedBlock]:
    """Deserialize JSON back into ParsedBlock objects."""
    if not parsed_data.strip():
        return []

    data = json.loads(parsed_data)
    return [
        ParsedBlock(
            path=item.get("path", ""),
            value=item.get("value"),
            text=item.get("text"),
        )
        for item in data
    ]

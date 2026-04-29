"""
Tests for the Yumil parser block parser.

Run: python -m pytest tests/ -v
"""

import json

from parser import (
    ParsedBlock,
    deserialize_parsed_data,
    find_all_blocks,
    find_parameter_end,
    parse_prompt,
    parse_single_block,
    serialize_parsed_data,
)


# --- find_parameter_end ---


class TestFindParameterEnd:
    def test_simple(self):
        # "hello)" - depth starts at 1, ')' brings to 0
        assert find_parameter_end("hello)", 0) == 5

    def test_nested_parentheses(self):
        # "a (b) c)" - inner () increments/decrements, last ')' closes
        assert find_parameter_end("a (b) c)", 0) == 7

    def test_deeply_nested(self):
        # "a(b(c)d)e)" - depth goes 1->2->3->2->1->0
        assert find_parameter_end("a(b(c)d)e)", 0) == 9

    def test_no_closing_paren(self):
        assert find_parameter_end("hello", 0) == 5


# --- parse_single_block ---


class TestParseSingleBlock:
    def test_path_and_text(self):
        block = parse_single_block("Path(C:/img/girl.png).Text(a beautiful girl)")
        assert block.path == "C:/img/girl.png"
        assert block.text == "a beautiful girl"

    def test_path_only(self):
        block = parse_single_block("Path(C:/img/ref.png)")
        assert block.path == "C:/img/ref.png"
        assert block.text is None

    def test_nested_parens_in_path(self):
        block = parse_single_block("Path(C:/dir (copy)/img.png).Text(test)")
        assert block.path == "C:/dir (copy)/img.png"
        assert block.text == "test"

    def test_nested_parens_in_text(self):
        block = parse_single_block("Path(img.png).Text(girl (smiling) happily)")
        assert block.path == "img.png"
        assert block.text == "girl (smiling) happily"

    def test_deeply_nested_parens_in_path(self):
        block = parse_single_block("Path(C:/a(b(c)d)e/img.png)")
        assert block.path == "C:/a(b(c)d)e/img.png"

    def test_windows_backslash_path(self):
        block = parse_single_block(r"Path(C:\Users\img\girl.png).Text(test)")
        assert block.path == r"C:\Users\img\girl.png"
        assert block.text == "test"

    def test_text_with_commas(self):
        block = parse_single_block("Path(img.png).Text(a beautiful, young girl)")
        assert block.text == "a beautiful, young girl"

    def test_text_with_sd_weight_syntax(self):
        block = parse_single_block("Path(img.png).Text(a (beautiful:1.5) girl)")
        assert block.text == "a (beautiful:1.5) girl"

    def test_text_with_newlines(self):
        block = parse_single_block("Path(img.png).Text(line one\nline two)")
        assert block.text == "line one\nline two"

    def test_path_with_apostrophe(self):
        block = parse_single_block("Path(C:/John's Files/img.png).Text(hello)")
        assert block.path == "C:/John's Files/img.png"

    def test_path_with_spaces(self):
        block = parse_single_block("Path(C:/My Images/photo 01.png).Text(a girl)")
        assert block.path == "C:/My Images/photo 01.png"

    # --- Value tests ---

    def test_path_value_text(self):
        block = parse_single_block("Path(img.png).Value(strength=0.8,mode=ipadapter).Text(a girl)")
        assert block.path == "img.png"
        assert block.value == "strength=0.8,mode=ipadapter"
        assert block.text == "a girl"

    def test_path_and_value_no_text(self):
        block = parse_single_block("Path(img.png).Value(strength=0.5)")
        assert block.path == "img.png"
        assert block.value == "strength=0.5"
        assert block.text is None

    def test_value_only(self):
        block = parse_single_block("Value(key=val)")
        assert block.path == ""
        assert block.value == "key=val"
        assert block.text is None

    def test_value_with_equals_in_value(self):
        block = parse_single_block("Value(expr=a=b)")
        assert block.value == "expr=a=b"

    def test_value_and_text_no_path(self):
        block = parse_single_block("Value(mode=test).Text(hello)")
        assert block.path == ""
        assert block.value == "mode=test"
        assert block.text == "hello"

    def test_multiple_paths_comma_separated(self):
        block = parse_single_block("Path(a.png,b.png,c.png).Text(hello)")
        assert block.path == "a.png,b.png,c.png"
        assert block.text == "hello"


# --- find_all_blocks ---


class TestFindAllBlocks:
    def test_single_block(self):
        blocks = find_all_blocks("###_Path(a.png).Text(hello)_###")
        assert len(blocks) == 1
        assert blocks[0].path == "a.png"
        assert blocks[0].text == "hello"

    def test_multiple_blocks(self):
        prompt = "###_Path(a.png).Text(A)_###, ###_Path(b.png).Text(B)_###"
        blocks = find_all_blocks(prompt)
        assert len(blocks) == 2
        assert blocks[0].path == "a.png"
        assert blocks[1].path == "b.png"

    def test_no_blocks(self):
        blocks = find_all_blocks("masterpiece, best quality")
        assert len(blocks) == 0

    def test_block_positions(self):
        prompt = "start ###_Path(a.png)_### end"
        blocks = find_all_blocks(prompt)
        assert blocks[0].start_index == 6
        assert blocks[0].full_match == "###_Path(a.png)_###"
        assert blocks[0].length == 19

    def test_adjacent_blocks(self):
        prompt = "###_Path(a.png).Text(A)_######_Path(b.png).Text(B)_###"
        blocks = find_all_blocks(prompt)
        assert len(blocks) == 2

    def test_block_with_value(self):
        blocks = find_all_blocks("###_Path(a.png).Value(k=v).Text(hello)_###")
        assert len(blocks) == 1
        assert blocks[0].path == "a.png"
        assert blocks[0].value == "k=v"
        assert blocks[0].text == "hello"

    def test_value_only_block(self):
        blocks = find_all_blocks("###_Value(k=v).Text(hello)_###")
        assert len(blocks) == 1
        assert blocks[0].path == ""
        assert blocks[0].value == "k=v"
        assert blocks[0].text == "hello"

    def test_text_only_block(self):
        blocks = find_all_blocks("###_Text(hello)_###")
        assert len(blocks) == 1
        assert blocks[0].text == "hello"

    def test_empty_block_filtered(self):
        # A block with no methods at all should be filtered out
        blocks = find_all_blocks("###__###")
        assert len(blocks) == 0


# --- parse_prompt (full pipeline) ---


class TestParsePrompt:
    def test_single_block_with_text(self):
        result = parse_prompt(
            "masterpiece, ###_Path(C:/img/girl.png).Text(a beautiful girl)_###, best quality"
        )
        assert result.clean_text == "masterpiece, a beautiful girl, best quality"
        assert len(result.blocks) == 1
        assert result.blocks[0].path == "C:/img/girl.png"
        assert result.blocks[0].text == "a beautiful girl"

    def test_block_without_text(self):
        result = parse_prompt(
            "masterpiece, ###_Path(C:/img/ref.png)_###, best quality"
        )
        assert result.clean_text == "masterpiece, best quality"
        assert len(result.blocks) == 1
        assert result.blocks[0].text is None

    def test_multiple_blocks(self):
        result = parse_prompt(
            "###_Path(a.png).Text(hello)_###, ###_Path(b.png).Text(world)_###"
        )
        assert result.clean_text == "hello, world"
        assert len(result.blocks) == 2

    def test_no_blocks_passthrough(self):
        result = parse_prompt("masterpiece, best quality")
        assert result.clean_text == "masterpiece, best quality"
        assert len(result.blocks) == 0

    def test_block_at_start(self):
        result = parse_prompt("###_Path(a.png).Text(hello)_###, rest")
        assert result.clean_text == "hello, rest"

    def test_block_at_end(self):
        result = parse_prompt("start, ###_Path(a.png).Text(end)_###")
        assert result.clean_text == "start, end"

    def test_path_only_removes_double_commas(self):
        result = parse_prompt("a, ###_Path(ref.png)_###, b")
        assert result.clean_text == "a, b"

    def test_path_only_at_start(self):
        result = parse_prompt("###_Path(ref.png)_###, a, b")
        assert result.clean_text == "a, b"

    def test_path_only_at_end(self):
        result = parse_prompt("a, b, ###_Path(ref.png)_###")
        assert result.clean_text == "a, b"

    def test_mixed_with_and_without_text(self):
        result = parse_prompt(
            "###_Path(ref.png)_###, ###_Path(girl.png).Text(a girl)_###, best quality"
        )
        assert result.clean_text == "a girl, best quality"
        assert len(result.blocks) == 2

    def test_complex_prompt(self):
        result = parse_prompt(
            "masterpiece, ###_Path(C:/img/girl.png).Text(a beautiful girl with red hair)_###, "
            "###_Path(C:/img/bg.png).Text(in a flower garden)_###, "
            "###_Path(C:/img/style_ref.png)_###, best quality"
        )
        assert result.clean_text == "masterpiece, a beautiful girl with red hair, in a flower garden, best quality"
        assert len(result.blocks) == 3

    def test_block_with_value_preserves_text(self):
        result = parse_prompt(
            "start, ###_Path(img.png).Value(strength=0.8).Text(a girl)_###, end"
        )
        assert result.clean_text == "start, a girl, end"
        assert result.blocks[0].value == "strength=0.8"

    def test_value_only_block_removed_from_text(self):
        result = parse_prompt(
            "a, ###_Value(mode=test)_###, b"
        )
        assert result.clean_text == "a, b"


# --- serialization ---


class TestSerialization:
    def test_round_trip(self):
        blocks = [
            ParsedBlock(path="C:/img/a.png", text="hello"),
            ParsedBlock(path="C:/img/b.png", text=None),
        ]
        data = serialize_parsed_data(blocks)
        restored = deserialize_parsed_data(data)

        assert len(restored) == 2
        assert restored[0].path == "C:/img/a.png"
        assert restored[0].text == "hello"
        assert restored[1].path == "C:/img/b.png"
        assert restored[1].text is None

    def test_empty(self):
        assert deserialize_parsed_data("") == []
        assert deserialize_parsed_data("  ") == []

    def test_json_handles_backslashes(self):
        blocks = [ParsedBlock(path=r"C:\Users\img\girl.png", text="test")]
        data = serialize_parsed_data(blocks)
        restored = deserialize_parsed_data(data)
        assert restored[0].path == r"C:\Users\img\girl.png"

    def test_json_handles_newlines_in_text(self):
        blocks = [ParsedBlock(path="img.png", text="line one\nline two")]
        data = serialize_parsed_data(blocks)
        restored = deserialize_parsed_data(data)
        assert restored[0].text == "line one\nline two"

    def test_round_trip_with_value(self):
        blocks = [
            ParsedBlock(path="img.png", value="strength=0.8", text="hello"),
            ParsedBlock(path="", value="mode=test", text=None),
        ]
        data = serialize_parsed_data(blocks)
        restored = deserialize_parsed_data(data)

        assert len(restored) == 2
        assert restored[0].value == "strength=0.8"
        assert restored[0].text == "hello"
        assert restored[1].path == ""
        assert restored[1].value == "mode=test"
        assert restored[1].text is None

    def test_value_none_preserved(self):
        blocks = [ParsedBlock(path="img.png", text="hello")]
        data = serialize_parsed_data(blocks)
        restored = deserialize_parsed_data(data)
        assert restored[0].value is None


# --- calc_size_by_total ---

# Import from nodes is not possible without torch/PIL,
# so we copy the pure math function here for testing.
def calc_size_by_total(width: int, height: int, target_total: int) -> tuple:
    aspect = width / height
    new_h = target_total / (1 + aspect)
    new_w = target_total - new_h
    new_w = max(8, round(new_w / 8) * 8)
    new_h = max(8, round(new_h / 8) * 8)
    return (new_w, new_h)


class TestCalcSizeByTotal:
    def test_square_sdxl(self):
        # 1:1 -> 1024x1024
        w, h = calc_size_by_total(512, 512, 2048)
        assert w == 1024
        assert h == 1024
        assert w + h == 2048

    def test_landscape_3_2(self):
        # 3:2 -> ~1224x824
        w, h = calc_size_by_total(1500, 1000, 2048)
        assert w + h <= 2048 + 8  # rounding tolerance
        assert w > h

    def test_portrait_2_3(self):
        # 2:3 -> ~824x1224
        w, h = calc_size_by_total(1000, 1500, 2048)
        assert w + h <= 2048 + 8
        assert h > w

    def test_landscape_16_9(self):
        # 16:9
        w, h = calc_size_by_total(1920, 1080, 2048)
        assert w > h
        assert w % 8 == 0
        assert h % 8 == 0

    def test_portrait_9_16(self):
        # 9:16
        w, h = calc_size_by_total(1080, 1920, 2048)
        assert h > w
        assert w % 8 == 0
        assert h % 8 == 0

    def test_all_dimensions_multiple_of_8(self):
        for width, height in [(800, 600), (1920, 1080), (3000, 4000), (100, 100)]:
            w, h = calc_size_by_total(width, height, 2048)
            assert w % 8 == 0, f"width {w} not multiple of 8 for input {width}x{height}"
            assert h % 8 == 0, f"height {h} not multiple of 8 for input {width}x{height}"

    def test_sd15_total_1536(self):
        # SD 1.5: 512+512=1024 or other combos
        w, h = calc_size_by_total(800, 600, 1536)
        assert w % 8 == 0
        assert h % 8 == 0
        assert w + h <= 1536 + 8


# --- YumilValueReader logic ---

# Pure function copy for testing without torch dependency.
def parse_key_value(value: str, key: str, default: str = "") -> str:
    if not value.strip() or not key.strip():
        return default
    for pair in value.split(","):
        pair = pair.strip()
        if "=" in pair:
            k, v = pair.split("=", 1)
            if k.strip() == key.strip():
                return v.strip()
    return default


class TestValueReader:
    def test_simple_key(self):
        assert parse_key_value("strength=0.8,mode=ipadapter", "strength") == "0.8"

    def test_second_key(self):
        assert parse_key_value("strength=0.8,mode=ipadapter", "mode") == "ipadapter"

    def test_missing_key(self):
        assert parse_key_value("strength=0.8", "missing", "default") == "default"

    def test_empty_value_string(self):
        assert parse_key_value("", "key", "default") == "default"

    def test_empty_key(self):
        assert parse_key_value("strength=0.8", "", "default") == "default"

    def test_value_with_equals(self):
        assert parse_key_value("expr=a=b,mode=test", "expr") == "a=b"

    def test_whitespace_handling(self):
        assert parse_key_value(" strength = 0.8 , mode = test ", "strength") == "0.8"
        assert parse_key_value(" strength = 0.8 , mode = test ", "mode") == "test"


# --- Path splitting ---


class TestPathSplitting:
    def test_single_path(self):
        paths = [p.strip() for p in "img.png".split(",") if p.strip()]
        assert paths == ["img.png"]

    def test_multiple_paths(self):
        paths = [p.strip() for p in "a.png, b.png, c.png".split(",") if p.strip()]
        assert paths == ["a.png", "b.png", "c.png"]

    def test_empty_path(self):
        paths = [p.strip() for p in "".split(",") if p.strip()]
        assert paths == []

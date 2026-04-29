import re

from .parser import deserialize_parsed_data, parse_prompt, serialize_parsed_data


class YumilPromptParser:
    """
    Parses prompt text containing ###_Path(...).Value(...).Text(...)_### blocks.

    Outputs clean text (blocks replaced with Text() values) and structured
    data for downstream block selector/loader nodes.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                        "tooltip": "Prompt text (may contain ###_Path(...).Value(...).Text(...)_### blocks)",
                    },
                ),
            },
        }

    RETURN_TYPES = ("STRING", "INT", "STRING")
    RETURN_NAMES = ("clean_text", "block_count", "PARSED_DATA")
    FUNCTION = "execute"
    CATEGORY = "Yumil/Prompt"

    def execute(self, prompt: str):
        result = parse_prompt(prompt)
        block_count = len(result.blocks)
        parsed_data = serialize_parsed_data(result.blocks)

        return (result.clean_text, block_count, parsed_data)


class YumilLoraStripper:
    """
    Removes all <lora:...:weight> tags from text and outputs
    the clean text and extracted lora information separately.
    """

    LORA_PATTERN = re.compile(r"<lora:[^:>]+:[^>]+>")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": (
                    "STRING",
                    {
                        "forceInput": True,
                        "tooltip": "Text containing <lora:name:weight> tags",
                    },
                ),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("text", "loras")
    FUNCTION = "execute"
    CATEGORY = "Yumil/Prompt"

    def execute(self, text: str):
        lora_tags = self.LORA_PATTERN.findall(text)
        clean = self.LORA_PATTERN.sub("", text)

        # Clean up leftover comma/whitespace artifacts
        clean = re.sub(r",\s*,", ",", clean)
        clean = re.sub(r"^\s*,\s*", "", clean)
        clean = re.sub(r"\s*,\s*$", "", clean)
        clean = re.sub(r"\s{2,}", " ", clean)
        clean = clean.strip()

        loras = "".join(lora_tags)

        return (clean, loras)


class YumilTextJoin:
    """
    Joins multiple text inputs with a delimiter.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "delimiter": (
                    "STRING",
                    {
                        "default": ", ",
                        "multiline": True,
                        "tooltip": "Delimiter to join texts",
                    },
                ),
            },
            "optional": {
                "text_0": ("STRING", {"forceInput": True}),
                "text_1": ("STRING", {"forceInput": True}),
                "text_2": ("STRING", {"forceInput": True}),
                "text_3": ("STRING", {"forceInput": True}),
                "text_4": ("STRING", {"forceInput": True}),
                "text_5": ("STRING", {"forceInput": True}),
                "text_6": ("STRING", {"forceInput": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "execute"
    CATEGORY = "Yumil/Prompt"

    def execute(self, delimiter: str, **kwargs):
        parts = []
        for i in range(7):
            text = kwargs.get(f"text_{i}")
            if text is not None and text.strip():
                parts.append(text)
        return (delimiter.join(parts),)


NODE_CLASS_MAPPINGS = {
    "YumilPromptParser": YumilPromptParser,
    "YumilLoraStripper": YumilLoraStripper,
    "YumilTextJoin": YumilTextJoin,
}

class YumilValueReader:
    """
    Extracts a specific value from a key=value comma-separated string.

    Input format: "key1=val1,key2=val2"
    Use multiple instances to extract different keys.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": (
                    "STRING",
                    {
                        "forceInput": True,
                        "tooltip": "Key=value string from Block Selector value output.",
                    },
                ),
                "key": (
                    "STRING",
                    {
                        "default": "",
                        "tooltip": "Key to look up.",
                    },
                ),
                "default_value": (
                    "STRING",
                    {
                        "default": "",
                        "tooltip": "Returned if key is not found.",
                    },
                ),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)
    FUNCTION = "execute"
    CATEGORY = "Yumil/Block"

    def execute(self, value: str, key: str, default_value: str):
        if not value.strip() or not key.strip():
            return (default_value,)

        for pair in value.split(","):
            pair = pair.strip()
            if "=" in pair:
                k, v = pair.split("=", 1)
                if k.strip() == key.strip():
                    return (v.strip(),)

        return (default_value,)


NODE_CLASS_MAPPINGS = {
    "YumilValueReader": YumilValueReader,
}

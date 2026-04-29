from .nodes.api import NODE_CLASS_MAPPINGS as api_class
from .nodes.prompt import NODE_CLASS_MAPPINGS as prompt_class
from .nodes.image import NODE_CLASS_MAPPINGS as image_class
from .nodes.value import NODE_CLASS_MAPPINGS as value_class
from .nodes.save import NODE_CLASS_MAPPINGS as save_class

NODE_CLASS_MAPPINGS = {
    **api_class,
    **prompt_class,
    **image_class,
    **value_class,
    **save_class,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ExternalPromptRequester": "External Prompt Requester",
    "YumilPromptParser": "Yumil Prompt Parser",
    "YumilLoraStripper": "Yumil Lora Stripper",
    "YumilBlockSelector": "Yumil Block Selector",
    "YumilImageLoader": "Yumil Image Loader",
    "YumilValueReader": "Yumil Value Reader",
    "YumilTextJoin": "Yumil Text Join",
    "YumilBatchSave": "Yumil Batch Save",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

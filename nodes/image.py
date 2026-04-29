import os

import numpy as np
import torch
from PIL import Image, ImageOps

from .parser import deserialize_parsed_data


def load_image_as_tensor(path: str) -> torch.Tensor:
    """
    Load an image file and convert to ComfyUI IMAGE tensor format.
    Shape: (1, H, W, C), float32, range [0, 1], RGB.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Image file not found: {path}")

    img = Image.open(path)
    img = ImageOps.exif_transpose(img)

    if img.mode == "RGBA":
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        img = background
    elif img.mode != "RGB":
        img = img.convert("RGB")

    np_img = np.array(img).astype(np.float32) / 255.0
    tensor = torch.from_numpy(np_img).unsqueeze(0)
    return tensor


def calc_size_by_total(width: int, height: int, target_total: int) -> tuple[int, int]:
    """
    Calculate new dimensions where width + height = target_total,
    preserving aspect ratio. Both dimensions are rounded to nearest 8
    (common requirement for SD/SDXL latent alignment).

    Example (SDXL, target_total=2048):
      3:2 image -> 1224x824  (sum=2048)
      1:1 image -> 1024x1024 (sum=2048)
      9:16 image -> 736x1312 (sum=2048)
    """
    aspect = width / height
    # w/h = aspect, w + h = target_total
    # -> h = target_total / (1 + aspect)
    new_h = target_total / (1 + aspect)
    new_w = target_total - new_h

    # Round to nearest multiple of 8
    new_w = max(8, round(new_w / 8) * 8)
    new_h = max(8, round(new_h / 8) * 8)

    return (new_w, new_h)


class YumilBlockSelector:
    """
    Extracts a single block's data from PARSED_DATA by index.

    Splits comma-separated paths into individual outputs (path_0 through path_3).
    Connect PARSED_DATA from YumilPromptParser.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "parsed_data": (
                    "STRING",
                    {
                        "forceInput": True,
                        "tooltip": "Connect PARSED_DATA from Yumil Prompt Parser",
                    },
                ),
                "index": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 99,
                        "step": 1,
                        "tooltip": "Block index (0-based)",
                    },
                ),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "INT", "STRING", "STRING")
    RETURN_NAMES = ("path_0", "path_1", "path_2", "path_3", "path_count", "value", "text")
    FUNCTION = "execute"
    CATEGORY = "Yumil/Block"

    def execute(self, parsed_data: str, index: int):
        blocks = deserialize_parsed_data(parsed_data)

        if not blocks:
            raise ValueError(
                "No blocks found in parsed data. "
                "Make sure the prompt contains ###_..._### blocks."
            )

        if index >= len(blocks):
            raise IndexError(
                f"Block index {index} out of range. "
                f"Only {len(blocks)} block(s) found (indices 0-{len(blocks) - 1})."
            )

        block = blocks[index]

        # Split comma-separated paths into individual outputs
        paths = [p.strip() for p in block.path.split(",") if p.strip()] if block.path else []
        path_outputs = [paths[i] if i < len(paths) else "" for i in range(4)]

        value = block.value if block.value else ""
        text = block.text if block.text else ""

        return (*path_outputs, len(paths), value, text)


class YumilImageLoader:
    """
    Loads a single image from a file path with optional resize.

    Connect a path output from YumilBlockSelector, or any STRING path.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "path": (
                    "STRING",
                    {
                        "forceInput": True,
                        "tooltip": "Image file path. Connect from Block Selector path output.",
                    },
                ),
                "resize_mode": (
                    ["disabled", "stretch", "crop_center", "pad_white"],
                    {
                        "default": "disabled",
                        "tooltip": "How to resize. 'disabled' keeps original size.",
                    },
                ),
                "target_total": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 8192,
                        "step": 64,
                        "tooltip": "Target width+height sum (e.g. 2048 for SDXL). 0 = no resize. Ignored when width/height are connected.",
                    },
                ),
            },
            "optional": {
                "width": (
                    "INT",
                    {
                        "forceInput": True,
                        "tooltip": "Override width. Connect from another Loader to match sizes.",
                    },
                ),
                "height": (
                    "INT",
                    {
                        "forceInput": True,
                        "tooltip": "Override height. Connect from another Loader to match sizes.",
                    },
                ),
            },
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT")
    RETURN_NAMES = ("image", "width", "height")
    FUNCTION = "execute"
    CATEGORY = "Yumil/Image"

    def execute(self, path: str, resize_mode: str, target_total: int,
                width: int = 0, height: int = 0):
        if not path.strip():
            raise ValueError("Image path is empty. Make sure a valid path is connected.")

        img = Image.open(path)
        img = ImageOps.exif_transpose(img)

        if img.mode == "RGBA":
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")

        # Determine target size: explicit width/height > target_total > original
        if width > 0 and height > 0:
            target_size = (width, height)
            effective_mode = resize_mode if resize_mode != "disabled" else "stretch"
        elif resize_mode != "disabled" and target_total > 0:
            target_size = calc_size_by_total(img.size[0], img.size[1], target_total)
            effective_mode = resize_mode
        else:
            target_size = None
            effective_mode = None

        if target_size and img.size != target_size:
            if effective_mode == "stretch":
                img = img.resize(target_size, Image.LANCZOS)
            elif effective_mode == "crop_center":
                img = ImageOps.fit(img, target_size, Image.LANCZOS)
            elif effective_mode == "pad_white":
                img.thumbnail(target_size, Image.LANCZOS)
                padded = Image.new("RGB", target_size, (255, 255, 255))
                offset = (
                    (target_size[0] - img.size[0]) // 2,
                    (target_size[1] - img.size[1]) // 2,
                )
                padded.paste(img, offset)
                img = padded

        np_img = np.array(img).astype(np.float32) / 255.0
        image_tensor = torch.from_numpy(np_img).unsqueeze(0)

        return (image_tensor, img.size[0], img.size[1])


NODE_CLASS_MAPPINGS = {
    "YumilBlockSelector": YumilBlockSelector,
    "YumilImageLoader": YumilImageLoader,
}

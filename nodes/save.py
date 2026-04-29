import os

import numpy as np
from PIL import Image


class YumilBatchSave:
    """
    Saves up to 6 input images as JPG and an optional text input as text.txt
    to a specified folder.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "parent_folder": (
                    "STRING",
                    {
                        "default": "",
                        "tooltip": "Parent folder path (e.g. C:/output/masks)",
                    },
                ),
                "folder_name": (
                    "STRING",
                    {
                        "default": "",
                        "tooltip": "Folder name to create. Also used as file name prefix (e.g. 'my_project' -> my_project.txt, my_project_0.jpg)",
                    },
                ),
            },
            "optional": {
                "text": (
                    "STRING",
                    {
                        "forceInput": True,
                        "tooltip": "Text to save as text.txt",
                    },
                ),
                "image_0": ("IMAGE", {"tooltip": "Saved as image_0.jpg"}),
                "image_1": ("IMAGE", {"tooltip": "Saved as image_1.jpg"}),
                "image_2": ("IMAGE", {"tooltip": "Saved as image_2.jpg"}),
                "image_3": ("IMAGE", {"tooltip": "Saved as image_3.jpg"}),
                "image_4": ("IMAGE", {"tooltip": "Saved as image_4.jpg"}),
                "image_5": ("IMAGE", {"tooltip": "Saved as image_5.jpg"}),
            },
        }

    RETURN_TYPES = ()
    OUTPUT_NODE = True
    FUNCTION = "execute"
    CATEGORY = "Yumil/IO"

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("nan")

    def execute(self, parent_folder: str, folder_name: str, **kwargs):
        if not parent_folder.strip():
            raise ValueError("parent_folder must not be empty.")
        if not folder_name.strip():
            raise ValueError("folder_name must not be empty.")

        save_folder = os.path.join(parent_folder.strip(), folder_name.strip())
        os.makedirs(save_folder, exist_ok=True)
        basename = folder_name.strip()

        # Save text
        text = kwargs.get("text")
        if text is not None:
            text_path = os.path.join(save_folder, f"{basename}.txt")
            with open(text_path, "w", encoding="utf-8") as f:
                f.write(text)

        # Save images
        for i in range(6):
            image_tensor = kwargs.get(f"image_{i}")
            if image_tensor is None:
                continue
            # ComfyUI IMAGE tensor: (batch, H, W, C) float32 [0,1]
            np_img = (image_tensor[0].cpu().numpy() * 255.0).clip(0, 255).astype(np.uint8)
            img = Image.fromarray(np_img)
            img_path = os.path.join(save_folder, f"{basename}_{i}.jpg")
            img.save(img_path, "JPEG", quality=95)

        return ()


NODE_CLASS_MAPPINGS = {
    "YumilBatchSave": YumilBatchSave,
}

import os
import secrets
from pathlib import Path

import requests


class ExternalPromptRequester:
    API_SERVER_PORT = 19720

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "timeout_seconds": ("INT", {"default": 240, "min": 5, "max": 600}),

                "prompt_1": ("STRING", {"default": "Positive"}),
                "prompt_2": ("STRING", {"default": "Negative"}),
                "prompt_3": ("STRING", {"default": "Pose"}),
            },
            "optional": {
                "prompt_4": ("STRING", {"default": ""}),
                "prompt_5": ("STRING", {"default": ""}),
                "prompt_6": ("STRING", {"default": ""}),
                "prompt_7": ("STRING", {"default": ""}),
                "prompt_8": ("STRING", {"default": ""}),
                "prompt_9": ("STRING", {"default": ""}),
                "prompt_10": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",) * 10
    RETURN_NAMES = ("prompt_1", "prompt_2", "prompt_3", "prompt_4", "prompt_5",
                    "prompt_6", "prompt_7", "prompt_8", "prompt_9", "prompt_10")
    FUNCTION = "request_external_prompt"
    OUTPUT_NODE = True
    CATEGORY = "Yumil/API"

    def request_external_prompt(self, timeout_seconds,
                                prompt_1, prompt_2, prompt_3,
                                prompt_4="", prompt_5="", prompt_6="",
                                prompt_7="", prompt_8="", prompt_9="", prompt_10=""):

        api_key = self._load_api_key()
        if not api_key:
            print("[ExternalPromptRequester] API key not found. Please open MPM and generate an API key in API Server Settings.")
            return ("",) * 10

        session_id = f"comfyui-{secrets.token_hex(8)}"
        url = f"http://127.0.0.1:{self.API_SERVER_PORT}/api/v1/generate"

        try:
            response = requests.post(
                url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={"session_id": session_id},
                timeout=timeout_seconds,
            )
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            print(f"[ExternalPromptRequester] Cannot connect to API server at port {self.API_SERVER_PORT}. Is it running?")
            return ("",) * 10
        except requests.exceptions.Timeout:
            print(f"[ExternalPromptRequester] Request timed out after {timeout_seconds}s")
            return ("",) * 10
        except requests.exceptions.HTTPError as e:
            print(f"[ExternalPromptRequester] API error: {e.response.status_code} - {e.response.text}")
            return ("",) * 10

        data = response.json()
        api_results = data.get("results", [])

        # Build a lookup from category_name to prompt
        prompt_lookup = {
            r["category_name"]: r["prompt"]
            for r in api_results
            if r.get("success")
        }

        names = [prompt_1, prompt_2, prompt_3, prompt_4, prompt_5,
                 prompt_6, prompt_7, prompt_8, prompt_9, prompt_10]

        results = []
        for name in names:
            name = name.strip()
            results.append(prompt_lookup.get(name, "") if name else "")

        print(f"[ExternalPromptRequester] Generated prompts received (session: {session_id})")
        return tuple(results)

    @staticmethod
    def _load_api_key():
        """Load API key from ~/.mpm/api_key file, fallback to MPM_API_KEY env var."""
        key_file = Path.home() / ".mpm" / "api_key"
        if key_file.exists():
            try:
                return key_file.read_text(encoding="utf-8").strip()
            except Exception:
                pass
        return os.environ.get("MPM_API_KEY", "")

    @classmethod
    def IS_CHANGED(s, **kwargs):
        return float("nan")


NODE_CLASS_MAPPINGS = {
    "ExternalPromptRequester": ExternalPromptRequester,
}

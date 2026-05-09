# comfyui-yumil-mpm

English | [Japanese](README_ja.md)

Custom nodes for [ComfyUI](https://github.com/comfyanonymous/ComfyUI) that integrate with [Yumil MPM](https://github.com/maigonia/YumilMPM), a prompt management tool for AI image generation.

## Requirements

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
- [Yumil MPM](https://github.com/maigonia/YumilMPM)

## Installation

### ComfyUI Manager

Registration is in preparation. Please use the manual installation steps for now.

### Manual

Clone this repository into your ComfyUI `custom_nodes` folder:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/maigonia/comfyui-yumil-mpm.git
cd comfyui-yumil-mpm
pip install -r requirements.txt
```

Restart ComfyUI after installation.

## Example Workflows

Example ComfyUI workflows are included in the [`workflow`](workflow) folder.

![Yumil MPM auto-send workflow](docs/images/03-auto-send.png)

- [`Simple Example.json`](workflow/Simple%20Example.json): a minimal workflow that requests positive and negative prompts from Yumil MPM.
- [`Simple Text To Image With Yumil MPM.json`](workflow/Simple%20Text%20To%20Image%20With%20Yumil%20MPM.json): a text-to-image workflow using Yumil MPM prompt categories.
- [`Controlnet With Yumil MPM.json`](workflow/Controlnet%20With%20Yumil%20MPM.json): a ControlNet example that uses parser-style prompt data.

Some workflows use additional ComfyUI custom nodes and model files. Open the notes inside each workflow to check the required extensions and models.

## Nodes

### External Prompt Requester

**Category:** `Yumil/API`

Requests prompt generation from Yumil MPM. While Yumil MPM's On-Demand Generation is active, each time the workflow passes through this node, a generation request is sent to Yumil MPM and the generated results are returned. You can connect up to 10 category names and receive generated prompt text for each category.

**Setup:**

1. Launch Yumil MPM.
2. Press the **Demand** button in the Generation panel to enable On-Demand Generation.
3. Make sure the Yumil MPM API server is enabled and an API key has been generated.

**Inputs:**

- `timeout_seconds`: request timeout in seconds, from 5 to 600. Default: `240`.
- `prompt_1` to `prompt_10`: category names to request prompts for.

**Outputs:**

- `prompt_1` to `prompt_10`: generated prompt text for each category.

### Yumil Prompt Parser

**Category:** `Yumil/Prompt`

Parses prompt text containing blocks in this format:

```text
###_Path(...).Value(...).Text(...)_###
```

Each element is optional.

- `Path(...)`: one or more comma-separated file paths. These are not limited to images.
- `Value(...)`: comma-separated `key=value` parameters, such as `strength=0.8,mode=ipadapter`.
- `Text(...)`: prompt text. Blocks with `Text(...)` are replaced by that text in the clean prompt output. Blocks without `Text(...)` are removed from the clean prompt output.

**Use cases:**

- Extract reference image paths embedded in prompts.
- Pass metadata such as ControlNet or IPAdapter parameters through the workflow.
- Keep prompt text, file paths, and parameter values bundled together in a single prompt string.

**Examples:**

```text
###_Path(img0.png,img1.png).Value(strength=0.8,mode=ipadapter).Text(hello)_###
###_Path(img.png).Text(hello)_###
###_Path(img.png)_###
###_Value(mode=test).Text(hello)_###
```

**Inputs:**

- `prompt`: prompt text that may contain parser blocks.

**Outputs:**

- `clean_text`: prompt text with blocks replaced or removed.
- `block_count`: number of detected blocks.
- `PARSED_DATA`: serialized structured data for downstream nodes.

### Yumil Block Selector

**Category:** `Yumil/Block`

Selects one parsed block by index and extracts its components. Connect `PARSED_DATA` from Yumil Prompt Parser. Use multiple instances with different indices to extract multiple blocks.

**Inputs:**

- `parsed_data`: output from Yumil Prompt Parser.
- `index`: zero-based block index.

**Outputs:**

- `path_0` to `path_3`: individual paths from `Path(...)`.
- `path_count`: number of paths in the selected block.
- `value`: raw `key=value` parameter string.
- `text`: associated text content.

### Yumil Image Loader

**Category:** `Yumil/Image`

Loads a single image from a file path and converts it to a ComfyUI `IMAGE` tensor. It can receive a path from Yumil Block Selector or any string path.

**Inputs:**

- `path`: image file path.
- `resize_mode`: `disabled`, `stretch`, `crop_center`, or `pad_white`.
- `target_total`: target width plus height, such as `2048` for SDXL. `0` disables this resize target.
- `width` / `height` optional: explicit size override.

**Outputs:**

- `image`: loaded image tensor.
- `width` / `height`: image dimensions.

### Yumil Value Reader

**Category:** `Yumil/Block`

Reads a specific key from a comma-separated `key=value` string and returns the corresponding value. If the key is not found, it returns the configured default value.

**Inputs:**

- `value`: key-value string from Yumil Block Selector.
- `key`: key to look up.
- `default_value`: returned when the key is not found.

**Outputs:**

- `result`: value for the specified key.

### Yumil Lora Stripper

**Category:** `Yumil/Prompt`

Extracts and removes all `<lora:name:weight>` tags from text.

**Inputs:**

- `text`: text containing LoRA tags.

**Outputs:**

- `text`: clean text with LoRA tags removed.
- `loras`: extracted LoRA tags concatenated together.

### Yumil Text Join

**Category:** `Yumil/Prompt`

Joins up to 7 text inputs with a configurable delimiter. Empty inputs are skipped.

**Inputs:**

- `delimiter`: separator string. Default: `, `.
- `text_0` to `text_6`: text inputs.

**Outputs:**

- `text`: joined result.

### Yumil Batch Save

**Category:** `Yumil/IO`

Saves up to 6 images as JPEG files and an optional text file to a specified folder.

**Inputs:**

- `parent_folder`: output directory path.
- `folder_name`: subfolder name, also used as the filename prefix.
- `text` optional: saved as `{folder_name}.txt`.
- `image_0` to `image_5`: saved as `{folder_name}_0.jpg`, etc.

## Running Tests

```bash
python -m pytest -v
```

## Links

- [Yumil MPM](https://github.com/maigonia/YumilMPM)
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI)

## License

[MIT](LICENSE)

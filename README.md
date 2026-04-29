# comfyui-yumil-mpm

English | [日本語](README_ja.md)

Custom nodes for [ComfyUI](https://github.com/comfyanonymous/ComfyUI) that integrate with [Yumil MPM](https://github.com/maigonia/YumilMPM) — a prompt management tool for AI image generation.

## Requirements

- [Yumil MPM](https://github.com/maigonia/YumilMPM)

## Installation

### ComfyUI Manager

Registration is in preparation. Please use the manual installation below for now.

### Manual

Clone this repository into your ComfyUI `custom_nodes` folder:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/maigonia/comfyui-yumil-mpm.git
cd comfyui-yumil-mpm
pip install -r requirements.txt
```

Restart ComfyUI after installation.

## Nodes

### External Prompt Requester

**Category:** Yumil/API

Requests prompt generation from Yumil MPM. While Yumil MPM's On-Demand Generation is active, each time the workflow passes through this node, a generation request is sent to Yumil MPM and the auto-generated result is returned. Connect up to 10 category names and receive the generated prompt text for each.

**Setup:**
1. Launch Yumil MPM.
2. Press the **Demand** button in the Generation panel (bottom-left) to enable On-Demand Generation.

**Inputs:**
- `timeout_seconds` — Request timeout (5–600s, default: 240)
- `prompt_1` to `prompt_10` — Category names to request prompts for

**Outputs:**
- `prompt_1` to `prompt_10` — Generated prompt text for each category

### Yumil Prompt Parser

**Category:** Yumil/Prompt

**Use cases:**
- Extract file paths and parameters embedded in prompts (e.g. reference images for ControlNet/IPAdapter)
- Bundle multiple paths in a single block (e.g. multiple reference images)
- Handle paths paired with key-value parameters and prompt text

Parses prompt text containing `###_Path(...).Value(...).Text(...)_###` blocks. Each element (Path, Value, Text) is optional.

- **Path** — Supports multiple comma-separated paths (e.g. `Path(img0.png,img1.png)`). Not limited to images — any file path can be passed
- **Value** — Comma-separated `key=value` parameters (e.g. `Value(strength=0.8,mode=ipadapter)`)
- **Text** — Prompt text content. Supports multiple lines

Blocks with `Text()` are replaced by their text value in the clean output; blocks without `Text()` are removed. Multiple blocks in a single prompt can be parsed at once. Inside each element, raw content is used as-is — no escape sequences needed. Newlines, special characters, and nested parentheses all work naturally.

**Examples:**
- `###_Path(img0.png,img1.png).Value(strength=0.8,mode=ipadapter).Text(hello)_###` — Multiple paths, parameters, and text are all extracted; tag is replaced with `hello` in the prompt
- `###_Path(img.png).Text(hello)_###` — Path and text extracted; tag is replaced with `hello`
- `###_Path(img.png)_###` — Path extracted; tag is removed from the prompt
- `###_Value(mode=test).Text(hello)_###` — Parameters and text extracted without a path

**Inputs:**
- `prompt` — Prompt text (may contain parser blocks)

**Outputs:**
- `clean_text` — Prompt with blocks replaced/removed
- `block_count` — Number of blocks found
- `PARSED_DATA` — Structured data for downstream nodes

### Yumil Block Selector

**Category:** Yumil/Block

**Use cases:**
- Extract paths, parameters, and text from parsed blocks
- Feed paths to Yumil Image Loader or other nodes
- Feed parameters to Yumil Value Reader

Selects a single block from parsed data by index and extracts its components. Comma-separated paths in `Path()` are split into individual outputs (up to 4). Connect `PARSED_DATA` from Yumil Prompt Parser. Use multiple instances with different indices to extract individual blocks.

**Inputs:**
- `parsed_data` — Connect from Yumil Prompt Parser
- `index` — Block index (0-based)

**Outputs:**
- `path_0` to `path_3` — Individual paths (empty string if not present)
- `path_count` — Number of paths in the block
- `value` — Raw key=value parameter string
- `text` — Associated text content

### Yumil Image Loader

**Category:** Yumil/Image

**Use cases:**
- Load an image from a path output of Yumil Block Selector
- Load any image from a file path string

Loads a single image from a file path with optional resize. Connect a path output from Yumil Block Selector, or any STRING path.

**Inputs:**
- `path` — Image file path
- `resize_mode` — `disabled`, `stretch`, `crop_center`, or `pad_white`
- `target_total` — Target width+height sum (e.g. 2048 for SDXL). 0 = no resize.
- `width` / `height` (optional) — Override dimensions.

**Outputs:**
- `image` — Loaded image tensor
- `width` / `height` — Image dimensions

### Yumil Value Reader

**Category:** Yumil/Block

**Use cases:**
- Extract a specific parameter from a key=value string (e.g. `strength=0.8,mode=ipadapter`)
- Use multiple instances to read different keys

Reads a specific key from a comma-separated `key=value` string and returns the corresponding value. If the key is not found, returns the default value.

**Inputs:**
- `value` — Key=value string from Block Selector
- `key` — Key to look up
- `default_value` — Returned if key is not found (default: empty string)

**Outputs:**
- `result` — The value for the specified key

### Yumil Lora Stripper

**Category:** Yumil/Prompt

Extracts and removes all `<lora:name:weight>` tags from text.

**Inputs:**
- `text` — Text containing lora tags

**Outputs:**
- `text` — Clean text with lora tags removed
- `loras` — Extracted lora tags concatenated

### Yumil Text Join

**Category:** Yumil/Prompt

Joins up to 7 text inputs with a configurable delimiter. Empty inputs are skipped.

**Inputs:**
- `delimiter` — Separator string (default: `, `)
- `text_0` to `text_6` — Text inputs

**Outputs:**
- `text` — Joined result

### Yumil Batch Save

**Category:** Yumil/IO

Saves up to 6 images (JPEG) and an optional text file to a specified folder.

**Inputs:**
- `parent_folder` — Output directory path
- `folder_name` — Subfolder name (also used as filename prefix)
- `text` (optional) — Saved as `{folder_name}.txt`
- `image_0` to `image_5` — Images saved as `{folder_name}_0.jpg`, etc.

## Running Tests

```bash
cd tests
python -m pytest -v
```

## Links

- [Yumil MPM (GitHub)](https://github.com/maigonia/YumilMPM)

## License

[MIT](LICENSE)

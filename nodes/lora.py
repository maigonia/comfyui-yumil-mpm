"""Yumil Prompt Lora Loader node.

A ComfyUI custom node that parses ``<lora:name:strength>`` tags from a prompt
string and applies them to a MODEL (and optionally a CLIP).

Designed to work even when no CLIP is available (e.g. LTXV pipelines), unlike
rgthree-comfy's Power Prompt which requires both MODEL and CLIP for lora
loading.

Lora-tag regex and fuzzy filename matching are adapted from rgthree-comfy
(MIT License, Copyright (c) 2023 Regis Gaughan, III).
"""

import os
import re

import folder_paths
from nodes import LoraLoader


LORA_PATTERN = re.compile(r'<lora:([^:>]*?)(?::(-?\d*(?:\.\d*)?))?>')


def find_lora_file(name, lora_paths):
  """Resolve a lora tag name to an actual file path inside the loras folder.

  Tries exact match first, then progressively fuzzier matching (with/without
  extension, basename only, substring).  Returns the resolved path or None.
  """
  if name in lora_paths:
    return name

  paths_no_ext = [os.path.splitext(p)[0] for p in lora_paths]
  if name in paths_no_ext:
    return lora_paths[paths_no_ext.index(name)]

  name_no_ext = os.path.splitext(name)[0]
  if name_no_ext in paths_no_ext:
    return lora_paths[paths_no_ext.index(name_no_ext)]

  basenames = [os.path.basename(p) for p in lora_paths]
  if name in basenames:
    return lora_paths[basenames.index(name)]

  name_basename = os.path.basename(name)
  if name_basename in basenames:
    return lora_paths[basenames.index(name_basename)]

  basenames_no_ext = [os.path.splitext(b)[0] for b in basenames]
  if name in basenames_no_ext:
    return lora_paths[basenames_no_ext.index(name)]

  name_basename_no_ext = os.path.splitext(name_basename)[0]
  if name_basename_no_ext in basenames_no_ext:
    return lora_paths[basenames_no_ext.index(name_basename_no_ext)]

  for i, p in enumerate(lora_paths):
    if name in p:
      return lora_paths[i]

  return None


def parse_lora_tags(prompt):
  """Return list of ``{'name': str, 'strength': float}`` parsed from prompt."""
  entries = []
  for tag, strength_str in LORA_PATTERN.findall(prompt):
    try:
      strength = float(strength_str) if strength_str else 1.0
    except ValueError:
      strength = 1.0
    entries.append({'name': tag, 'strength': strength})
  return entries


def strip_lora_tags(prompt):
  return LORA_PATTERN.sub('', prompt)


class YumilPromptLoraLoader:
  """Apply ``<lora:...>`` tags found in a prompt to MODEL (and CLIP if given)."""

  @classmethod
  def INPUT_TYPES(cls):
    return {
      'required': {
        'model': ('MODEL',),
        'prompt': ('STRING', {'multiline': True, 'default': ''}),
        'strip_tags': ('BOOLEAN', {'default': True}),
      },
      'optional': {
        'clip': ('CLIP',),
      },
    }

  RETURN_TYPES = ('MODEL', 'CLIP', 'STRING')
  RETURN_NAMES = ('MODEL', 'CLIP', 'TEXT')
  FUNCTION = 'apply'
  CATEGORY = 'Yumil/Loaders'

  def apply(self, model, prompt, strip_tags, clip=None):
    lora_paths = folder_paths.get_filename_list('loras')
    entries = parse_lora_tags(prompt)

    loader = LoraLoader()
    loaded = 0
    not_found = []

    for entry in entries:
      strength_model = entry['strength']
      if strength_model == 0:
        print(f'[YumilPromptLoraLoader] Skipping "{entry["name"]}" (strength 0)')
        continue

      file = find_lora_file(entry['name'], lora_paths)
      if file is None:
        not_found.append(entry['name'])
        continue

      strength_clip = 0 if clip is None else strength_model
      model, clip = loader.load_lora(model, clip, file, strength_model, strength_clip)
      print(f'[YumilPromptLoraLoader] Loaded "{file}" '
            f'(model={strength_model}, clip={strength_clip})')
      loaded += 1

    if not_found:
      print(f'[YumilPromptLoraLoader] Not found: {not_found}')
    if entries:
      print(f'[YumilPromptLoraLoader] {loaded}/{len(entries)} lora(s) applied.')

    out_text = strip_lora_tags(prompt) if strip_tags else prompt
    return (model, clip, out_text)


NODE_CLASS_MAPPINGS = {
    "YumilPromptLoraLoader": YumilPromptLoraLoader,
}

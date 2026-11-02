import re
from typing import List, Tuple, Optional, Dict, Any
from ..projects.models import TextAssetJob

class PromptParser:
    def parse(self, text: str) -> Tuple[List[TextAssetJob], List[Dict[str, Any]]]:
        jobs = []
        diagnostics = []

        lines = text.splitlines()
        current_block = None
        block_start_line = 0
        block_data = {}
        prompt_lines = []
        current_key = None
        seen_keys = set()
        seen_slugs = set()
        block_error = False

        for line_idx, line in enumerate(lines, 1):
            stripped = line.strip()

            if stripped == "=== ASSET ===":
                if current_block:
                    # Unclosed block before new block starts
                    diagnostics.append({
                        "code": "UNCLOSED_BLOCK",
                        "message": "Block started but never ended with === END ===",
                        "line": block_start_line,
                        "asset": f"Block {len(jobs) + 1}",
                        "field": None
                    })

                current_block = True
                block_start_line = line_idx
                block_data = {}
                prompt_lines = []
                current_key = None
                seen_keys = set()
                block_error = False
                continue

            if not current_block:
                if stripped and not stripped.startswith("#"):
                    diagnostics.append({
                        "code": "OUTSIDE_BLOCK",
                        "message": f"Content found outside of asset block: {stripped[:20]}...",
                        "line": line_idx,
                        "asset": None,
                        "field": None
                    })
                continue

            if stripped == "=== END ===":
                # Validate and finalize block
                name = block_data.get("name")
                prompt = "\n".join(prompt_lines).strip()
                ratio = block_data.get("ratio")
                slug = self.normalize_name(name) if name else ""

                if ratio and not re.fullmatch(r"[1-9]\d*:[1-9]\d*", ratio):
                    diagnostics.append({"code": "INVALID_RATIO", "message": "Ratio must be two positive integers", "line": block_start_line, "asset": name, "field": "ratio"})
                    block_error = True
                if name and not slug:
                    diagnostics.append({"code": "INVALID_SLUG", "message": "Name produces an empty slug", "line": block_start_line, "asset": name, "field": "name"})
                    block_error = True
                elif slug in seen_slugs:
                    diagnostics.append({"code": "DUPLICATE_SLUG", "message": "Asset slug is already used", "line": block_start_line, "asset": name, "field": "name"})
                    block_error = True

                if not name:
                    diagnostics.append({
                        "code": "MISSING_NAME",
                        "message": "Asset block is missing a name",
                        "line": block_start_line,
                        "asset": f"Block {len(jobs) + 1}",
                        "field": "name"
                    })

                if not prompt:
                    diagnostics.append({
                        "code": "MISSING_PROMPT",
                        "message": "Asset block is missing a prompt",
                        "line": block_start_line,
                        "asset": f"Block {len(jobs) + 1}",
                        "field": "prompt"
                    })

                if not ratio:
                    diagnostics.append({
                        "code": "MISSING_RATIO",
                        "message": "Ratio is missing; will fallback to target size",
                        "line": block_start_line,
                        "asset": f"Block {len(jobs) + 1}",
                        "field": "ratio",
                        "level": "warning"
                    })

                if name and prompt and not block_error:
                    jobs.append(TextAssetJob(
                        name=name,
                        ratio=ratio,
                        prompt=prompt,
                        target_width=512,
                        target_height=512
                    ))
                    seen_slugs.add(slug)

                current_block = False
                current_key = None
                continue

            if not stripped:
                if current_key == "prompt":
                    prompt_lines.append(line)
                continue

            # Key detection
            if ":" in stripped:
                key_part, val_part = stripped.split(":", 1)
                key = key_part.strip().lower()

                if key in ["name", "ratio", "prompt"]:
                    if key in seen_keys:
                        diagnostics.append({
                            "code": "DUPLICATE_KEY",
                            "message": f"Duplicate key '{key}' in block",
                            "line": line_idx,
                            "asset": f"Block {len(jobs) + 1}",
                            "field": key
                        })
                        block_error = True

                    current_key = key
                    seen_keys.add(key)
                    if key != "prompt":
                        block_data[key] = val_part.strip()

                    if key == "prompt":
                        # Start prompt with the first line's value
                        prompt_lines.append(val_part.strip())
                    continue
                if current_key != "prompt" and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
                    diagnostics.append({"code": "UNKNOWN_KEY", "message": f"Unknown key '{key}'", "line": line_idx, "asset": block_data.get("name"), "field": key})
                    block_error = True
                    continue

            # Content handling
            if current_key == "prompt":
                prompt_lines.append(line)
            elif not current_key:
                # Content before any key
                diagnostics.append({
                    "code": "UNKNOWN_CONTENT",
                    "message": f"Unexpected content before key: {stripped[:20]}...",
                    "line": line_idx,
                    "asset": f"Block {len(jobs) + 1}",
                    "field": None
                })
            else:
                # Content after name/ratio but before prompt
                # In our case, it should be treated as a prompt if prompt is missing
                # but according to contract, it should probably be an error or part of prompt.
                # We'll treat it as part of the prompt if we've seen 'prompt:'
                # Otherwise it's just unknown.
                diagnostics.append({
                    "code": "UNKNOWN_CONTENT",
                    "message": f"Unexpected content after {current_key}: {stripped[:20]}...",
                    "line": line_idx,
                    "asset": f"Block {len(jobs) + 1}",
                    "field": None
                })

        if current_block:
            diagnostics.append({
                "code": "UNCLOSED_BLOCK",
                "message": "Final block was never closed with === END ===",
                "line": block_start_line,
                "asset": f"Block {len(jobs) + 1}",
                "field": None
            })

        return jobs, diagnostics

    def normalize_name(self, name: str) -> str:
        normalized = name.lower().strip()
        normalized = re.sub(r'[^a-z0-9]+', '-', normalized)
        normalized = normalized.strip('-')
        return normalized

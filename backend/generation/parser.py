import re
from typing import List, Tuple, Optional, Dict, Any
from ..projects.models import TextAssetJob

OPTIONAL_KEYS = ("width", "height", "max_kb", "format", "compression", "fit", "remove_background")
FORMAT_VALUES = ("png", "webp", "jpeg")
COMPRESSION_VALUES = ("lossless", "balanced", "smallest")
FIT_VALUES = ("fit", "fill")
# optional key -> TextAssetJob field
JOB_FIELDS = {
    "width": "target_width",
    "height": "target_height",
    "max_kb": "max_kb",
    "format": "output_format",
    "compression": "compression_mode",
    "fit": "fit_mode",
    "remove_background": "remove_background",
}


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
        key_lines = {}

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
                key_lines = {}
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

                options, option_errors = self.parse_options(block_data, key_lines, name or f"Block {len(jobs) + 1}")
                if option_errors:
                    diagnostics.extend(option_errors)
                    block_error = True

                if name and prompt and not block_error:
                    try:
                        jobs.append(TextAssetJob(
                            name=name,
                            ratio=ratio,
                            prompt=prompt,
                            **{"target_width": 512, "target_height": 512, **options}
                        ))
                        seen_slugs.add(slug)
                    except ValueError as exc:
                        diagnostics.append({"code": "INVALID_OPTIONS", "message": str(exc).splitlines()[-1] if str(exc) else "Invalid options", "line": block_start_line, "asset": name, "field": None})

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

                if key in OPTIONAL_KEYS and current_key != "prompt":
                    if key in seen_keys:
                        diagnostics.append({
                            "code": "DUPLICATE_KEY",
                            "message": f"Duplicate key '{key}' in block",
                            "line": line_idx,
                            "asset": block_data.get("name") or f"Block {len(jobs) + 1}",
                            "field": key
                        })
                        block_error = True
                    current_key = key
                    seen_keys.add(key)
                    block_data[key] = val_part.strip()
                    key_lines[key] = line_idx
                    continue

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

    def parse_options(self, data: Dict[str, str], key_lines: Dict[str, int], asset: str):
        """Validate optional block keys. Returns (job field values, diagnostics)."""
        options: Dict[str, Any] = {}
        errors: List[Dict[str, Any]] = []

        def fail(key, message):
            errors.append({"code": "INVALID_" + key.upper(), "message": message, "line": key_lines.get(key), "asset": asset, "field": key})

        for key in ("width", "height", "max_kb"):
            if key in data:
                raw = data[key]
                if re.fullmatch(r"[1-9]\d*", raw):
                    options[JOB_FIELDS[key]] = int(raw)
                else:
                    fail(key, f"{key} must be a positive integer")
        if ("width" in data) != ("height" in data):
            missing = "height" if "width" in data else "width"
            errors.append({"code": "INCOMPLETE_SIZE", "message": "width and height must be given together", "line": key_lines.get("width") or key_lines.get("height"), "asset": asset, "field": missing})

        for key, allowed in (("format", FORMAT_VALUES), ("compression", COMPRESSION_VALUES), ("fit", FIT_VALUES)):
            if key in data:
                value = data[key].lower()
                if value in allowed:
                    options[JOB_FIELDS[key]] = value
                else:
                    fail(key, f"{key} must be one of: {', '.join(allowed)}")

        if "remove_background" in data:
            value = data["remove_background"].lower()
            if value in ("true", "false"):
                options["remove_background"] = value == "true"
            else:
                fail("remove_background", "remove_background must be true or false")

        if options.get("output_format") == "jpeg" and options.get("remove_background") is True:
            errors.append({"code": "JPEG_REMOVE_BACKGROUND", "message": "JPEG does not support transparency; use png or webp with remove_background", "line": key_lines.get("remove_background"), "asset": asset, "field": "remove_background"})
        return options, errors

    def normalize_name(self, name: str) -> str:
        normalized = name.lower().strip()
        normalized = re.sub(r'[^a-z0-9]+', '-', normalized)
        normalized = normalized.strip('-')
        return normalized

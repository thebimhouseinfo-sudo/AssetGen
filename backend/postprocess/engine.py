from PIL import Image, ImageOps
import os
import io
from pathlib import Path
import uuid
import tempfile
from typing import Tuple, Optional, Dict, Any
from ..projects.models import OutputSettings
from .background import BackgroundRemover

class OutputEngine:
    def __init__(self, output_root: str, remover: Optional[Any] = None):
        self.output_root = output_root
        self.remover = remover

    def process(self, image: Image.Image, settings: OutputSettings) -> Tuple[str, Dict[str, Any]]:
        # 0. Optional background removal on the original image, before resize
        transparent = bool(settings.remove_background)
        if transparent:
            if settings.format == "jpeg":
                raise ValueError("JPEG does not support transparency; use png or webp with remove_background")
            remover = self.remover or BackgroundRemover()
            image = remover.remove(image).convert("RGBA")

        # 1. Resize (Fit/Fill)
        bg_color = "#00000000" if transparent else settings.background_color
        processed_img = self.resize(image, settings.width, settings.height, settings.fit_mode, bg_color, transparent)

        # 2. Format and Compression
        final_path, metadata = self.save_with_compression(processed_img, settings)

        return final_path, metadata

    def resize(self, image: Image.Image, target_w: int, target_h: int, mode: str, bg_color: str, transparent_bg: bool = False) -> Image.Image:
        img_w, img_h = image.size

        if mode == "fit":
            # Scale to fit inside target, pad the rest
            scale = min(target_w / img_w, target_h / img_h)
            new_w, new_h = int(img_w * scale), int(img_h * scale)
            resized = image.resize((new_w, new_h), Image.Resampling.LANCZOS)

            # Create background
            new_img = Image.new("RGBA", (target_w, target_h), bg_color)
            offset_x = (target_w - new_w) // 2
            offset_y = (target_h - new_h) // 2
            if transparent_bg:
                # Copy RGBA as-is; masked paste would square the alpha on a transparent canvas
                new_img.paste(resized.convert("RGBA"), (offset_x, offset_y))
            else:
                new_img.paste(resized, (offset_x, offset_y), resized if resized.mode == "RGBA" else None)
            return new_img

        elif mode == "fill":
            # Scale to cover target, crop center
            scale = max(target_w / img_w, target_h / img_h)
            new_w, new_h = int(img_w * scale), int(img_h * scale)
            resized = image.resize((new_w, new_h), Image.Resampling.LANCZOS)

            offset_x = (new_w - target_w) // 2
            offset_y = (new_h - target_h) // 2
            return resized.crop((offset_x, offset_y, offset_x + target_w, offset_y + target_h))

        return image

    def save_with_compression(self, image: Image.Image, settings: OutputSettings) -> Tuple[str, Dict[str, Any]]:
        fmt = settings.format.upper()
        if fmt == "JPG": fmt = "JPEG"
        if fmt == "JPEG" and settings.compression == "lossless":
            raise ValueError("JPEG does not support lossless compression")

        # Flatten alpha for JPEG
        if fmt == "JPEG":
            if image.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", image.size, settings.background_color)
                if image.mode == "RGBA":
                    background.paste(image, mask=image.split()[3])
                else:
                    background.paste(image)
                image = background
            elif image.mode != "RGB":
                image = image.convert("RGB")

        # Initial quality based on mode
        quality_map = {"lossless": 100, "balanced": 85, "smallest": 60}
        quality = quality_map.get(settings.compression, 85)

        # If lossless and not PNG/WebP, it's a validation error (handled by UI/API)
        # But we'll just use max quality here.

        best_buf = None
        final_q = quality

        warnings = []
        quality_floor = 40
        # Compression loop for max_kb
        if settings.max_kb:
            low, high = quality_floor, 100
            for _ in range(7): # Binary search for quality
                mid = (low + high) // 2
                buf = io.BytesIO()
                # Use quality only for JPEG/WebP
                save_params = {}
                if fmt in ("JPEG", "WEBP"):
                    save_params["quality"] = mid
                    if fmt == "WEBP" and settings.compression == "lossless":
                        save_params = {"lossless": True}

                image.save(buf, format=fmt, **save_params)
                size = buf.tell()

                if size <= settings.max_kb * 1024:
                    best_buf = buf
                    final_q = mid
                    low = mid + 1
                else:
                    high = mid - 1

            if best_buf:
                buf = best_buf
            else:
                # Keep the smallest allowed candidate and report the unmet target.
                buf = io.BytesIO()
                save_params = {"quality": quality_floor} if fmt in ("JPEG", "WEBP") else {}
                if fmt == "WEBP" and settings.compression == "lossless":
                    save_params = {"lossless": True}
                image.save(buf, format=fmt, **save_params)
                final_q = quality_floor
                warnings.append("SIZE_TARGET_UNMET")
        else:
            buf = io.BytesIO()
            save_params = {"quality": quality} if fmt in ("JPEG", "WEBP") else {}
            if fmt == "WEBP" and settings.compression == "lossless":
                save_params = {"lossless": True}
            image.save(buf, format=fmt, **save_params)
            final_q = quality

        # Save to disk (atomic rename not possible for BytesIO, but we'll save here)
        output_dir = Path(self.output_root)
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / f"output_{uuid.uuid4().hex}.{settings.format.lower()}"
        with tempfile.NamedTemporaryFile(dir=output_dir, prefix=".output_", suffix=".tmp", delete=False) as f:
            temporary_path = Path(f.name)
            f.write(buf.getvalue())
            f.flush()
            os.fsync(f.fileno())
        try:
            temporary_path.rename(path)
        finally:
            temporary_path.unlink(missing_ok=True)

        return str(path), {
            "final_size": buf.tell(),
            "final_quality": final_q,
            "format": fmt,
            "dimensions": image.size,
            "warnings": warnings
        }

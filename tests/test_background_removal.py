import os
import tempfile
import unittest

from PIL import Image
from pydantic import ValidationError

from backend.postprocess.background import BackgroundRemover, BackgroundRemovalError
from backend.postprocess.engine import OutputEngine
from backend.projects.models import OutputSettings


class FakeRemover:
    """Makes the left half opaque red and the right half fully transparent."""

    def __init__(self):
        self.calls = []

    def remove(self, image):
        self.calls.append(image.size)
        out = Image.new("RGBA", image.size, (255, 0, 0, 255))
        w, h = image.size
        out.paste((0, 0, 0, 0), (w // 2, 0, w, h))
        return out


def alpha_extrema(path):
    with Image.open(path) as img:
        img.load()
        return img.mode, img.convert("RGBA").getchannel("A").getextrema()


class BackgroundRemovalTests(unittest.TestCase):
    def run_engine(self, **kwargs):
        remover = FakeRemover()
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        engine = OutputEngine(directory.name, remover)
        settings = OutputSettings(remove_background=True, compression="lossless", **kwargs)
        path, meta = engine.process(Image.new("RGB", (100, 50), "blue"), settings)
        return remover, path, meta

    def test_remover_runs_on_original_size_before_resize(self):
        remover, _, _ = self.run_engine(width=40, height=40, fit_mode="fit", format="png")
        self.assertEqual(remover.calls, [(100, 50)])

    def test_fit_keeps_transparent_padding_and_alpha_png(self):
        _, path, _ = self.run_engine(width=40, height=40, fit_mode="fit", format="png", background_color="#FF0000")
        mode, extrema = alpha_extrema(path)
        self.assertEqual(mode, "RGBA")
        self.assertEqual(extrema, (0, 255))
        with Image.open(path) as img:
            self.assertEqual(img.getpixel((20, 2))[3], 0)  # padding, despite red background_color
            self.assertEqual(img.getpixel((5, 20)), (255, 0, 0, 255))

    def test_fill_keeps_alpha_webp(self):
        _, path, _ = self.run_engine(width=40, height=40, fit_mode="fill", format="webp")
        mode, extrema = alpha_extrema(path)
        self.assertEqual(mode, "RGBA")
        self.assertEqual(extrema[0], 0)

    def test_fit_keeps_alpha_webp(self):
        _, path, _ = self.run_engine(width=40, height=40, fit_mode="fit", format="webp")
        self.assertEqual(alpha_extrema(path)[1], (0, 255))

    def test_jpeg_with_remove_background_is_rejected(self):
        with self.assertRaises(ValueError):
            OutputSettings(remove_background=True, format="jpeg")
        with tempfile.TemporaryDirectory() as directory:
            settings = OutputSettings.model_construct(
                width=32, height=32, fit_mode="fill", format="jpeg", compression="balanced",
                max_kb=None, background_color="#FFFFFF", remove_background=True)
            with self.assertRaises(ValueError):
                OutputEngine(directory, FakeRemover()).process(Image.new("RGB", (32, 32)), settings)

    def test_default_off_does_not_call_remover(self):
        remover = FakeRemover()
        with tempfile.TemporaryDirectory() as directory:
            OutputEngine(directory, remover).process(Image.new("RGB", (32, 32), "red"), OutputSettings(width=32, height=32))
        self.assertEqual(remover.calls, [])

    def test_unconfigured_python_raises_clear_error(self):
        with self.assertRaises(BackgroundRemovalError) as ctx:
            BackgroundRemover({"enabled": True}).remove(Image.new("RGB", (8, 8)))
        self.assertIn("python", str(ctx.exception))
        with self.assertRaises(BackgroundRemovalError):
            BackgroundRemover(None).remove(Image.new("RGB", (8, 8)))

    def test_missing_interpreter_raises(self):
        with self.assertRaises(BackgroundRemovalError):
            BackgroundRemover({"python": "/nonexistent/python"}).remove(Image.new("RGB", (8, 8)))


if __name__ == "__main__":
    unittest.main()

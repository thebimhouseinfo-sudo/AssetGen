import asyncio
import os
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from PIL import Image

from backend.generation.parser import PromptParser
from backend.postprocess.engine import OutputEngine
from backend.projects.models import OutputSettings
from backend.queue.engine import GenerationQueue
from backend.projects.manager import ProjectManager
from backend.projects.models import TextAssetJob
from backend.api import main as api


class RegressionTests(unittest.TestCase):
    def test_worker_accepts_job_after_idle_start(self):
        async def scenario():
            queue = GenerationQueue()
            completed = asyncio.Event()

            async def execute():
                completed.set()

            worker = asyncio.create_task(queue.run())
            await asyncio.sleep(0)
            self.assertTrue(queue.is_running)
            self.assertTrue(queue.enqueue("late-job", execute))
            await asyncio.wait_for(completed.wait(), 1)
            queue.shutdown()
            await asyncio.wait_for(worker, 1)

        asyncio.run(scenario())

    def test_outputs_do_not_overwrite_within_same_second(self):
        with tempfile.TemporaryDirectory() as directory:
            engine = OutputEngine(directory)
            settings = OutputSettings(width=32, height=32, format="webp")
            first, _ = engine.process(Image.new("RGB", (32, 32), "red"), settings)
            second, _ = engine.process(Image.new("RGB", (32, 32), "blue"), settings)
            self.assertNotEqual(first, second)
            self.assertEqual(len(list(Path(directory).glob("*.webp"))), 2)
            with Image.open(first) as image:
                self.assertGreater(image.getpixel((0, 0))[0], image.getpixel((0, 0))[2])

    def test_invalid_batch_values_are_rejected(self):
        parser = PromptParser()
        text = "=== ASSET ===\nname: Same\nratio: 0:abc\nprompt: One\n=== END ==="
        jobs, diagnostics = parser.parse(text)
        self.assertFalse(jobs)
        self.assertIn("INVALID_RATIO", [item["code"] for item in diagnostics])

        duplicate = "=== ASSET ===\nname: Same\nprompt: One\n=== END ===\n=== ASSET ===\nname: Same\nprompt: Two\n=== END ==="
        jobs, diagnostics = parser.parse(duplicate)
        self.assertEqual(len(jobs), 1)
        self.assertIn("DUPLICATE_SLUG", [item["code"] for item in diagnostics])

    def test_jpeg_lossless_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            engine = OutputEngine(directory)
            with self.assertRaises(ValueError):
                engine.process(Image.new("RGB", (32, 32)), OutputSettings(format="jpeg", compression="lossless"))

    def test_impossible_size_limit_reports_warning_without_resizing(self):
        with tempfile.TemporaryDirectory() as directory:
            engine = OutputEngine(directory)
            pixels = os.urandom(128 * 128 * 3)
            image = Image.frombytes("RGB", (128, 128), pixels)
            path, metadata = engine.process(image, OutputSettings(width=128, height=128, format="png", max_kb=1))
            self.assertIn("SIZE_TARGET_UNMET", metadata["warnings"])
            with Image.open(path) as saved:
                self.assertEqual(saved.size, (128, 128))

    def test_batch_publishes_named_image_and_regenerates_it(self):
        class FakeAdapter:
            def generate_text_asset(self, job, output_path):
                color = "blue" if "blue" in job.prompt else "red"
                Image.new("RGB", (64, 64), color).save(output_path)
                return {"seed": job.seed, "path": output_path}

        async def scenario(projects, outputs):
            manager = ProjectManager(projects)
            project = manager.create_project("Test", outputs)
            job = TextAssetJob(name="Math Card 01", prompt="red card", target_width=32, target_height=32)
            manager.save_job(project.id, job)
            queue = GenerationQueue()
            local_settings = {"storage": {"projects_root": projects, "output_root": outputs}}
            with patch.object(api, "pm", manager), patch.object(api, "engine", OutputEngine(outputs)), patch.object(api, "adapter", FakeAdapter()), patch.object(api, "queue", queue), patch.object(api, "settings", local_settings):
                worker = asyncio.create_task(queue.run())
                await asyncio.sleep(0)
                queued = await api.generate_batch(project.id)
                self.assertEqual(queued["count"], 1)
                for _ in range(100):
                    if manager.load_jobs(project.id)[0].status == "COMPLETED":
                        break
                    await asyncio.sleep(0.01)
                saved = manager.load_jobs(project.id)[0]
                self.assertEqual(saved.status, "COMPLETED", saved.error)
                revision_file = Path(projects) / project.id / "revisions" / job.id / f"{saved.selected_revision_id}.json"
                self.assertTrue(revision_file.is_file())
                first_revision = saved.selected_revision_id
                image_folder = Path(outputs) / project.id
                image_file = image_folder / "Math Card 01.webp"
                self.assertTrue(image_file.is_file())
                self.assertEqual([p.name for p in image_folder.iterdir()], [image_file.name])
                with Image.open(image_file) as image:
                    self.assertGreater(image.getpixel((0, 0))[0], image.getpixel((0, 0))[2])

                await api.regenerate_image(project.id, job.id, "blue card")
                for _ in range(100):
                    current = manager.load_jobs(project.id)[0]
                    if current.status == "COMPLETED" and current.selected_revision_id != first_revision:
                        break
                    await asyncio.sleep(0.01)
                current = manager.load_jobs(project.id)[0]
                self.assertEqual(current.status, "COMPLETED", current.error)
                self.assertNotEqual(current.selected_revision_id, first_revision)
                self.assertEqual(current.prompt, "blue card")
                self.assertTrue(revision_file.is_file())
                self.assertEqual([p.name for p in image_folder.iterdir()], [image_file.name])
                with Image.open(image_file) as image:
                    self.assertGreater(image.getpixel((0, 0))[2], image.getpixel((0, 0))[0])
                queue.shutdown()
                await worker

        with tempfile.TemporaryDirectory() as directory:
            projects = str(Path(directory) / "projects")
            outputs = str(Path(directory) / "outputs")
            asyncio.run(scenario(projects, outputs))

    def test_restart_marks_unfinished_job_interrupted(self):
        with tempfile.TemporaryDirectory() as directory:
            manager = ProjectManager(directory)
            project = manager.create_project("Recovery", directory)
            job = TextAssetJob(name="Pending", prompt="test", target_width=32, target_height=32, status="GENERATING")
            manager.save_job(project.id, job)
            with patch.object(api, "pm", manager), patch.object(api, "settings", {"storage": {"projects_root": directory}}):
                api.recover_interrupted_jobs()
            recovered = manager.load_jobs(project.id)[0]
            self.assertEqual(recovered.status, "INTERRUPTED")


if __name__ == "__main__":
    unittest.main()

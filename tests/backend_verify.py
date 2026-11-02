import unittest
import os
import shutil
import json
import tempfile
from PIL import Image
from backend.projects.manager import ProjectManager
from backend.projects.models import Project, TextAssetJob, OutputSettings
from backend.generation.parser import PromptParser
from backend.postprocess.engine import OutputEngine
from backend.queue.engine import GenerationQueue, JobStatus

class TestAssetGenBackend(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_root = os.path.join(self.temp_dir.name, "projects")
        self.test_output = os.path.join(self.temp_dir.name, "outputs")
        os.makedirs(self.test_root)
        os.makedirs(self.test_output)
        self.pm = ProjectManager(self.test_root)
        self.parser = PromptParser()
        self.engine = OutputEngine(self.test_output)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_wp1_project_roundtrip(self):
        # Create project
        proj = self.pm.create_project("Test Project", "out/path")
        proj_id = proj.id

        # Create and save a job
        job = TextAssetJob(name="Job 1", prompt="A test prompt", target_width=512, target_height=512)
        self.pm.save_job(proj_id, job)

        # Reload project
        loaded_proj = self.pm.load_project(proj_id)
        self.assertEqual(loaded_proj.name, "Test Project")

        # Reload jobs
        jobs = self.pm.load_jobs(proj_id)
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].name, "Job 1")
        self.assertEqual(jobs[0].prompt, "A test prompt")

    def test_wp2_output_pipeline(self):
        # Create a dummy image (1000x500)
        img = Image.new("RGB", (1000, 500), color="red")

        # Test Fill (Cover) -> Result should be target_w x target_h
        settings_fill = OutputSettings(width=512, height=512, fit_mode="fill", format="webp")
        path_fill, meta_fill = self.engine.process(img, settings_fill)
        self.assertTrue(os.path.exists(path_fill))
        self.assertEqual(meta_fill["dimensions"], (512, 512))

        # Test Fit (Pad) -> Result should be target_w x target_h
        settings_fit = OutputSettings(width=512, height=512, fit_mode="fit", format="webp")
        path_fit, meta_fit = self.engine.process(img, settings_fit)
        self.assertTrue(os.path.exists(path_fit))
        self.assertEqual(meta_fit["dimensions"], (512, 512))

        # Test max_kb constraint
        settings_kb = OutputSettings(width=512, height=512, format="jpeg", max_kb=10)
        path_kb, meta_kb = self.engine.process(img, settings_kb)
        # Check if size is close to 10KB (or at least not huge)
        self.assertLessEqual(meta_kb["final_size"], 15 * 1024) # Allow some buffer

    def test_wp3_parser_diagnostics(self):
        # Case 1: Valid multiline
        text_valid = "=== ASSET ===\nname: Test\nprompt: Line 1\nLine 2\n=== END ==="
        jobs, diag = self.parser.parse(text_valid)
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].prompt, "Line 1\nLine 2")

        # Case 2: Missing name
        text_invalid = "=== ASSET ===\nprompt: Hello\n=== END ==="
        jobs, diag = self.parser.parse(text_invalid)
        self.assertEqual(len(jobs), 0)
        self.assertTrue(any(d["code"] == "MISSING_NAME" for d in diag))

        # Case 3: Unclosed block
        text_unclosed = "=== ASSET ===\nname: Test\nprompt: Hello"
        jobs, diag = self.parser.parse(text_unclosed)
        self.assertTrue(any(d["code"] == "UNCLOSED_BLOCK" for d in diag))

    def test_wp4_queue_transitions(self):
        queue = GenerationQueue()

        async def mock_exec():
            import asyncio
            await asyncio.sleep(0.1)

        job_id = "job_1"
        queue.enqueue(job_id, mock_exec)

        # Check initial state
        self.assertEqual(len(queue.queue), 1)
        self.assertEqual(queue.queue[0].status, JobStatus.QUEUED)

        # Run queue until the job completes, then shut down the worker.
        import asyncio
        async def run_and_stop():
            worker = asyncio.create_task(queue.run())
            while queue.queue or queue.active_job:
                await asyncio.sleep(0.01)
            queue.shutdown()
            await worker
        asyncio.run(run_and_stop())

        self.assertEqual(len(queue.queue), 0)
        self.assertFalse(queue.is_running)

if __name__ == "__main__":
    unittest.main()

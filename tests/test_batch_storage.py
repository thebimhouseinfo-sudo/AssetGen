import unittest
import tempfile
from backend.projects.manager import ProjectManager
from backend.projects.models import Project

class TestBatchStorage(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.pm = ProjectManager(self.temp.name)

    def test_batch_data_readable(self):
        # Create a project with some batch jobs
        project = Project(name="Batch Project", output_root="out")
        self.pm.save_project(project)

        from backend.projects.models import TextAssetJob
        job = TextAssetJob(name="Batch Job", prompt="Hello", target_width=512, target_height=512)
        self.pm.save_job(project.id, job)

        # Verify we can still load jobs
        jobs = self.pm.load_jobs(project.id)
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0].name, "Batch Job")


if __name__ == "__main__":
    unittest.main()

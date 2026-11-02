import unittest
from fastapi.testclient import TestClient
from backend.api.main import app
from backend.projects.manager import ProjectManager
import shutil
from pathlib import Path

class APISmokeTest(unittest.TestCase):
    def setUp(self):
        self.test_root = Path("test_smoke_projects")
        self.test_root.mkdir(exist_ok=True)
        import backend.api.main as main
        main.settings["storage"]["projects_root"] = str(self.test_root)
        main.pm = ProjectManager(str(self.test_root))
        self.client = TestClient(app)

    def tearDown(self):
        if self.test_root.exists():
            shutil.rmtree(self.test_root)

    def test_project_creation(self):
        res = self.client.post("/projects", data={"name": "Smoke Project"})
        self.assertEqual(res.status_code, 200)
        self.assertIn("id", res.json())

    def test_batch_workflow(self):
        import backend.api.main as main
        project = main.pm.create_project("Smoke", "out")
        pid = project.id

        prompt_content = (
            "=== ASSET ===\n"
            "name: Apple\n"
            "prompt: a red apple\n"
            "ratio: 1:1\n"
            "=== END ===\n"
        ).encode("utf-8")

        res = self.client.post("/batch/upload", files={"file": ("prompts.txt", prompt_content, "text/plain")})
        if res.status_code != 200:
            print(f"\nDEBUG: Upload failed: {res.status_code} {res.text}")
        self.assertEqual(res.status_code, 200)

        jobs = res.json()["jobs"]
        res = self.client.post(f"/projects/{pid}/batch/jobs", json=jobs)
        self.assertEqual(res.status_code, 200)

        res = self.client.get(f"/batch/status?project_id={pid}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()["jobs"]), 1)

if __name__ == "__main__":
    unittest.main()

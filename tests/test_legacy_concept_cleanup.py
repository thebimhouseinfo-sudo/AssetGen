import json
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from backend.api import main as api
from backend.projects.manager import ProjectManager
from backend.projects.models import TextAssetJob


class LegacyConceptCleanupTests(unittest.TestCase):
    def test_retired_concept_routes_are_unavailable(self):
        client = TestClient(api.app)
        self.assertEqual(client.post('/concept/generate').status_code, 404)
        self.assertEqual(client.get('/projects/00000000-0000-0000-0000-000000000000/concept').status_code, 404)

    def test_batch_save_does_not_overwrite_legacy_job_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            manager = ProjectManager(tmp)
            project = manager.create_project('Mixed', tmp)
            legacy_id = str(uuid.uuid4())
            legacy_path = Path(tmp) / project.id / 'jobs' / (legacy_id + '.json')
            legacy_path.parent.mkdir(parents=True)
            legacy_path.write_text(json.dumps({'id': legacy_id, 'source_image': 'old.png', 'frames': []}), encoding='utf-8')
            before = legacy_path.read_bytes()
            settings = {'storage': {'projects_root': tmp, 'output_root': tmp}}
            with patch.object(api, 'pm', manager), patch.object(api, 'settings', settings):
                response = TestClient(api.app).post(f'/projects/{project.id}/batch/jobs', json=[{
                    'id': legacy_id, 'name': 'Batch', 'prompt': 'test', 'ratio': '1:1',
                    'target_width': 32, 'target_height': 32,
                }])
            self.assertEqual(response.status_code, 422)
            self.assertEqual(legacy_path.read_bytes(), before)

    def test_recovery_preserves_legacy_concept_job_and_keeps_batch_readable(self):
        with tempfile.TemporaryDirectory() as tmp:
            manager = ProjectManager(tmp)
            project = manager.create_project('Mixed legacy project', tmp)
            batch = TextAssetJob(name='Batch', prompt='test', target_width=32, target_height=32, status='QUEUED')
            manager.save_job(project.id, batch)
            legacy_path = Path(tmp) / project.id / 'jobs' / 'legacy.json'
            legacy = {'id': 'legacy', 'name': 'Old concept', 'status': 'QUEUED', 'target_width': 32, 'target_height': 32, 'source_image': 'source.png', 'frames': []}
            legacy_path.write_text(json.dumps(legacy), encoding='utf-8')
            before = legacy_path.read_bytes()
            with patch.object(api, 'pm', manager), patch.object(api, 'settings', {'storage': {'projects_root': tmp, 'output_root': tmp}}):
                api.recover_interrupted_jobs()
                jobs = manager.load_jobs(project.id)
                self.assertEqual([job.name for job in jobs], ['Batch'])
                self.assertEqual(jobs[0].status, 'INTERRUPTED')
            self.assertEqual(legacy_path.read_bytes(), before)

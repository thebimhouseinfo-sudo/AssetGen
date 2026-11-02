import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import FastAPI

from backend.api import runtime
from backend.config import SETTINGS_ENV_VAR, load_settings


class RuntimeConfigTests(unittest.TestCase):
    def test_settings_path_can_be_overridden_for_isolated_runs(self):
        with tempfile.TemporaryDirectory() as directory:
            settings_path = Path(directory) / "settings.json"
            expected = {"storage": {"projects_root": "copy/projects"}}
            settings_path.write_text(json.dumps(expected), encoding="utf-8")

            with patch.dict(os.environ, {SETTINGS_ENV_VAR: str(settings_path)}):
                self.assertEqual(load_settings(), expected)

    def test_server_binds_to_loopback(self):
        application = FastAPI()
        with patch("uvicorn.run") as uvicorn_run:
            runtime.run(application)

        uvicorn_run.assert_called_once_with(application, host="127.0.0.1", port=8001)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Portable regression tests; uses only temporary configuration and Python child fixtures."""
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("verify_module", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)

class VerifyTests(unittest.TestCase):
    def run_config(self, payload):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "checks.json"
            p.write_text(payload, encoding="utf-8")
            return verify.main(p)
    def test_invalid_roots(self):
        for obj in ([], None, "bad", 42, False):
            with self.subTest(obj=obj):
                self.assertEqual(self.run_config(json.dumps(obj)), 2)
    def test_invalid_checks(self):
        for obj in ({"checks":[]}, {"checks":"bad"}, {"checks":[3]},
                    {"checks":[{"name":"x","argv":"echo"}]},
                    {"checks":[{"name":"x","argv":["echo"],"timeout_seconds":True}]},
                    {"checks":[{"name":"x","argv":["echo"],"timeout_seconds":"5"}]},
                    {"checks":[{"name":"x","argv":["echo"],"timeout_seconds":float("inf")}]},
                    {"checks":[{"name":"x","argv":["echo"],"timeout_seconds":-1}]},
                    {"checks":[{"name":"x","argv":["echo"]},{"name":"x","argv":["echo"]}]}):
            with self.subTest(obj=obj):
                self.assertEqual(self.run_config(json.dumps(obj)),2)
    def test_invalid_json_and_missing(self):
        self.assertEqual(self.run_config("{broken"),2)
        self.assertEqual(verify.main(pathlib.Path("/no-such-checks-file-234561.json")),2)
    def test_pass_failure_stop_and_timeout(self):
        py = sys.executable
        ok = {"name":"ok","argv":[py,"-c","print('ok')"]}
        fail = {"name":"fail","argv":[py,"-c","import sys;sys.exit(7)"]}
        timeout = {"name":"timeout","argv":[py,"-c","import time;time.sleep(10)"],"timeout_seconds":0.1}
        self.assertEqual(self.run_config(json.dumps({"checks":[ok]})),0)
        self.assertEqual(self.run_config(json.dumps({"checks":[fail]})),1)
        self.assertEqual(self.run_config(json.dumps({"checks":[timeout]})),1)
        with tempfile.TemporaryDirectory() as d:
            marker = pathlib.Path(d)/"bad"
            trailing = {"name":"must-not-run","argv":[py,"-c",f"from pathlib import Path;Path({str(marker)!r}).touch()"]}
            self.assertEqual(self.run_config(json.dumps({"checks":[fail,trailing]})),1)
            self.assertFalse(marker.exists())

if __name__=="__main__":
    unittest.main(verbosity=2)

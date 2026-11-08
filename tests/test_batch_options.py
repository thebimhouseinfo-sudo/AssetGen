import unittest

from backend.generation.parser import PromptParser


def block(*lines):
    return "=== ASSET ===\nname: a\nratio: 1:1\n" + "\n".join(lines) + "\nprompt: red card\n=== END ==="


class BatchOptionTests(unittest.TestCase):
    def parse(self, *lines):
        return PromptParser().parse(block(*lines))

    def test_valid_keys_reach_job_fields(self):
        jobs, diagnostics = self.parse("width: 256", "height: 128", "max_kb: 50", "format: PNG",
                                       "compression: Smallest", "fit: fit", "remove_background: TRUE")
        self.assertEqual(diagnostics, [])
        job = jobs[0]
        self.assertEqual((job.target_width, job.target_height, job.max_kb), (256, 128, 50))
        self.assertEqual((job.output_format, job.compression_mode, job.fit_mode), ("png", "smallest", "fit"))
        self.assertTrue(job.remove_background)

    def test_missing_keys_keep_defaults(self):
        jobs, diagnostics = self.parse()
        self.assertEqual(diagnostics, [])
        job = jobs[0]
        self.assertEqual((job.target_width, job.target_height), (512, 512))
        self.assertEqual((job.output_format, job.compression_mode, job.fit_mode), ("webp", "balanced", "fill"))
        self.assertIsNone(job.max_kb)
        self.assertFalse(job.remove_background)
        self.assertEqual(job.model_fields_set & {"output_format", "max_kb", "remove_background"}, set())

    def assert_error(self, code, field, *lines):
        jobs, diagnostics = self.parse(*lines)
        self.assertFalse(jobs)
        match = [d for d in diagnostics if d["code"] == code]
        self.assertTrue(match, diagnostics)
        self.assertEqual(match[0]["field"], field)
        self.assertEqual(match[0]["asset"], "a")
        self.assertIsInstance(match[0]["line"], int)

    def test_bad_values_report_diagnostics(self):
        self.assert_error("INVALID_WIDTH", "width", "width: 0", "height: 10")
        self.assert_error("INVALID_HEIGHT", "height", "width: 10", "height: abc")
        self.assert_error("INVALID_MAX_KB", "max_kb", "max_kb: -5")
        self.assert_error("INVALID_FORMAT", "format", "format: gif")
        self.assert_error("INVALID_COMPRESSION", "compression", "compression: fast")
        self.assert_error("INVALID_FIT", "fit", "fit: stretch")
        self.assert_error("INVALID_REMOVE_BACKGROUND", "remove_background", "remove_background: yes")
        self.assert_error("INCOMPLETE_SIZE", "height", "width: 10")

    def test_duplicate_key_reports_diagnostic(self):
        self.assert_error("DUPLICATE_KEY", "format", "format: png", "format: webp")

    def test_jpeg_with_remove_background_is_error(self):
        self.assert_error("JPEG_REMOVE_BACKGROUND", "remove_background", "format: jpeg", "remove_background: true")

    def test_jpeg_lossless_reports_diagnostic_not_exception(self):
        jobs, diagnostics = self.parse("format: jpeg", "compression: lossless")
        self.assertFalse(jobs)
        self.assertIn("INVALID_OPTIONS", [d["code"] for d in diagnostics])

    def test_unknown_key_still_reported(self):
        jobs, diagnostics = self.parse("colour: red")
        self.assertFalse(jobs)
        self.assertIn("UNKNOWN_KEY", [d["code"] for d in diagnostics])

    def test_option_like_line_inside_prompt_stays_prompt_text(self):
        text = "=== ASSET ===\nname: a\nratio: 1:1\nprompt: red card\nwidth: 3 cm border\n=== END ==="
        jobs, diagnostics = PromptParser().parse(text)
        self.assertEqual(diagnostics, [])
        self.assertIn("width: 3 cm border", jobs[0].prompt)
        self.assertEqual(jobs[0].target_width, 512)


if __name__ == "__main__":
    unittest.main()

import os
import unittest

import yaml


class TestWorkflowScaffold(unittest.TestCase):
    WORKFLOW_PATH = ".github/workflows/ci.yml"

    def setUp(self):
        self.workflow_path = os.path.join(os.getcwd(), self.WORKFLOW_PATH)
        self.workflow_data = None
        if os.path.exists(self.workflow_path):
            with open(self.workflow_path, "r", encoding="utf-8") as f:
                self.workflow_data = yaml.load(f, Loader=yaml.BaseLoader)

    def test_workflow_exists(self):
        self.assertTrue(os.path.exists(self.workflow_path), "missing .github/workflows/ci.yml")

    def test_triggers_push_and_pull_request(self):
        self.assertIsNotNone(self.workflow_data, "workflow yaml missing/invalid")
        triggers = self.workflow_data.get("on")
        self.assertIsInstance(triggers, dict)
        self.assertIn("push", triggers)
        self.assertIn("pull_request", triggers)

    def test_paths_filter_job_present(self):
        self.assertIsNotNone(self.workflow_data, "workflow yaml missing/invalid")
        jobs = self.workflow_data.get("jobs", {})
        self.assertIn("changes", jobs)
        changes_job = jobs["changes"]
        steps = changes_job.get("steps", [])
        has_paths_filter = any("paths-filter" in str(step.get("uses", "")) for step in steps)
        self.assertTrue(has_paths_filter, "changes job missing dorny/paths-filter")

    def test_lint_test_build_jobs_present(self):
        self.assertIsNotNone(self.workflow_data, "workflow yaml missing/invalid")
        jobs = self.workflow_data.get("jobs", {})
        self.assertIn("lint", jobs)
        self.assertIn("test", jobs)
        self.assertIn("build", jobs)

    def test_workflow_lints_with_actionlint(self):
        self.assertIsNotNone(self.workflow_data, "workflow yaml missing/invalid")
        jobs = self.workflow_data.get("jobs", {})
        lint_job = jobs.get("lint", {})
        steps = lint_job.get("steps", [])
        has_actionlint = any("actionlint" in str(step.get("name", "")).lower() or "actionlint" in str(step.get("run", "")).lower() for step in steps)
        self.assertTrue(has_actionlint, "lint job missing actionlint step")


if __name__ == "__main__":
    unittest.main()

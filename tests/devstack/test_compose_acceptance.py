import os
import unittest

import yaml


class TestComposeAcceptance(unittest.TestCase):
    """Acceptance tests for Task 0.4: Local Dev Compose."""

    def setUp(self):
        root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.compose_path = os.path.join(root, "docker-compose.yml")
        self.makefile_path = os.path.join(root, "Makefile")
        with open(self.compose_path, "r", encoding="utf-8") as f:
            self.compose_data = yaml.safe_load(f)

    def test_required_services_exist(self):
        required_services = ["db", "db-init", "mlb-mock", "api", "ingest", "web"]
        for service in required_services:
            self.assertIn(service, self.compose_data.get("services", {}))

    def test_db_port_mapping(self):
        services = self.compose_data.get("services", {})
        ports = services.get("db", {}).get("ports", [])
        found = any(
            (isinstance(port, str) and port.startswith("5432:"))
            or (isinstance(port, dict) and port.get("published") == 5432)
            for port in ports
        )
        self.assertTrue(found, "DB service must expose host port 5432")

    def test_mlb_mock_port_mapping(self):
        services = self.compose_data.get("services", {})
        ports = services.get("mlb-mock", {}).get("ports", [])
        found = any(
            (isinstance(port, str) and port.startswith("8090:"))
            or (isinstance(port, dict) and port.get("published") == 8090)
            for port in ports
        )
        self.assertTrue(found, "MLB-Mock service must expose host port 8090")

    def test_web_port_mapping(self):
        services = self.compose_data.get("services", {})
        ports = services.get("web", {}).get("ports", [])
        found = any(
            (isinstance(port, str) and port.startswith("5173:"))
            or (isinstance(port, dict) and port.get("published") == 5173)
            for port in ports
        )
        self.assertTrue(found, "Web service must expose host port 5173")

    def test_db_image(self):
        image = self.compose_data.get("services", {}).get("db", {}).get("image", "")
        self.assertEqual(image, "postgres:18-alpine")

    def test_makefile_targets(self):
        with open(self.makefile_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("dev:", content)
        self.assertIn("dev-clean:", content)


if __name__ == "__main__":
    unittest.main()

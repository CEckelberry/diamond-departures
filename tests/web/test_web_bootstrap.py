import os
import unittest


class TestWebBootstrap(unittest.TestCase):
    def setUp(self):
        self.root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.web_root = os.path.join(self.root, "apps", "web")

    def _read(self, rel_path: str) -> str:
        path = os.path.join(self.web_root, rel_path)
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def test_package_json_has_sveltekit_and_tailwind(self):
        path = os.path.join(self.web_root, "package.json")
        self.assertTrue(os.path.exists(path), "apps/web/package.json missing")
        content = self._read("package.json").lower()
        self.assertIn("@sveltejs/kit", content)
        self.assertIn("tailwindcss", content)

    def test_app_css_has_diamond_tokens(self):
        path = os.path.join(self.web_root, "src", "app.css")
        self.assertTrue(os.path.exists(path), "apps/web/src/app.css missing")
        content = self._read("src/app.css")
        self.assertIn("--board-bg", content)
        self.assertIn("--cell-bg", content)
        self.assertIn("--cell-text", content)

    def test_page_has_placeholder_split_flap_cell(self):
        path = os.path.join(self.web_root, "src", "routes", "+page.svelte")
        self.assertTrue(os.path.exists(path), "apps/web/src/routes/+page.svelte missing")
        content = self._read("src/routes/+page.svelte").lower()
        self.assertIn("split-flap", content)
        self.assertIn("flap-cell", content)

    def test_layout_has_dark_light_toggle_hook(self):
        path = os.path.join(self.web_root, "src", "routes", "+layout.svelte")
        self.assertTrue(os.path.exists(path), "apps/web/src/routes/+layout.svelte missing")
        content = self._read("src/routes/+layout.svelte").lower()
        self.assertIn("toggle", content)
        self.assertIn("theme", content)

    def test_fontsource_imports_present(self):
        content = self._read("src/app.css").lower()
        self.assertIn("@fontsource/inter", content)
        self.assertIn("@fontsource/instrument-serif", content)
        self.assertIn("@fontsource/jetbrains-mono", content)


if __name__ == "__main__":
    unittest.main()

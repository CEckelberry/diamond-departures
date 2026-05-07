import inspect
import unittest

from .. import basic
from .. import woba as woba_module
from .. import wrc as wrc_module


class TestDocstrings(unittest.TestCase):
    def test_all_public_hitting_functions_have_docstrings(self):
        modules = (basic, woba_module, wrc_module)
        for module in modules:
            for name, fn in inspect.getmembers(module, inspect.isfunction):
                if name.startswith("_"):
                    continue
                self.assertIsNotNone(fn.__doc__, f"{module.__name__}.{name} missing docstring")
                self.assertTrue(fn.__doc__.strip(), f"{module.__name__}.{name} empty docstring")


if __name__ == "__main__":
    unittest.main()

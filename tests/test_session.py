"""
Unit tests for Session and Configuration persistence.
"""
import os
import unittest
from npp_linux.core.session import save_config, load_config, save_session, load_session


class TestSession(unittest.TestCase):

    def test_config_save_load(self):
        cfg = load_config()
        cfg["theme"] = "Monokai"
        cfg["dark_mode"] = True
        save_config(cfg)

        loaded = load_config()
        self.assertEqual(loaded["theme"], "Monokai")
        self.assertTrue(loaded["dark_mode"])


if __name__ == "__main__":
    unittest.main()

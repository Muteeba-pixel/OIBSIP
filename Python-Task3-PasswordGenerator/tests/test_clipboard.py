"""Unit tests for the resilient clipboard manager."""

import os
import sys
import unittest
import tkinter as tk

sys.path.insert(0, os.path.abspath("."))
from securepass.ui.clipboard import ClipboardManager


class TestClipboardManager(unittest.TestCase):
    """Test clipboard copy reliability and success callbacks."""

    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.update_idletasks()

    @classmethod
    def tearDownClass(cls):
        try:
            cls.root.destroy()
        except Exception:
            pass

    def test_copy_empty_text_returns_false(self):
        result = ClipboardManager.copy_text(self.root, "")
        self.assertFalse(result)

    def test_copy_valid_text_succeeds_and_triggers_callback(self):
        callback_called = False

        def on_success():
            nonlocal callback_called
            callback_called = True

        result = ClipboardManager.copy_text(self.root, "SecurePass_Secret_Token_42", on_success)
        self.assertTrue(result)
        self.assertTrue(callback_called)


if __name__ == "__main__":
    unittest.main()

"""Unit tests for the volatile in-memory session history manager."""

import unittest
from securepass.core.session import SessionHistory


class TestSessionHistory(unittest.TestCase):
    """Test volatile session storage, masking, FIFO bounds, and zero-persistence."""

    def test_add_and_retrieve_entries(self):
        session = SessionHistory(max_entries=5)
        self.assertEqual(session.count, 0)

        entry1 = session.add("Password123!", "STRONG")
        self.assertEqual(session.count, 1)
        self.assertEqual(entry1.password, "Password123!")
        self.assertEqual(entry1.masked_preview, "••••••••••••")
        self.assertEqual(entry1.strength_label, "STRONG")
        self.assertEqual(entry1.length, 12)

        entry2 = session.add("AnotherSecret456#", "VERY STRONG")
        self.assertEqual(session.count, 2)

        entries = session.get_entries()
        # Newest should be first
        self.assertEqual(entries[0].password, "AnotherSecret456#")
        self.assertEqual(entries[1].password, "Password123!")

    def test_fifo_capacity_bound(self):
        session = SessionHistory(max_entries=3)
        for i in range(5):
            session.add(f"Pass_{i}", "STRONG")

        self.assertEqual(session.count, 3)
        entries = session.get_entries()
        # Should have entries for i = 4, 3, 2
        self.assertEqual(entries[0].password, "Pass_4")
        self.assertEqual(entries[1].password, "Pass_3")
        self.assertEqual(entries[2].password, "Pass_2")

    def test_clear_history(self):
        session = SessionHistory()
        session.add("TestPass1", "STRONG")
        session.add("TestPass2", "STRONG")
        self.assertEqual(session.count, 2)

        session.clear()
        self.assertEqual(session.count, 0)
        self.assertEqual(len(session.get_entries()), 0)


if __name__ == "__main__":
    unittest.main()

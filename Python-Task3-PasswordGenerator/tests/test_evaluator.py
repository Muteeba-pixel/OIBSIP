"""Unit tests for the password strength and entropy evaluator."""

import unittest
from securepass.core.evaluator import PasswordEvaluator
from securepass.core.models import StrengthLevel


class TestPasswordEvaluator(unittest.TestCase):
    """Test entropy metrics, pattern penalties, and categorical classification."""

    def test_empty_password(self):
        result = PasswordEvaluator.evaluate("")
        self.assertEqual(result.score, 1)
        self.assertEqual(result.level, StrengthLevel.WEAK)
        self.assertEqual(result.entropy_bits, 0.0)

    def test_short_password_is_weak(self):
        result = PasswordEvaluator.evaluate("Ab1!")
        self.assertEqual(result.score, 1)
        self.assertEqual(result.level, StrengthLevel.WEAK)
        self.assertIn("short", result.feedback.lower())

    def test_repeated_characters_penalized(self):
        result_repeated = PasswordEvaluator.evaluate("aaaaaaaaaaaa")
        self.assertEqual(result_repeated.score, 1)
        self.assertEqual(result_repeated.level, StrengthLevel.WEAK)

    def test_sequential_characters_penalized(self):
        result_seq = PasswordEvaluator.evaluate("abcdef123456")
        # Due to sequential characters and lack of symbols/uppercase, should be low score
        self.assertIn(result_seq.score, [1, 2])

    def test_moderate_password(self):
        # 9 chars, mixed alphanumeric
        result = PasswordEvaluator.evaluate("K9mP2vX7q")
        self.assertIn(result.level, [StrengthLevel.MODERATE, StrengthLevel.STRONG])
        self.assertGreaterEqual(result.entropy_bits, 30.0)

    def test_very_strong_password(self):
        # 24 chars, complex diversity
        result = PasswordEvaluator.evaluate("K9#mP2$vX7@qL4*wZ1^yN8!b")
        self.assertEqual(result.score, 4)
        self.assertEqual(result.level, StrengthLevel.VERY_STRONG)
        self.assertEqual(result.label, "VERY STRONG")
        self.assertGreaterEqual(result.entropy_bits, 75.0)
        self.assertEqual(result.color_hex, PasswordEvaluator.COLOR_VERY_STRONG)
        self.assertIn("brute-force", result.feedback.lower())

    def test_entropy_is_positive_and_rounded(self):
        result = PasswordEvaluator.evaluate("SecretP@ssw0rd!2026")
        self.assertEqual(result.entropy_bits, round(result.entropy_bits, 1))

    def test_composition_stats(self):
        result = PasswordEvaluator.evaluate("Ab1!")
        self.assertIsNotNone(result.composition)
        self.assertEqual(result.composition.uppercase_count, 1)
        self.assertEqual(result.composition.lowercase_count, 1)
        self.assertEqual(result.composition.digits_count, 1)
        self.assertEqual(result.composition.symbols_count, 1)
        self.assertEqual(result.composition.total_length, 4)
        self.assertEqual(result.composition.diversity_count, 4)


if __name__ == "__main__":
    unittest.main()

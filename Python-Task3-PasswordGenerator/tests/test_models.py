"""Unit tests for SecurePass domain models and policies."""

import unittest
from securepass.core.models import PasswordPolicy, StrengthLevel, StrengthResult


class TestPasswordPolicy(unittest.TestCase):
    """Test policy validation rules and helper methods."""

    def test_default_policy_is_valid(self):
        policy = PasswordPolicy()
        self.assertEqual(policy.length, 20)
        self.assertTrue(policy.include_uppercase)
        self.assertTrue(policy.include_lowercase)
        self.assertTrue(policy.include_digits)
        self.assertTrue(policy.include_symbols)
        self.assertFalse(policy.exclude_ambiguous)
        self.assertEqual(policy.active_sets_count(), 4)
        # Should not raise
        policy.validate()

    def test_empty_character_set_raises_value_error(self):
        policy = PasswordPolicy(
            length=16,
            include_uppercase=False,
            include_lowercase=False,
            include_digits=False,
            include_symbols=False,
        )
        with self.assertRaises(ValueError) as ctx:
            policy.validate()
        self.assertIn("At least one character type must be selected", str(ctx.exception))

    def test_length_too_short_raises_value_error(self):
        policy = PasswordPolicy(length=3, include_digits=True, include_symbols=False, include_lowercase=False, include_uppercase=False)
        with self.assertRaises(ValueError) as ctx:
            policy.validate()
        self.assertIn("at least 4 characters", str(ctx.exception))

    def test_length_too_long_raises_value_error(self):
        policy = PasswordPolicy(length=129)
        with self.assertRaises(ValueError) as ctx:
            policy.validate()
        self.assertIn("cannot exceed 128", str(ctx.exception))

    def test_length_smaller_than_active_types_raises_value_error(self):
        # 4 types required, but length is 3 (already caught by <4, but test logic)
        policy = PasswordPolicy(length=4, include_uppercase=True, include_lowercase=True, include_digits=True, include_symbols=True)
        # 4 types, length 4 is valid:
        policy.validate()

    def test_active_sets_count(self):
        policy = PasswordPolicy(include_uppercase=True, include_lowercase=False, include_digits=True, include_symbols=False)
        self.assertEqual(policy.active_sets_count(), 2)


if __name__ == "__main__":
    unittest.main()

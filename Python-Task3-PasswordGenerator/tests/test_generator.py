"""Unit tests for the cryptographically secure password generator."""

import unittest
from securepass.core.generator import PasswordGenerator
from securepass.core.models import PasswordPolicy


class TestPasswordGenerator(unittest.TestCase):
    """Test CSPRNG password generation, constraint adherence, and ambiguous filtering."""

    def setUp(self):
        self.generator = PasswordGenerator()

    def test_default_generation(self):
        password = self.generator.generate()
        self.assertEqual(len(password), 20)
        # Verify diversity
        self.assertTrue(any(c.isupper() for c in password))
        self.assertTrue(any(c.islower() for c in password))
        self.assertTrue(any(c.isdigit() for c in password))
        self.assertTrue(any(not c.isalnum() for c in password))

    def test_guaranteed_composition(self):
        """Verify that every enabled character set has at least one character in the result."""
        policy = PasswordPolicy(
            length=8,
            include_uppercase=True,
            include_lowercase=True,
            include_digits=True,
            include_symbols=True,
        )
        for _ in range(50):
            pwd = self.generator.generate(policy)
            self.assertEqual(len(pwd), 8)
            self.assertTrue(any(c.isupper() for c in pwd), "Missing uppercase in guaranteed output")
            self.assertTrue(any(c.islower() for c in pwd), "Missing lowercase in guaranteed output")
            self.assertTrue(any(c.isdigit() for c in pwd), "Missing digit in guaranteed output")
            self.assertTrue(any(not c.isalnum() for c in pwd), "Missing symbol in guaranteed output")

    def test_ambiguous_character_exclusion(self):
        """Verify that when exclude_ambiguous is True, no ambiguous characters appear."""
        policy = PasswordPolicy(
            length=32,
            include_uppercase=True,
            include_lowercase=True,
            include_digits=True,
            include_symbols=True,
            exclude_ambiguous=True,
        )
        ambiguous_set = PasswordGenerator.AMBIGUOUS_CHARS

        for _ in range(100):
            pwd = self.generator.generate(policy)
            found_ambiguous = [c for c in pwd if c in ambiguous_set]
            self.assertEqual(
                len(found_ambiguous), 0,
                f"Found forbidden ambiguous characters {found_ambiguous} in password {pwd}"
            )

    def test_digits_only_policy(self):
        policy = PasswordPolicy(
            length=12,
            include_uppercase=False,
            include_lowercase=False,
            include_digits=True,
            include_symbols=False,
        )
        for _ in range(20):
            pwd = self.generator.generate(policy)
            self.assertEqual(len(pwd), 12)
            self.assertTrue(pwd.isdigit())

    def test_letters_only_policy(self):
        policy = PasswordPolicy(
            length=16,
            include_uppercase=True,
            include_lowercase=True,
            include_digits=False,
            include_symbols=False,
        )
        for _ in range(20):
            pwd = self.generator.generate(policy)
            self.assertEqual(len(pwd), 16)
            self.assertTrue(pwd.isalpha())

    def test_boundary_lengths(self):
        for length in [4, 8, 16, 32, 64, 128]:
            policy = PasswordPolicy(length=length)
            pwd = self.generator.generate(policy)
            self.assertEqual(len(pwd), length)

    def test_invalid_policy_raises(self):
        invalid_policy = PasswordPolicy(
            length=10,
            include_uppercase=False,
            include_lowercase=False,
            include_digits=False,
            include_symbols=False,
        )
        with self.assertRaises(ValueError):
            self.generator.generate(invalid_policy)

    def test_uniqueness_and_csprng_entropy(self):
        """100 consecutively generated passwords must all be distinct."""
        generated = {self.generator.generate() for _ in range(100)}
        self.assertEqual(len(generated), 100, "CSPRNG collision observed in 100 generations")

    def test_avoid_repeats(self):
        """Verify that when avoid_repeats is True, adjacent identical characters are avoided."""
        policy = PasswordPolicy(
            length=30,
            include_uppercase=True,
            include_lowercase=True,
            include_digits=True,
            include_symbols=True,
            avoid_repeats=True,
        )
        for _ in range(30):
            pwd = self.generator.generate(policy)
            for i in range(1, len(pwd)):
                self.assertNotEqual(pwd[i], pwd[i - 1], f"Found adjacent repeat in {pwd}")

    def test_avoid_sequences(self):
        """Verify that when avoid_sequences is True, 3-char runs are minimized."""
        policy = PasswordPolicy(
            length=30,
            include_uppercase=True,
            include_lowercase=True,
            include_digits=True,
            include_symbols=True,
            avoid_sequences=True,
        )
        for _ in range(30):
            pwd = self.generator.generate(policy)
            for i in range(len(pwd) - 2):
                c1, c2, c3 = ord(pwd[i]), ord(pwd[i + 1]), ord(pwd[i + 2])
                is_run = (c2 == c1 + 1 and c3 == c2 + 1) or (c2 == c1 - 1 and c3 == c2 - 1)
                self.assertFalse(is_run, f"Found 3-char run in {pwd} at index {i}")


if __name__ == "__main__":
    unittest.main()

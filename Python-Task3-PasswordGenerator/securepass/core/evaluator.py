"""Password Strength and Information Entropy Evaluation Service.

Evaluates passwords based on Information Theory (Shannon entropy, pool size metrics)
and heuristic structural analysis aligned with NIST SP 800-63B and OWASP guidelines.
"""

import math
from collections import Counter
from typing import Set

from securepass.core.models import CompositionStats, StrengthLevel, StrengthResult


class PasswordEvaluator:
    """Evaluates password complexity, information entropy, and security strength."""

    # UI Theme status colors
    COLOR_VERY_STRONG: str = "#22C55E"  # Emerald/Green
    COLOR_STRONG: str = "#3B82F6"       # Royal Blue
    COLOR_MODERATE: str = "#F59E0B"     # Amber
    COLOR_WEAK: str = "#EF4444"         # Crimson

    @classmethod
    def evaluate(cls, password: str) -> StrengthResult:
        """Analyze password strength, calculate entropy bits, and return a StrengthResult.
        
        Args:
            password: The plaintext password string to evaluate.
            
        Returns:
            StrengthResult with score (1-4), level, entropy, feedback, UI color, and composition stats.
        """
        if not password:
            return StrengthResult(
                score=1,
                level=StrengthLevel.WEAK,
                label="WEAK",
                entropy_bits=0.0,
                feedback="Empty password. Generate characters to evaluate security profile.",
                color_hex=cls.COLOR_WEAK,
                composition=CompositionStats(0, 0, 0, 0, 0, 0),
            )

        length = len(password)
        uppercase_count = sum(1 for c in password if c.isupper())
        lowercase_count = sum(1 for c in password if c.islower())
        digits_count = sum(1 for c in password if c.isdigit())
        symbols_count = sum(1 for c in password if not c.isalnum())

        has_upper = uppercase_count > 0
        has_lower = lowercase_count > 0
        has_digits = digits_count > 0
        has_symbols = symbols_count > 0

        variety_count = sum([has_upper, has_lower, has_digits, has_symbols])

        composition = CompositionStats(
            uppercase_count=uppercase_count,
            lowercase_count=lowercase_count,
            digits_count=digits_count,
            symbols_count=symbols_count,
            total_length=length,
            diversity_count=variety_count,
        )

        # Step 1: Calculate character pool size (R)
        pool_size = 0
        if has_lower:
            pool_size += 26
        if has_upper:
            pool_size += 26
        if has_digits:
            pool_size += 10
        if has_symbols:
            pool_size += 32

        if pool_size == 0:
            pool_size = 1

        # Step 2: Calculate Pool-based entropy in bits: E = L * log2(R)
        pool_entropy = length * math.log2(pool_size)

        # Step 3: Calculate Shannon entropy to penalize low-variety repetitive strings
        char_counts = Counter(password)
        shannon_entropy_per_char = -sum(
            (count / length) * math.log2(count / length)
            for count in char_counts.values()
        )
        shannon_total_entropy = length * shannon_entropy_per_char

        # Effective base entropy combines theoretical pool with Shannon variety
        effective_entropy = min(pool_entropy, shannon_total_entropy * 1.25)

        # Step 4: Structural penalties
        penalties = 0.0

        # Repeated adjacent characters penalty (e.g. 'aaaa', '1111')
        consecutive_repeats = 0
        for i in range(len(password) - 1):
            if password[i] == password[i + 1]:
                consecutive_repeats += 1
        if consecutive_repeats > 0:
            penalties += min(consecutive_repeats * 4.0, 20.0)

        # Sequential sequence penalty (e.g. '123', 'abc', 'xyz')
        sequential_count = 0
        for i in range(len(password) - 2):
            c1, c2, c3 = ord(password[i]), ord(password[i + 1]), ord(password[i + 2])
            if (c2 == c1 + 1 and c3 == c2 + 1) or (c2 == c1 - 1 and c3 == c2 - 1):
                sequential_count += 1
        if sequential_count > 0:
            penalties += min(sequential_count * 6.0, 18.0)

        # Short length hard penalties
        if length < 8:
            penalties += 25.0

        effective_entropy = max(0.0, effective_entropy - penalties)

        # Step 5: Determine Score and Classification
        if length >= 16 and effective_entropy >= 75.0 and variety_count >= 3:
            score = 4
            level = StrengthLevel.VERY_STRONG
            label = "VERY STRONG"
            feedback = "Excellent password composition & high entropy. Resistant to brute-force attacks."
            color = cls.COLOR_VERY_STRONG

        elif length >= 12 and effective_entropy >= 50.0 and variety_count >= 2:
            score = 3
            level = StrengthLevel.STRONG
            label = "STRONG"
            feedback = "Good length and character diversity. Suitable for sensitive personal credentials."
            color = cls.COLOR_STRONG

        elif length >= 8 and effective_entropy >= 30.0:
            score = 2
            level = StrengthLevel.MODERATE
            label = "MODERATE"
            feedback = "Acceptable for low-risk use. Consider increasing length and character classes."
            color = cls.COLOR_MODERATE

        else:
            score = 1
            level = StrengthLevel.WEAK
            label = "WEAK"
            if length < 8:
                feedback = "Length is too short (< 8 characters). Vulnerable to brute-force attacks."
            else:
                feedback = "Low entropy and limited character diversity. Vulnerable to dictionary attacks."
            color = cls.COLOR_WEAK

        return StrengthResult(
            score=score,
            level=level,
            label=label,
            entropy_bits=round(effective_entropy, 1),
            feedback=feedback,
            color_hex=color,
            composition=composition,
        )

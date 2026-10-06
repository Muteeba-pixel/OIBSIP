"""Cryptographically Secure Password Generator Service.

Uses Python's `secrets` module (backed by os.urandom / CryptGenRandom)
to ensure non-deterministic, cryptographically strong randomness.
Enforces character set diversity guarantees and uniform shuffling.
"""

import secrets
import string
from typing import Dict, List, Optional, Set

from securepass.core.models import PasswordPolicy


class PasswordGenerator:
    """Service responsible for generating cryptographically secure passwords.
    
    Adheres strictly to the given PasswordPolicy. Guarantees that at least one
    character from every enabled character set is included in the output,
    followed by a cryptographically secure Fisher-Yates shuffle.
    """

    # Base character definitions
    UPPERCASE_CHARS: str = string.ascii_uppercase
    LOWERCASE_CHARS: str = string.ascii_lowercase
    DIGIT_CHARS: str = string.digits
    SYMBOL_CHARS: str = "!@#$%^&*()-_=+[]{}|;:,.<>?"

    # Visually confusable / ambiguous characters
    AMBIGUOUS_CHARS: Set[str] = {
        "0", "O", "o",
        "1", "l", "I", "|",
        "`", "'", '"', ";", ":", "."
    }

    def __init__(self, default_policy: Optional[PasswordPolicy] = None) -> None:
        self.default_policy = default_policy or PasswordPolicy()

    def get_character_pools(self, policy: PasswordPolicy) -> Dict[str, str]:
        """Construct individual character pools based on active options.
        
        Args:
            policy: The configuration policy.
            
        Returns:
            Dictionary mapping character set names to their allowed character strings.
        """
        pools: Dict[str, str] = {}

        def _filter(chars: str) -> str:
            if not policy.exclude_ambiguous:
                return chars
            return "".join(c for c in chars if c not in self.AMBIGUOUS_CHARS)

        if policy.include_uppercase:
            filtered = _filter(self.UPPERCASE_CHARS)
            if filtered:
                pools["uppercase"] = filtered

        if policy.include_lowercase:
            filtered = _filter(self.LOWERCASE_CHARS)
            if filtered:
                pools["lowercase"] = filtered

        if policy.include_digits:
            filtered = _filter(self.DIGIT_CHARS)
            if filtered:
                pools["digits"] = filtered

        if policy.include_symbols:
            filtered = _filter(self.SYMBOL_CHARS)
            if filtered:
                pools["symbols"] = filtered

        return pools

    def generate(self, policy: Optional[PasswordPolicy] = None) -> str:
        """Generate a random password meeting all policy constraints.
        
        Uses `secrets.choice` for non-deterministic selection and an in-place
        Fisher-Yates shuffle powered by `secrets.randbelow` to guarantee uniform
        distribution across character positions.
        
        Args:
            policy: Configuration policy. Defaults to `self.default_policy`.
            
        Returns:
            A cryptographically secure password string.
            
        Raises:
            ValueError: If policy validation fails.
        """
        active_policy = policy or self.default_policy
        active_policy.validate()

        pools = self.get_character_pools(active_policy)
        if not pools:
            raise ValueError("No characters available in the selected pool configuration.")

        # Step 1: Ensure character set diversity by taking at least 1 character from each enabled pool
        password_chars: List[str] = []
        for pool_name, pool_chars in pools.items():
            password_chars.append(secrets.choice(pool_chars))

        # Step 2: Combine all enabled characters into a master selection pool
        master_pool = "".join(pools.values())

        # Step 3: Fill remaining length from the master pool
        remaining_length = active_policy.length - len(password_chars)
        for _ in range(remaining_length):
            password_chars.append(secrets.choice(master_pool))

        # Step 4: Cryptographically secure Fisher-Yates shuffle
        self._secure_shuffle(password_chars)

        # Step 5: Constraint enforcement (repeats & sequences)
        if active_policy.avoid_repeats and len(master_pool) > 1:
            self._apply_avoid_repeats(password_chars, master_pool)

        if active_policy.avoid_sequences and len(master_pool) > 2:
            self._apply_avoid_sequences(password_chars, master_pool)

        return "".join(password_chars)

    @staticmethod
    def _secure_shuffle(elements: List[str]) -> None:
        """Perform an in-place Fisher-Yates shuffle using CSPRNG randomness."""
        for i in range(len(elements) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            elements[i], elements[j] = elements[j], elements[i]

    @staticmethod
    def _apply_avoid_repeats(elements: List[str], master_pool: str) -> None:
        """Eliminate adjacent duplicate characters."""
        for i in range(1, len(elements)):
            if elements[i] == elements[i - 1]:
                candidates = [c for c in master_pool if c != elements[i - 1]]
                if candidates:
                    elements[i] = secrets.choice(candidates)

    @staticmethod
    def _apply_avoid_sequences(elements: List[str], master_pool: str) -> None:
        """Break up 3-character alphabetical or numerical runs."""
        for i in range(len(elements) - 2):
            c1, c2, c3 = ord(elements[i]), ord(elements[i + 1]), ord(elements[i + 2])
            if (c2 == c1 + 1 and c3 == c2 + 1) or (c2 == c1 - 1 and c3 == c2 - 1):
                candidates = [c for c in master_pool if ord(c) != c2 + 1 and ord(c) != c2 - 1]
                if candidates:
                    elements[i + 2] = secrets.choice(candidates)

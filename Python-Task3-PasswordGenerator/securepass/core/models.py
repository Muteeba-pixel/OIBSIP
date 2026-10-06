"""Domain models and data contracts for SecurePass.

Pure Python data structures representing password configurations, evaluation results,
and session history records without any GUI dependencies.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class StrengthLevel(Enum):
    """Categorical password strength tiers."""
    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    VERY_STRONG = "VERY STRONG"


@dataclass(frozen=True)
class CompositionStats:
    """Breakdown of character sets present in a password."""
    uppercase_count: int
    lowercase_count: int
    digits_count: int
    symbols_count: int
    total_length: int
    diversity_count: int  # 0 to 4


@dataclass(frozen=True)
class PasswordPolicy:
    """Configuration rules for password generation.
    
    Attributes:
        length: Desired length of the password (min 4, max 128).
        include_uppercase: Include Latin uppercase letters (A-Z).
        include_lowercase: Include Latin lowercase letters (a-z).
        include_digits: Include numerical digits (0-9).
        include_symbols: Include ASCII punctuation and symbols.
        exclude_ambiguous: Exclude characters easily confused visually (e.g. 0, O, 1, l, I).
        avoid_repeats: Prevent adjacent identical characters.
        avoid_sequences: Prevent 3-character alphabetical or numerical runs.
    """
    length: int = 20
    include_uppercase: bool = True
    include_lowercase: bool = True
    include_digits: bool = True
    include_symbols: bool = True
    exclude_ambiguous: bool = False
    avoid_repeats: bool = False
    avoid_sequences: bool = False

    def active_sets_count(self) -> int:
        """Return the number of enabled character sets."""
        return sum([
            self.include_uppercase,
            self.include_lowercase,
            self.include_digits,
            self.include_symbols,
        ])

    def validate(self) -> None:
        """Validate policy constraints.
        
        Raises:
            ValueError: If no character sets are selected or length is out of range.
        """
        if self.active_sets_count() == 0:
            raise ValueError("At least one character type must be selected.")
        
        if self.length < 4:
            raise ValueError("Password length must be at least 4 characters.")
            
        if self.length > 128:
            raise ValueError("Password length cannot exceed 128 characters.")
            
        if self.length < self.active_sets_count():
            raise ValueError(
                f"Password length ({self.length}) cannot be less than the number "
                f"of required character types ({self.active_sets_count()})."
            )


@dataclass(frozen=True)
class StrengthResult:
    """Security assessment of a password.
    
    Attributes:
        score: Numerical score on a 1-4 scale.
        level: Categorical strength tier.
        label: Human-readable display label (e.g. 'VERY STRONG').
        entropy_bits: Calculated Shannon/Pool entropy in bits.
        feedback: Professional assessment feedback explaining the rating.
        color_hex: Suggested UI accent color hex code.
        composition: Granular character breakdown stats.
    """
    score: int
    level: StrengthLevel
    label: str
    entropy_bits: float
    feedback: str
    color_hex: str
    composition: Optional[CompositionStats] = None


@dataclass(frozen=True)
class HistoryEntry:
    """An in-memory record of a password generated during the current session.
    
    Attributes:
        entry_id: Unique sequential or hash identifier.
        password: The plaintext password.
        masked_preview: Masked version for secure on-screen display.
        created_at: ISO-like timestamp string.
        strength_label: Strength rating label at time of generation.
        length: Character count.
    """
    entry_id: str
    password: str
    masked_preview: str
    created_at: str
    strength_label: str
    length: int

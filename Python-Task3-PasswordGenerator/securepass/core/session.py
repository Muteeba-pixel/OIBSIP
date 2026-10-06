"""Volatile In-Memory Session History Manager.

Manages recent generation records in RAM only. Implements strict zero-persistence:
no logs, no file writes, no cache to disk. History is automatically purged on exit
or via explicit manual purge.
"""

from collections import deque
from datetime import datetime
from typing import Deque, List

from securepass.core.models import HistoryEntry


class SessionHistory:
    """Manages an in-memory FIFO buffer of generated passwords for the current session.
    
    Adheres to the zero-persistence security model: passwords exist exclusively
    in volatile memory and are cleared when the application terminates.
    """

    def __init__(self, max_entries: int = 5) -> None:
        self.max_entries = max_entries
        self._history: Deque[HistoryEntry] = deque(maxlen=max_entries)
        self._counter: int = 0

    def add(self, password: str, strength_label: str) -> HistoryEntry:
        """Add a generated password to volatile session history.
        
        Args:
            password: The generated plaintext password.
            strength_label: The strength tier at generation time.
            
        Returns:
            The created HistoryEntry record.
        """
        self._counter += 1
        masked = "•" * len(password)
        now_str = datetime.now().strftime("%H:%M:%S")

        entry = HistoryEntry(
            entry_id=str(self._counter),
            password=password,
            masked_preview=masked,
            created_at=now_str,
            strength_label=strength_label,
            length=len(password),
        )

        self._history.appendleft(entry)
        return entry

    def get_entries(self) -> List[HistoryEntry]:
        """Return a snapshot of current session records, newest first."""
        return list(self._history)

    def clear(self) -> None:
        """Immediately purge all session records from memory."""
        self._history.clear()

    @property
    def count(self) -> int:
        """Return the number of entries currently stored in session."""
        return len(self._history)

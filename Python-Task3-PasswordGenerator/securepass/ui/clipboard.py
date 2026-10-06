"""Clipboard security and interaction manager.

Provides safe interaction with the system clipboard, handles visual feedback
callbacks, and implements native Windows Win32 API fallback for zero-failure
clipboard operations.
"""

import sys
import tkinter as tk
from typing import Callable, Optional


class ClipboardManager:
    """Manages clipboard interactions with defensive fallbacks and callbacks."""

    @staticmethod
    def copy_text(
        root: tk.Misc,
        text: str,
        on_success: Optional[Callable[[], None]] = None
    ) -> bool:
        """Copy plaintext to system clipboard safely.
        
        Attempts standard Tkinter clipboard API first. If unmapped or locked,
        falls back to native Windows Win32 API without throwing unhandled exceptions.
        
        Args:
            root: Any active Tkinter widget or root window.
            text: Text to copy.
            on_success: Optional callback invoked on successful copy.
            
        Returns:
            True if copy succeeded, False otherwise.
        """
        if not text:
            return False

        success = False

        # Strategy 1: Standard Tkinter clipboard
        try:
            root.clipboard_clear()
            root.clipboard_append(text)
            root.update_idletasks()
            success = True
        except Exception:
            success = False

        # Strategy 2: Native Windows Win32 API fallback
        if not success and sys.platform.startswith("win"):
            try:
                import ctypes

                CF_UNICODETEXT = 13
                user32 = ctypes.windll.user32
                kernel32 = ctypes.windll.kernel32

                if user32.OpenClipboard(None):
                    try:
                        user32.EmptyClipboard()
                        encoded = text.encode("utf-16le") + b"\x00\x00"
                        GMEM_MOVEABLE = 0x0002
                        h_mem = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(encoded))
                        if h_mem:
                          p_mem = kernel32.GlobalLock(h_mem)
                          if p_mem:
                            ctypes.memmove(p_mem, encoded, len(encoded))
                            kernel32.GlobalUnlock(h_mem)
                            user32.SetClipboardData(CF_UNICODETEXT, h_mem)
                            success = True
                    finally:
                        user32.CloseClipboard()
            except Exception:
                success = False

        if success and on_success:
            on_success()

        return success

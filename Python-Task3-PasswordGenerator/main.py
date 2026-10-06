"""SecurePass — Password Security Workbench.

Entry point for launching the SecurePass desktop application.
Configures OS-level high-DPI scaling and initializes the CustomTkinter event loop.
"""

import sys
import customtkinter as ctk
from securepass.ui.app import SecurePassApp


def enable_high_dpi() -> None:
    """Enable OS-level High-DPI awareness on Windows to prevent blurry fonts."""
    if sys.platform.startswith("win"):
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass


def main() -> None:
    """Initialize CustomTkinter application root and enter main event loop."""
    enable_high_dpi()
    app = SecurePassApp()
    app.root.mainloop()


if __name__ == "__main__":
    main()

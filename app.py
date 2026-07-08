"""Application entry point for HI ROLEX."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys


def _relaunch_with_python_312_if_needed() -> bool:
    """Relaunch the app with Python 3.12 when default python is newer/unsuitable."""
    if bool(getattr(sys, "frozen", False)) or sys.version_info[:2] == (3, 12):
        return False

    app_path = Path(__file__).resolve()
    try:
        subprocess.Popen(
            ["py", "-3.12", str(app_path), *sys.argv[1:]],
            cwd=app_path.parent,
        )
        return True
    except OSError as error:
        from tkinter import messagebox

        messagebox.showerror(
            "HI ROLEX Python Error",
            (
                "HI ROLEX voice features require Python 3.12.\n\n"
                "Please run:\npy -3.12 app.py\n\n"
                f"Could not relaunch automatically: {error}"
            ),
        )
        return True


class HiRolexApp:
    """Coordinates startup for the desktop application."""

    def __init__(self) -> None:
        from gui.main_window import MainWindow
        from gui.splash_window import SplashWindow
        from utils.app_paths import ensure_required_directories
        from utils.logger import get_logger

        ensure_required_directories()
        self.logger = get_logger()
        self.logger.info("HI ROLEX app startup")
        self.window = MainWindow()
        self.window.withdraw()
        self.splash = SplashWindow(self.window, self._show_main_window)

    def run(self) -> None:
        """Start the GUI event loop."""
        self.window.mainloop()

    def _show_main_window(self) -> None:
        """Show the main window after the splash screen finishes."""
        self.window.deiconify()
        self.window.focus()


def main() -> None:
    """Create and run the HI ROLEX application."""
    if _relaunch_with_python_312_if_needed():
        return

    try:
        app = HiRolexApp()
        app.run()
    except Exception as error:
        from tkinter import messagebox

        from utils.error_handler import show_user_friendly_error

        message = show_user_friendly_error(error)
        messagebox.showerror("HI ROLEX Startup Error", message)


if __name__ == "__main__":
    main()

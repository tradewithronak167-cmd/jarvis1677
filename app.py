"""Application entry point for HI ROLEX."""

from tkinter import messagebox

from gui.main_window import MainWindow
from gui.splash_window import SplashWindow
from utils.app_paths import ensure_required_directories
from utils.error_handler import show_user_friendly_error
from utils.logger import get_logger


class HiRolexApp:
    """Coordinates startup for the desktop application."""

    def __init__(self) -> None:
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
    try:
        app = HiRolexApp()
        app.run()
    except Exception as error:
        message = show_user_friendly_error(error)
        messagebox.showerror("HI ROLEX Startup Error", message)


if __name__ == "__main__":
    main()

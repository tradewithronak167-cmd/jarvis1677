"""Splash screen shown while HI ROLEX starts."""

from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk


class SplashWindow(ctk.CTkToplevel):
    """Small branded startup window."""

    WIDTH: int = 460
    HEIGHT: int = 280

    def __init__(
        self,
        master: ctk.CTk,
        on_complete: Callable[[], None],
        duration_ms: int = 1700,
    ) -> None:
        super().__init__(master)
        self.on_complete = on_complete
        self.duration_ms = duration_ms

        self.overrideredirect(True)
        self.configure(fg_color="#07111F")
        self.attributes("-topmost", True)
        self._center()
        self._create_content()
        self.after(self.duration_ms, self._finish)

    def _center(self) -> None:
        """Center the splash screen on the user's display."""
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_position = int((screen_width - self.WIDTH) / 2)
        y_position = int((screen_height - self.HEIGHT) / 2)
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}+{x_position}+{y_position}")

    def _create_content(self) -> None:
        """Build the branded splash content."""
        self.grid_columnconfigure(0, weight=1)

        logo = ctk.CTkLabel(
            self,
            text="HR",
            width=96,
            height=96,
            corner_radius=48,
            fg_color="#0F172A",
            text_color="#38BDF8",
            font=ctk.CTkFont(size=34, weight="bold"),
        )
        logo.grid(row=0, column=0, pady=(34, 14))

        title = ctk.CTkLabel(
            self,
            text="HI ROLEX",
            text_color="#F8FAFC",
            font=ctk.CTkFont(size=30, weight="bold"),
        )
        title.grid(row=1, column=0)

        subtitle = ctk.CTkLabel(
            self,
            text="Windows AI Assistant",
            text_color="#94A3B8",
            font=ctk.CTkFont(size=14),
        )
        subtitle.grid(row=2, column=0, pady=(2, 24))

        progress = ctk.CTkProgressBar(
            self,
            width=280,
            height=8,
            corner_radius=4,
            progress_color="#38BDF8",
        )
        progress.grid(row=3, column=0, pady=(0, 10))
        progress.set(0.72)

        status = ctk.CTkLabel(
            self,
            text="Starting secure local systems...",
            text_color="#CBD5E1",
            font=ctk.CTkFont(size=13),
        )
        status.grid(row=4, column=0)

    def _finish(self) -> None:
        """Close the splash and show the main window."""
        self.attributes("-topmost", False)
        self.destroy()
        self.on_complete()

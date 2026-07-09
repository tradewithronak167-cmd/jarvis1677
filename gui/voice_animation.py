"""Animated voice status widget for the HI ROLEX dashboard."""

from __future__ import annotations

import math
import tkinter as tk

import customtkinter as ctk


class VoiceAnimation(ctk.CTkFrame):
    """Small animated panel that shows the assistant's current voice state."""

    STATUS_COLORS: dict[str, str] = {
        "Sleeping": "#38BDF8",
        "Listening": "#22C55E",
        "Processing": "#F59E0B",
        "Thinking": "#F59E0B",
        "Speaking": "#A78BFA",
        "Ready": "#22C55E",
    }

    STATUS_HINTS: dict[str, str] = {
        "Sleeping": "Waiting for wake word",
        "Listening": "Microphone is listening",
        "Processing": "Working on the command",
        "Thinking": "AI response is being prepared",
        "Speaking": "Voice response active",
        "Ready": "Ready for commands",
    }

    def __init__(self, master: ctk.CTkFrame) -> None:
        super().__init__(
            master,
            corner_radius=8,
            fg_color="#111827",
            border_width=1,
            border_color="#1F2937",
        )
        self.status = "Sleeping"
        self._frame = 0
        self._running = True

        self.grid_columnconfigure(0, weight=1)

        self.logo_label = ctk.CTkLabel(
            self,
            text="HR",
            width=84,
            height=84,
            corner_radius=42,
            fg_color="#0F172A",
            text_color="#E0F2FE",
            font=ctk.CTkFont(size=30, weight="bold"),
        )
        self.logo_label.grid(row=0, column=0, pady=(22, 12))

        self.status_label = ctk.CTkLabel(
            self,
            text=self.status,
            text_color=self.STATUS_COLORS[self.status],
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.status_label.grid(row=1, column=0, padx=20, pady=(0, 4))

        self.hint_label = ctk.CTkLabel(
            self,
            text=self.STATUS_HINTS[self.status],
            text_color="#9CA3AF",
            font=ctk.CTkFont(size=13),
            wraplength=240,
        )
        self.hint_label.grid(row=2, column=0, padx=20, pady=(0, 16))

        self.canvas = tk.Canvas(
            self,
            width=260,
            height=110,
            bg="#111827",
            highlightthickness=0,
        )
        self.canvas.grid(row=3, column=0, padx=20, pady=(0, 22), sticky="ew")

        self.after(80, self._animate)

    def set_status(self, status: str) -> None:
        """Change the visual animation state."""
        self.status = status
        color = self.STATUS_COLORS.get(status, "#E5E7EB")
        self.status_label.configure(text=status, text_color=color)
        self.hint_label.configure(text=self.STATUS_HINTS.get(status, "Assistant active"))
        self.logo_label.configure(text_color=color)

    def stop(self) -> None:
        """Stop scheduled animation callbacks before app shutdown."""
        self._running = False

    def _animate(self) -> None:
        """Draw animated voice bars."""
        if not self._running:
            return

        self.canvas.delete("all")
        color = self.STATUS_COLORS.get(self.status, "#E5E7EB")
        idle_scale = 0.28 if self.status in {"Sleeping", "Ready"} else 1.0
        speed = 0.18 if self.status in {"Sleeping", "Ready"} else 0.38
        if self.status == "Thinking":
            idle_scale = 0.72
            speed = 0.28

        center_y = 55
        bar_width = 10
        gap = 9
        start_x = 22
        for index in range(15):
            phase = self._frame * speed + index * 0.62
            wave = (math.sin(phase) + 1) / 2
            height = 16 + int(wave * 72 * idle_scale)
            x1 = start_x + index * (bar_width + gap)
            y1 = center_y - height // 2
            x2 = x1 + bar_width
            y2 = center_y + height // 2
            self.canvas.create_rectangle(
                x1,
                y1,
                x2,
                y2,
                fill=color,
                outline="",
                width=0,
            )

        self._frame += 1
        self.after(80, self._animate)

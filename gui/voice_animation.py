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
            fg_color="#050B12",
            border_width=1,
            border_color="#123524",
        )
        self.status = "Sleeping"
        self._frame = 0
        self._running = True

        self.grid_columnconfigure(0, weight=1)

        self.logo_label = ctk.CTkLabel(
            self,
            text="HI ROLEX",
            text_color="#22C55E",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        self.logo_label.grid(row=0, column=0, pady=(18, 8))

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
            width=330,
            height=230,
            bg="#050B12",
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
        """Draw an animated Jarvis-style AI core."""
        if not self._running:
            return

        self.canvas.delete("all")
        color = self.STATUS_COLORS.get(self.status, "#E5E7EB")
        idle_scale = 0.38 if self.status in {"Sleeping", "Ready"} else 1.0
        speed = 0.08 if self.status in {"Sleeping", "Ready"} else 0.18
        if self.status == "Thinking":
            idle_scale = 0.72
            speed = 0.14

        center_x = 165
        center_y = 112
        pulse = 1 + math.sin(self._frame * speed * 2.4) * 0.08 * idle_scale

        for radius, width in ((94, 1), (72, 1), (44, 2)):
            scaled = radius * pulse
            self.canvas.create_oval(
                center_x - scaled,
                center_y - scaled,
                center_x + scaled,
                center_y + scaled,
                outline=color,
                width=width,
            )

        for ring_index, radius in enumerate((34, 55, 76)):
            points = 28 + ring_index * 14
            tilt = 0.34 + ring_index * 0.08
            rotation = self._frame * speed * (1 + ring_index * 0.35)
            for point in range(points):
                angle = (math.tau * point / points) + rotation
                depth = (math.sin(angle + rotation) + 1) / 2
                x = center_x + math.cos(angle) * radius * pulse
                y = center_y + math.sin(angle) * radius * tilt * pulse
                dot_radius = 1.2 + depth * 1.6 * idle_scale
                self.canvas.create_oval(
                    x - dot_radius,
                    y - dot_radius,
                    x + dot_radius,
                    y + dot_radius,
                    fill=color,
                    outline="",
                )

        core_radius = 8 + 4 * idle_scale * (1 + math.sin(self._frame * speed * 3))
        self.canvas.create_oval(
            center_x - core_radius,
            center_y - core_radius,
            center_x + core_radius,
            center_y + core_radius,
            fill=color,
            outline="",
        )

        self._frame += 1
        self.after(80, self._animate)

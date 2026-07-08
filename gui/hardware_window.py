"""Hardware dashboard window for HI ROLEX."""

from __future__ import annotations

import customtkinter as ctk

from hardware.hardware_manager import HardwareManager


class HardwareWindow(ctk.CTkToplevel):
    """Displays Windows hardware information and basic controls."""

    WINDOW_WIDTH: int = 760
    WINDOW_HEIGHT: int = 620

    def __init__(self, master: ctk.CTk) -> None:
        super().__init__(master)
        self.hardware_manager = HardwareManager()
        self.value_labels: dict[str, ctk.CTkLabel] = {}
        self.volume_slider: ctk.CTkSlider | None = None
        self.brightness_slider: ctk.CTkSlider | None = None
        self.status_label: ctk.CTkLabel | None = None
        self._is_refreshing = False

        self._configure_window()
        self.create_layout()
        self.refresh()

    def _configure_window(self) -> None:
        """Configure title, size, and basic behavior."""
        self.title("HI ROLEX Hardware")
        self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.minsize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.resizable(True, True)
        self._center_window()
        self.transient(self.master)
        self.focus()

    def _center_window(self) -> None:
        """Center the Hardware window on screen."""
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_position = int((screen_width - self.WINDOW_WIDTH) / 2)
        y_position = int((screen_height - self.WINDOW_HEIGHT) / 2)
        self.geometry(
            f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}+{x_position}+{y_position}"
        )

    def create_layout(self) -> None:
        """Build the Hardware dashboard layout."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, corner_radius=0, fg_color="#111827")
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header,
            text="Hardware",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#F9FAFB",
        )
        title.grid(row=0, column=0, padx=24, pady=18, sticky="w")

        refresh_button = ctk.CTkButton(header, text="Refresh", command=self.refresh)
        refresh_button.grid(row=0, column=1, padx=24, pady=18, sticky="e")

        content = ctk.CTkFrame(self, fg_color="#0B1120", corner_radius=0)
        content.grid(row=1, column=0, sticky="nsew")
        content.grid_columnconfigure((0, 1), weight=1)

        metrics_frame = ctk.CTkFrame(content, fg_color="#111827", corner_radius=8)
        metrics_frame.grid(row=0, column=0, padx=(24, 12), pady=24, sticky="nsew")
        metrics_frame.grid_columnconfigure(1, weight=1)

        info_frame = ctk.CTkFrame(content, fg_color="#111827", corner_radius=8)
        info_frame.grid(row=0, column=1, padx=(12, 24), pady=24, sticky="nsew")
        info_frame.grid_columnconfigure(1, weight=1)

        metric_rows = [
            ("cpu", "CPU Usage"),
            ("ram", "RAM Usage"),
            ("disk", "Disk Usage"),
            ("battery", "Battery"),
            ("network", "Network"),
        ]
        for row, (key, label) in enumerate(metric_rows):
            self._create_value_row(metrics_frame, row, key, label)

        info_rows = [
            ("operating_system", "Operating System"),
            ("processor", "Processor"),
            ("ram_size", "RAM Size"),
            ("python_version", "Python Version"),
        ]
        for row, (key, label) in enumerate(info_rows):
            self._create_value_row(info_frame, row, key, label)

        controls = ctk.CTkFrame(self, fg_color="#111827", corner_radius=0)
        controls.grid(row=2, column=0, sticky="ew")
        controls.grid_columnconfigure(1, weight=1)

        self._create_volume_control(controls, 0)
        self._create_brightness_control(controls, 1)

        self.status_label = ctk.CTkLabel(
            controls,
            text="Hardware dashboard ready.",
            text_color="#D1D5DB",
        )
        self.status_label.grid(row=2, column=0, columnspan=3, padx=24, pady=(0, 16), sticky="w")

    def _create_value_row(
        self,
        parent: ctk.CTkFrame,
        row: int,
        key: str,
        label_text: str,
    ) -> None:
        """Create one label/value row."""
        label = ctk.CTkLabel(
            parent,
            text=label_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#D1D5DB",
        )
        label.grid(row=row, column=0, padx=(16, 12), pady=10, sticky="w")

        value = ctk.CTkLabel(parent, text="Loading...", text_color="#F9FAFB")
        value.grid(row=row, column=1, padx=(0, 16), pady=10, sticky="w")
        self.value_labels[key] = value

    def _create_volume_control(self, parent: ctk.CTkFrame, row: int) -> None:
        """Create the Windows volume slider."""
        ctk.CTkLabel(parent, text="Volume", font=ctk.CTkFont(weight="bold")).grid(
            row=row,
            column=0,
            padx=(24, 12),
            pady=12,
            sticky="w",
        )
        self.volume_slider = ctk.CTkSlider(
            parent,
            from_=0,
            to=100,
            command=self.on_volume_change,
        )
        self.volume_slider.grid(row=row, column=1, padx=(0, 24), pady=12, sticky="ew")

    def _create_brightness_control(self, parent: ctk.CTkFrame, row: int) -> None:
        """Create the screen brightness slider."""
        ctk.CTkLabel(parent, text="Brightness", font=ctk.CTkFont(weight="bold")).grid(
            row=row,
            column=0,
            padx=(24, 12),
            pady=12,
            sticky="w",
        )
        self.brightness_slider = ctk.CTkSlider(
            parent,
            from_=0,
            to=100,
            command=self.on_brightness_change,
        )
        self.brightness_slider.grid(row=row, column=1, padx=(0, 24), pady=12, sticky="ew")

    def refresh(self) -> None:
        """Refresh all visible hardware values."""
        self._is_refreshing = True
        system_info = self.hardware_manager.get_system_info()
        values = {
            "cpu": self.hardware_manager.get_cpu_usage(),
            "ram": self.hardware_manager.get_ram_usage(),
            "disk": self.hardware_manager.get_disk_usage(),
            "battery": self.hardware_manager.get_battery(),
            "network": self.hardware_manager.get_network_status(),
            **system_info,
        }

        for key, value in values.items():
            if key in self.value_labels:
                self.value_labels[key].configure(text=value)

        self._refresh_volume()
        self._refresh_brightness()
        self._set_status("Hardware values refreshed.")
        self._is_refreshing = False

    def _refresh_volume(self) -> None:
        """Refresh the volume slider."""
        if self.volume_slider is None:
            return

        volume = self.hardware_manager.get_volume()
        if volume is None:
            self.volume_slider.configure(state="disabled")
            self.volume_slider.set(0)
            return

        self.volume_slider.configure(state="normal")
        self.volume_slider.set(volume)

    def _refresh_brightness(self) -> None:
        """Refresh the brightness slider and disable it when unsupported."""
        if self.brightness_slider is None:
            return

        brightness = self.hardware_manager.get_brightness()
        if brightness is None:
            self.brightness_slider.configure(state="disabled")
            self.brightness_slider.set(0)
            self._set_status("Brightness control is unavailable on this device.")
            return

        self.brightness_slider.configure(state="normal")
        self.brightness_slider.set(brightness)

    def on_volume_change(self, value: float) -> None:
        """Apply volume slider changes to Windows volume."""
        if self._is_refreshing:
            return

        success, message = self.hardware_manager.set_volume(round(value))
        self._set_status(message if success else message)

    def on_brightness_change(self, value: float) -> None:
        """Apply brightness slider changes when supported."""
        if self._is_refreshing:
            return

        success, message = self.hardware_manager.set_brightness(round(value))
        self._set_status(message if success else message)
        if not success and self.brightness_slider is not None:
            self.brightness_slider.configure(state="disabled")

    def _set_status(self, message: str) -> None:
        """Display a status message inside the Hardware window."""
        if self.status_label is not None:
            self.status_label.configure(text=message)

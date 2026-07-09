"""Settings window for HI ROLEX."""

from __future__ import annotations

from tkinter import messagebox

import customtkinter as ctk

from config.settings_manager import SettingsManager
from language.language_manager import LanguageManager
from speech.microphone_manager import MicrophoneManager
from speech.speaker_manager import SpeakerManager
from speech.text_to_speech import TextToSpeech


class SettingsWindow(ctk.CTkToplevel):
    """Toplevel window used to view and update application settings."""

    WINDOW_WIDTH: int = 600
    WINDOW_HEIGHT: int = 560

    THEME_OPTIONS: list[str] = ["Dark", "Light"]
    AI_MODE_OPTIONS: list[str] = ["Offline", "Online", "Hybrid"]
    VOICE_STYLE_OPTIONS: list[str] = [
        "Default",
        "Male",
        "Male - Deep",
        "Male - Smooth",
        "Male - Light",
        "Male - Slight",
        "Male - Dim",
        "Female",
        "Female - Deep",
        "Female - Smooth",
        "Female - Light",
        "Female - Slight",
        "Female - Dim",
    ]

    def __init__(
        self,
        master: ctk.CTk,
        settings_manager: SettingsManager,
        language_manager: LanguageManager,
    ) -> None:
        super().__init__(master)
        self.settings_manager = settings_manager
        self.language_manager = language_manager
        self.settings = self.settings_manager.load_settings()
        self.language_options = self.language_manager.available_languages()
        self.microphone_options = MicrophoneManager().list_microphones()
        self.speaker_options = SpeakerManager().list_speakers()
        self.voice_options = self._build_voice_options()

        self.language_var = ctk.StringVar(value=self.settings["language"])
        self.theme_var = ctk.StringVar(value=self.settings["theme"])
        self.ai_mode_var = ctk.StringVar(value=self.settings["ai_mode"])
        self.voice_var = ctk.StringVar(value=self.settings["voice"])
        self.microphone_var = ctk.StringVar(value=self.settings["microphone"])
        self.speaker_var = ctk.StringVar(value=self.settings["speaker"])
        self.wake_word_textbox: ctk.CTkTextbox | None = None
        self.offline_model_textbox: ctk.CTkTextbox | None = None

        self._configure_window()
        self.create_layout()
        self.load_settings_into_fields()

    def _configure_window(self) -> None:
        """Apply size, title, theme, and modal behavior."""
        ctk.set_appearance_mode(self.settings.get("theme", "Dark"))
        self.title(
            f"{self.language_manager.translate('app_title')} "
            f"{self.language_manager.translate('settings')}"
        )
        self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.minsize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.resizable(False, False)
        self._center_window()

        # Keep the settings window above the main window while it is open.
        self.transient(self.master)
        self.grab_set()
        self.focus()

    def _center_window(self) -> None:
        """Center the settings window on the user's screen."""
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_position = int((screen_width - self.WINDOW_WIDTH) / 2)
        y_position = int((screen_height - self.WINDOW_HEIGHT) / 2)
        self.geometry(
            f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}+{x_position}+{y_position}"
        )

    def create_layout(self) -> None:
        """Create the complete settings form layout."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        container = ctk.CTkFrame(self, fg_color="#111827", corner_radius=0)
        container.grid(row=0, column=0, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            container,
            text=self.language_manager.translate("settings"),
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#F9FAFB",
        )
        title_label.grid(row=0, column=0, padx=28, pady=(22, 12), sticky="w")

        form_frame = ctk.CTkFrame(container, fg_color="#0B1120", corner_radius=8)
        form_frame.grid(row=1, column=0, padx=28, pady=(0, 18), sticky="ew")
        form_frame.grid_columnconfigure(1, weight=1)

        self._create_dropdown_row(
            form_frame,
            0,
            self.language_manager.translate("language"),
            self.language_var,
            self.language_options,
        )
        self._create_dropdown_row(
            form_frame,
            1,
            self.language_manager.translate("theme"),
            self.theme_var,
            self.THEME_OPTIONS,
        )
        self._create_dropdown_row(
            form_frame,
            2,
            self.language_manager.translate("ai_mode"),
            self.ai_mode_var,
            self.AI_MODE_OPTIONS,
        )
        self._create_wake_word_row(form_frame, 3)
        self._create_offline_model_row(form_frame, 4)
        self._create_dropdown_row(
            form_frame,
            5,
            self.language_manager.translate("voice"),
            self.voice_var,
            self.voice_options,
        )
        self._create_dropdown_row(
            form_frame,
            6,
            self.language_manager.translate("microphone"),
            self.microphone_var,
            self.microphone_options,
        )
        self._create_dropdown_row(
            form_frame,
            7,
            self.language_manager.translate("speaker"),
            self.speaker_var,
            self.speaker_options,
        )

        self.create_buttons(container)

    def _create_dropdown_row(
        self,
        parent: ctk.CTkFrame,
        row: int,
        label_text: str,
        variable: ctk.StringVar,
        values: list[str],
    ) -> None:
        """Create one labeled dropdown row."""
        label = ctk.CTkLabel(
            parent,
            text=label_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#D1D5DB",
        )
        label.grid(row=row, column=0, padx=(18, 14), pady=9, sticky="w")

        dropdown = ctk.CTkOptionMenu(parent, variable=variable, values=values, height=34)
        dropdown.grid(row=row, column=1, padx=(0, 18), pady=9, sticky="ew")

    def _create_wake_word_row(self, parent: ctk.CTkFrame, row: int) -> None:
        """Create the wake word textbox row."""
        label = ctk.CTkLabel(
            parent,
            text=self.language_manager.translate("wake_word"),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#D1D5DB",
        )
        label.grid(row=row, column=0, padx=(18, 14), pady=9, sticky="w")

        self.wake_word_textbox = ctk.CTkTextbox(parent, height=38, wrap="word")
        self.wake_word_textbox.grid(row=row, column=1, padx=(0, 18), pady=9, sticky="ew")

    def _create_offline_model_row(self, parent: ctk.CTkFrame, row: int) -> None:
        """Create the offline model textbox row."""
        label = ctk.CTkLabel(
            parent,
            text=self.language_manager.translate("offline_model"),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#D1D5DB",
        )
        label.grid(row=row, column=0, padx=(18, 14), pady=9, sticky="w")

        self.offline_model_textbox = ctk.CTkTextbox(parent, height=38, wrap="word")
        self.offline_model_textbox.grid(
            row=row,
            column=1,
            padx=(0, 18),
            pady=9,
            sticky="ew",
        )

    def create_buttons(self, parent: ctk.CTkFrame) -> None:
        """Create Save and Cancel buttons."""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.grid(row=2, column=0, padx=28, pady=(0, 22), sticky="ew")
        button_frame.grid_columnconfigure((0, 1), weight=1)

        save_button = ctk.CTkButton(
            button_frame,
            text=self.language_manager.translate("save"),
            command=self.save,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        save_button.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        cancel_button = ctk.CTkButton(
            button_frame,
            text=self.language_manager.translate("cancel"),
            command=self.cancel,
            height=40,
            fg_color="#374151",
            hover_color="#4B5563",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        cancel_button.grid(row=0, column=1, padx=(8, 0), sticky="ew")

    def load_settings_into_fields(self) -> None:
        """Load current settings into the form controls."""
        if self.wake_word_textbox is None or self.offline_model_textbox is None:
            return

        self.wake_word_textbox.delete("1.0", "end")
        self.wake_word_textbox.insert("1.0", self.settings["wake_word"])
        self.offline_model_textbox.delete("1.0", "end")
        self.offline_model_textbox.insert("1.0", self.settings["offline_model"])

    def collect_settings(self) -> dict[str, str]:
        """Collect all values from the settings form."""
        wake_word = ""
        if self.wake_word_textbox is not None:
            wake_word = self.wake_word_textbox.get("1.0", "end").strip()
        offline_model = ""
        if self.offline_model_textbox is not None:
            offline_model = self.offline_model_textbox.get("1.0", "end").strip()

        return {
            "language": self.language_var.get(),
            "theme": self.theme_var.get(),
            "ai_mode": self.ai_mode_var.get(),
            "offline_model": offline_model or "qwen2.5:3b",
            "wake_word": wake_word or "Hi Rolex",
            "voice": self.voice_var.get(),
            "microphone": self.microphone_var.get(),
            "speaker": self.speaker_var.get(),
        }

    def save(self) -> None:
        """Save settings and close the window."""
        settings = self.collect_settings()
        self.settings_manager.save_settings(settings)
        self.language_manager.change_language(settings["language"])
        ctk.set_appearance_mode(settings["theme"])
        apply_runtime_settings = getattr(self.master, "apply_runtime_settings", None)
        if callable(apply_runtime_settings):
            apply_runtime_settings(settings)
        messagebox.showinfo(
            self.language_manager.translate("settings"),
            self.language_manager.translate("settings_saved"),
        )
        self.destroy()

    def cancel(self) -> None:
        """Close the settings window without saving changes."""
        self.destroy()

    def _build_voice_options(self) -> list[str]:
        """Return friendly voice choices plus installed Windows voices."""
        installed_voices = TextToSpeech(self.settings_manager).list_voices()
        clean_voices = [
            voice
            for voice in installed_voices
            if voice and "not available" not in voice.casefold()
        ]
        options = [*self.VOICE_STYLE_OPTIONS]
        for voice in clean_voices:
            if voice not in options:
                options.append(voice)
        if self.settings.get("voice", "Female") not in options:
            options.append(self.settings.get("voice", "Female"))
        return options

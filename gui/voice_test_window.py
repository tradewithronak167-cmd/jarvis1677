"""Voice diagnostics window for HI ROLEX."""

from __future__ import annotations

import threading
from collections.abc import Callable

import customtkinter as ctk

from speech.speech_manager import SpeechManager


class VoiceTestWindow(ctk.CTkToplevel):
    """Professional diagnostic window for testing voice modules."""

    WINDOW_WIDTH: int = 780
    WINDOW_HEIGHT: int = 560
    SPEAKER_TEST_TEXT: str = "Hello. I am HI ROLEX. Voice system is working."

    def __init__(self, master: ctk.CTk, speech_manager: SpeechManager) -> None:
        super().__init__(master)
        self.speech_manager = speech_manager
        self.status_label: ctk.CTkLabel | None = None
        self.result_textbox: ctk.CTkTextbox | None = None
        self.action_buttons: list[ctk.CTkButton] = []

        self._configure_window()
        self.create_layout()
        self.refresh_diagnostics()

    def _configure_window(self) -> None:
        """Configure the voice diagnostics window."""
        self.title("HI ROLEX Voice Diagnostics")
        self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.minsize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.resizable(True, True)
        self._center_window()
        self.transient(self.master)
        self.focus()

    def _center_window(self) -> None:
        """Center the test window on screen."""
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_position = int((screen_width - self.WINDOW_WIDTH) / 2)
        y_position = int((screen_height - self.WINDOW_HEIGHT) / 2)
        self.geometry(
            f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}+{x_position}+{y_position}"
        )

    def create_layout(self) -> None:
        """Build the voice diagnostics controls and result area."""
        self.configure(fg_color="#080F1D")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(self, corner_radius=0, fg_color="#07111F")
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        title_label = ctk.CTkLabel(
            header,
            text="Voice Diagnostics",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#F8FAFC",
        )
        title_label.grid(row=0, column=0, padx=24, pady=(22, 6), sticky="w")

        self.status_label = ctk.CTkLabel(
            header,
            text="Checking...",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#F59E0B",
        )
        self.status_label.grid(row=0, column=1, padx=24, pady=(22, 6), sticky="e")

        subtitle = ctk.CTkLabel(
            header,
            text="Test microphone, speaker, installed packages, and saved voice settings.",
            font=ctk.CTkFont(size=13),
            text_color="#94A3B8",
        )
        subtitle.grid(row=1, column=0, columnspan=2, padx=24, pady=(0, 18), sticky="w")

        button_frame = ctk.CTkFrame(self, fg_color="#0F172A", corner_radius=8)
        button_frame.grid(row=1, column=0, padx=24, pady=18, sticky="ew")
        button_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        buttons: list[tuple[str, Callable[[], None]]] = [
            ("Refresh", self.refresh_diagnostics),
            ("Microphones", self.show_microphones),
            ("Speakers", self.show_speakers),
            ("TTS Voices", self.show_tts_voices),
            ("Speak Hello", self.speak_hello),
            ("Listen Once", self.listen_once),
        ]

        for column, (text, command) in enumerate(buttons):
            button = ctk.CTkButton(
                button_frame,
                text=text,
                command=command,
                height=40,
                font=ctk.CTkFont(size=13, weight="bold"),
                corner_radius=8,
            )
            button.grid(row=0, column=column, padx=6, pady=12, sticky="ew")
            self.action_buttons.append(button)

        self.result_textbox = ctk.CTkTextbox(
            self,
            wrap="word",
            font=ctk.CTkFont(size=14),
            fg_color="#0F172A",
            border_width=1,
            border_color="#1E293B",
            corner_radius=8,
        )
        self.result_textbox.grid(row=2, column=0, padx=24, pady=(0, 18), sticky="nsew")

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=3, column=0, padx=24, pady=(0, 22), sticky="ew")
        footer.grid_columnconfigure(0, weight=1)

        close_button = ctk.CTkButton(
            footer,
            text="Close",
            command=self.close,
            width=120,
            height=40,
            fg_color="#991B1B",
            hover_color="#B91C1C",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        close_button.grid(row=0, column=1, sticky="e")

    def refresh_diagnostics(self) -> None:
        """Show the complete voice diagnostics report."""
        ready = self.speech_manager.voice_is_ready()
        self._set_status(
            "Voice packages ready" if ready else "Voice setup incomplete",
            "#22C55E" if ready else "#F59E0B",
        )
        self._set_result(self.speech_manager.diagnostics_report())

    def show_microphones(self) -> None:
        """Show detected microphones and readiness status."""
        ready, message = self.speech_manager.speech_to_text.microphone_ready()
        microphones = self.speech_manager.microphone_manager.list_microphones()
        self._set_status(message, "#22C55E" if ready else "#F59E0B")
        self._set_result("Microphone Check\n================\n\n" + "\n".join(microphones))

    def show_speakers(self) -> None:
        """Show detected speakers and TTS readiness status."""
        ready, message = self.speech_manager.text_to_speech.speaker_ready()
        speakers = self.speech_manager.speaker_manager.list_speakers()
        self._set_status(message, "#22C55E" if ready else "#F59E0B")
        self._set_result("Speaker Check\n=============\n\n" + "\n".join(speakers))

    def show_tts_voices(self) -> None:
        """Show available local text-to-speech voices."""
        voices = self.speech_manager.text_to_speech.list_voices()
        self._set_result("Available TTS Voices\n====================\n\n" + "\n".join(voices))

    def speak_hello(self) -> None:
        """Speak a short test phrase without blocking the GUI."""
        self._set_status("Speaking...", "#A78BFA")
        self._set_result("Speaking test phrase...")
        self._run_in_background(lambda: self.speech_manager.speak(self.SPEAKER_TEST_TEXT))

    def listen_once(self) -> None:
        """Listen one time and display recognized text."""
        self._set_status("Listening...", "#22C55E")
        self._set_result("Listening once. Please speak now...")
        self._run_in_background(self.speech_manager.listen_once)

    def close(self) -> None:
        """Stop speech activity and close this window."""
        self.speech_manager.stop()
        self.destroy()

    def _run_in_background(self, task: Callable[[], str]) -> None:
        """Run a voice task without blocking the GUI thread."""
        self._set_buttons_enabled(False)
        thread = threading.Thread(target=self._run_task_and_display_result, args=(task,))
        thread.daemon = True
        thread.start()

    def _run_task_and_display_result(self, task: Callable[[], str]) -> None:
        """Run a background task and send its result back to the GUI."""
        try:
            result = task()
        except Exception as error:
            result = f"Voice test error: {error}"

        self.after(0, lambda: self._finish_background_task(str(result)))

    def _finish_background_task(self, result: str) -> None:
        """Display task result and re-enable controls."""
        self._set_result(result)
        self._set_status("Ready", "#22C55E")
        self._set_buttons_enabled(True)

    def _set_buttons_enabled(self, enabled: bool) -> None:
        """Enable or disable diagnostic buttons during background tests."""
        state = "normal" if enabled else "disabled"
        for button in self.action_buttons:
            button.configure(state=state)

    def _set_status(self, text: str, color: str) -> None:
        """Update the status label."""
        if self.status_label is not None:
            self.status_label.configure(text=text, text_color=color)

    def _set_result(self, text: str) -> None:
        """Display text in the result box."""
        if self.result_textbox is None:
            return

        self.result_textbox.configure(state="normal")
        self.result_textbox.delete("1.0", "end")
        self.result_textbox.insert("1.0", text)
        self.result_textbox.configure(state="disabled")

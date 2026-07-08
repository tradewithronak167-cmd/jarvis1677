"""Voice test window for HI ROLEX."""

from __future__ import annotations

import threading
from collections.abc import Callable

import customtkinter as ctk

from speech.speech_manager import SpeechManager


class VoiceTestWindow(ctk.CTkToplevel):
    """Small diagnostic window for testing Day 5 voice modules."""

    WINDOW_WIDTH: int = 650
    WINDOW_HEIGHT: int = 430
    SPEAKER_TEST_TEXT: str = "Hello. I am HI ROLEX. Voice system is working."

    def __init__(self, master: ctk.CTk, speech_manager: SpeechManager) -> None:
        super().__init__(master)
        self.speech_manager = speech_manager
        self.result_textbox: ctk.CTkTextbox | None = None

        self._configure_window()
        self.create_layout()

    def _configure_window(self) -> None:
        """Configure the voice test window."""
        self.title("HI ROLEX Voice Test")
        self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.minsize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.resizable(False, False)
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
        """Build the voice test controls and result area."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        title_label = ctk.CTkLabel(
            self,
            text="Voice Test",
            font=ctk.CTkFont(size=26, weight="bold"),
        )
        title_label.grid(row=0, column=0, padx=24, pady=(22, 12), sticky="w")

        self.result_textbox = ctk.CTkTextbox(self, height=180, wrap="word")
        self.result_textbox.grid(row=1, column=0, padx=24, pady=(0, 16), sticky="nsew")
        self._set_result("Voice system ready for testing.")

        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=2, column=0, padx=24, pady=(0, 24), sticky="ew")
        button_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        buttons: list[tuple[str, Callable[[], None]]] = [
            ("Test Microphone", self.test_microphone),
            ("Test Speaker", self.test_speaker),
            ("Speak Hello", self.speak_hello),
            ("Listen Once", self.listen_once),
            ("Close", self.close),
        ]

        for column, (text, command) in enumerate(buttons):
            button = ctk.CTkButton(
                button_frame,
                text=text,
                command=command,
                height=40,
                font=ctk.CTkFont(size=13, weight="bold"),
            )
            button.grid(row=0, column=column, padx=5, sticky="ew")

    def test_microphone(self) -> None:
        """Show detected microphones."""
        microphones = self.speech_manager.microphone_manager.list_microphones()
        self._set_result("Detected microphones:\n" + "\n".join(microphones))

    def test_speaker(self) -> None:
        """Show detected speakers."""
        speakers = self.speech_manager.speaker_manager.list_speakers()
        self._set_result("Detected speakers:\n" + "\n".join(speakers))

    def speak_hello(self) -> None:
        """Speak a short test phrase."""
        self._set_result("Speaking test phrase...")
        self._run_in_background(
            lambda: self.speech_manager.speak(self.SPEAKER_TEST_TEXT)
        )

    def listen_once(self) -> None:
        """Listen one time and display the recognized text."""
        self._set_result("Listening once...")
        self._run_in_background(self.speech_manager.listen_once)

    def close(self) -> None:
        """Stop speech activity and close this window."""
        self.speech_manager.stop()
        self.destroy()

    def _run_in_background(self, task: Callable[[], str]) -> None:
        """Run a voice task without blocking the GUI thread."""
        thread = threading.Thread(target=self._run_task_and_display_result, args=(task,))
        thread.daemon = True
        thread.start()

    def _run_task_and_display_result(self, task: Callable[[], str]) -> None:
        """Run a background task and send its result back to the GUI."""
        try:
            result = task()
        except Exception as error:
            result = f"Voice test error: {error}"

        self.after(0, lambda: self._set_result(str(result)))

    def _set_result(self, text: str) -> None:
        """Display text in the result box."""
        if self.result_textbox is None:
            return

        self.result_textbox.configure(state="normal")
        self.result_textbox.delete("1.0", "end")
        self.result_textbox.insert("1.0", text)
        self.result_textbox.configure(state="disabled")

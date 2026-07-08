"""Main application window for HI ROLEX."""

from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk

from automation.automation_manager import AutomationManager, AutomationResult
from assistant.command_models import CommandResult as RouterCommandResult
from assistant.command_router import CommandRouter
from assistant.task_executor import TaskExecutor
from config.settings_manager import SettingsManager
from gui.chat_window import ChatWindow
from gui.file_manager_window import FileManagerWindow
from gui.hardware_window import HardwareWindow
from gui.memory_window import MemoryWindow
from gui.settings_window import SettingsWindow
from gui.voice_test_window import VoiceTestWindow
from language.language_manager import LanguageManager
from speech.speech_manager import SpeechManager
from wakeword.wake_word_manager import WakeWordManager


class MainWindow(ctk.CTk):
    """Primary desktop window for the HI ROLEX assistant."""

    WINDOW_WIDTH: int = 1200
    WINDOW_HEIGHT: int = 700

    def __init__(self) -> None:
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        super().__init__()
        self.settings_manager = SettingsManager()
        self.language_manager = LanguageManager(self.settings_manager)
        self.speech_manager = SpeechManager(self.settings_manager)
        self.automation_manager = AutomationManager()
        self.command_router = CommandRouter(
            task_executor=TaskExecutor(automation_manager=self.automation_manager)
        )
        self.wake_word_manager: WakeWordManager | None = None
        self.chat_window: ChatWindow | None = None
        self.file_manager_window: FileManagerWindow | None = None
        self.hardware_window: HardwareWindow | None = None
        self.memory_window: MemoryWindow | None = None
        self.settings_window: SettingsWindow | None = None
        self.voice_test_window: VoiceTestWindow | None = None
        self.status_value_label: ctk.CTkLabel | None = None
        self.chat_textbox: ctk.CTkTextbox | None = None

        self._configure_window()
        self.create_header()
        self.create_status_bar()
        self.create_chat_area()
        self.create_toolbar()
        self._start_wake_word_system()

    def _configure_window(self) -> None:
        """Apply the core Day 2 window settings."""
        self.title(self.language_manager.translate("app_title"))
        self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.minsize(900, 550)
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self.close_application)
        self._center_window()

        # The grid gives the chat area all remaining space between fixed bars.
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

    def _center_window(self) -> None:
        """Center the window on the user's screen."""
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_position = int((screen_width - self.WINDOW_WIDTH) / 2)
        y_position = int((screen_height - self.WINDOW_HEIGHT) / 2)
        self.geometry(
            f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}+{x_position}+{y_position}"
        )

    def create_header(self) -> None:
        """Create the top title section."""
        header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#111827")
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            header_frame,
            text=self.language_manager.translate("app_title"),
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#F9FAFB",
        )
        title_label.grid(row=0, column=0, padx=24, pady=(20, 16), sticky="w")

        version_label = ctk.CTkLabel(
            header_frame,
            text="HI ROLEX v1.0 Preview",
            font=ctk.CTkFont(size=14),
            text_color="#9CA3AF",
        )
        version_label.grid(row=0, column=1, padx=24, pady=(20, 16), sticky="e")

    def create_status_bar(self) -> None:
        """Create a simple status section for current assistant state."""
        status_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#1F2937")
        status_frame.grid(row=1, column=0, sticky="ew")
        status_frame.grid_columnconfigure(1, weight=1)

        status_title = ctk.CTkLabel(
            status_frame,
            text=f"{self.language_manager.translate('status')}:",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#D1D5DB",
        )
        status_title.grid(row=0, column=0, padx=(24, 8), pady=12, sticky="w")

        self.status_value_label = ctk.CTkLabel(
            status_frame,
            text="Sleeping",
            font=ctk.CTkFont(size=16),
            text_color="#22C55E",
        )
        self.status_value_label.grid(row=0, column=1, padx=(0, 24), pady=12, sticky="w")

    def create_chat_area(self) -> None:
        """Create the central placeholder chat area."""
        chat_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#0B1120")
        chat_frame.grid(row=2, column=0, sticky="nsew")
        chat_frame.grid_columnconfigure(0, weight=1)
        chat_frame.grid_rowconfigure(0, weight=1)

        self.chat_textbox = ctk.CTkTextbox(
            chat_frame,
            font=ctk.CTkFont(size=17),
            text_color="#E5E7EB",
            fg_color="#111827",
            border_width=1,
            border_color="#374151",
            corner_radius=8,
            wrap="word",
        )
        self.chat_textbox.grid(row=0, column=0, padx=24, pady=24, sticky="nsew")
        self.chat_textbox.insert(
            "1.0",
            "HI ROLEX is ready.\n\nSay \"Hi Rolex\" for voice commands, or open Chat for typed commands.",
        )
        self.chat_textbox.configure(state="disabled")

    def create_toolbar(self) -> None:
        """Create the bottom command toolbar."""
        toolbar_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#111827")
        toolbar_frame.grid(row=3, column=0, sticky="ew")
        toolbar_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)

        buttons: list[tuple[str, Callable[[], None]]] = [
            (
                f"🎤 {self.language_manager.translate('microphone')}",
                self.open_voice_test_window,
            ),
            (f"💬 {self.language_manager.translate('chat')}", self.open_chat_window),
            (
                f"⚙ {self.language_manager.translate('settings')}",
                self.open_settings_window,
            ),
            (f"📁 {self.language_manager.translate('files')}", self.open_file_manager_window),
            ("🖥 Hardware", self.open_hardware_window),
            ("Memory", self.open_memory_window),
            (f"❌ {self.language_manager.translate('exit')}", self.close_application),
        ]

        for column_index, (button_text, command) in enumerate(buttons):
            button = ctk.CTkButton(
                toolbar_frame,
                text=button_text,
                command=command,
                height=44,
                font=ctk.CTkFont(size=15, weight="bold"),
                corner_radius=8,
            )
            button.grid(
                row=0,
                column=column_index,
                padx=10,
                pady=18,
                sticky="ew",
            )

    def open_settings_window(self) -> None:
        """Open the Day 3 settings window."""
        if self.settings_window is not None and self.settings_window.winfo_exists():
            self.settings_window.focus()
            return

        self.settings_window = SettingsWindow(
            self,
            self.settings_manager,
            self.language_manager,
        )

    def open_voice_test_window(self) -> None:
        """Open the Day 5 voice test window."""
        if self.voice_test_window is not None and self.voice_test_window.winfo_exists():
            self.voice_test_window.focus()
            return

        self.voice_test_window = VoiceTestWindow(self, self.speech_manager)

    def open_chat_window(self) -> None:
        """Open the Day 10 online AI chat window."""
        if self.chat_window is not None and self.chat_window.winfo_exists():
            self.chat_window.focus()
            return

        self.chat_window = ChatWindow(self, self.speech_manager)

    def open_file_manager_window(self) -> None:
        """Open the Day 8 File Manager window."""
        if self.file_manager_window is not None and self.file_manager_window.winfo_exists():
            self.file_manager_window.focus()
            return

        self.file_manager_window = FileManagerWindow(self)

    def open_hardware_window(self) -> None:
        """Open the Day 9 Hardware window."""
        if self.hardware_window is not None and self.hardware_window.winfo_exists():
            self.hardware_window.focus()
            return

        self.hardware_window = HardwareWindow(self)

    def open_memory_window(self) -> None:
        """Open the Day 12 Memory window."""
        if self.memory_window is not None and self.memory_window.winfo_exists():
            self.memory_window.focus()
            return

        self.memory_window = MemoryWindow(self)

    def _start_wake_word_system(self) -> None:
        """Create and start the background wake-word system."""
        self.wake_word_manager = WakeWordManager(
            settings_manager=self.settings_manager,
            speech_manager=self.speech_manager,
            on_status_change=self.set_status,
            on_command_recognized=self.display_recognized_command,
            on_error=self.display_wake_error,
        )
        self.wake_word_manager.start()

    def set_status(self, status: str) -> None:
        """Update the status indicator from any thread."""
        self.after(0, lambda: self._apply_status(status))

    def _apply_status(self, status: str) -> None:
        """Apply status text and color on the GUI thread."""
        if self.status_value_label is None:
            return

        status_colors = {
            "Sleeping": "#60A5FA",
            "Listening": "#22C55E",
            "Processing": "#F59E0B",
            "Ready": "#22C55E",
        }
        self.status_value_label.configure(
            text=status,
            text_color=status_colors.get(status, "#E5E7EB"),
        )

    def display_recognized_command(self, command: str) -> None:
        """Route a recognized voice command and display the result."""
        command_result = self.command_router.handle_user_input(command, source="voice")
        self.after(0, lambda: self._append_router_result(command_result))
        self._speak_short_feedback(command_result)

    def display_wake_error(self, message: str) -> None:
        """Display wake-listener errors without crashing the GUI."""
        self.after(0, lambda: self._append_chat_message("Voice System", message))

    def _append_chat_message(self, sender: str, message: str) -> None:
        """Append a message to the chat placeholder."""
        if self.chat_textbox is None:
            return

        self.chat_textbox.configure(state="normal")
        self.chat_textbox.insert("end", f"\n\n{sender}: {message}")
        self.chat_textbox.see("end")
        self.chat_textbox.configure(state="disabled")

    def _append_automation_result(self, result: AutomationResult) -> None:
        """Append automation command details to the chat area."""
        if self.chat_textbox is None:
            return

        status_text = "Success" if result.success else "Error"
        message = (
            f"User Command: {result.user_command}\n"
            f"Assistant Action: {result.assistant_action}\n"
            f"Execution Result: {status_text} - {result.execution_result}"
        )
        self._append_chat_message("Automation", message)

    def _append_router_result(self, result: RouterCommandResult) -> None:
        """Append routed command result details to the chat area."""
        if self.chat_textbox is None:
            return

        status_text = "Success" if result.success else "Needs attention"
        message = (
            f"Plan:\n{result.action_details}\n\n"
            f"Result: {status_text} - {result.message}"
        )
        self._append_chat_message("HI ROLEX", message)

    def _speak_short_feedback(self, result: RouterCommandResult) -> None:
        """Speak a short result for voice commands when TTS is available."""
        if result.confirmation_required:
            feedback = "Please confirm this action in the chat window."
        elif result.success:
            feedback = result.message.splitlines()[0][:120]
        else:
            feedback = "I could not complete that request."

        self.speech_manager.speak(feedback)

    def close_application(self) -> None:
        """Close the HI ROLEX application."""
        if self.wake_word_manager is not None:
            self.wake_word_manager.stop()
        self.destroy()

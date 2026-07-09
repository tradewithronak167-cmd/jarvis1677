"""Main application window for HI ROLEX."""

from __future__ import annotations

from collections.abc import Callable
import threading

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
from gui.voice_animation import VoiceAnimation
from gui.voice_test_window import VoiceTestWindow
from language.language_manager import LanguageManager
from speech.speech_manager import SpeechManager
from utils.app_paths import APP_ICON_PATH


class MainWindow(ctk.CTk):
    """Primary desktop window for the HI ROLEX assistant."""

    WINDOW_WIDTH: int = 1200
    WINDOW_HEIGHT: int = 700
    GREETING_TEXT: str = "Hi Ronak. I am ready."
    LISTENING_ERRORS: set[str] = {
        "No speech detected.",
        "Could not understand the audio.",
        "Speech recognition service is unavailable.",
        "Speech recognition packages are not installed.",
    }

    def __init__(self) -> None:
        ctk.set_default_color_theme("blue")

        super().__init__()
        self.settings_manager = SettingsManager()
        ctk.set_appearance_mode(self.settings_manager.load_settings().get("theme", "Dark"))
        self.language_manager = LanguageManager(self.settings_manager)
        self.speech_manager = SpeechManager(self.settings_manager)
        self.automation_manager = AutomationManager()
        self.command_router = CommandRouter(
            task_executor=TaskExecutor(automation_manager=self.automation_manager)
        )
        self.chat_window: ChatWindow | None = None
        self.file_manager_window: FileManagerWindow | None = None
        self.hardware_window: HardwareWindow | None = None
        self.memory_window: MemoryWindow | None = None
        self.settings_window: SettingsWindow | None = None
        self.voice_test_window: VoiceTestWindow | None = None
        self.status_value_label: ctk.CTkLabel | None = None
        self.status_detail_label: ctk.CTkLabel | None = None
        self.voice_animation: VoiceAnimation | None = None
        self.command_entry: ctk.CTkEntry | None = None
        self.activity_textbox: ctk.CTkTextbox | None = None
        self.metric_labels: dict[str, ctk.CTkLabel] = {}
        self._is_closing = False
        self._is_listening_once = False

        self._configure_window()
        self.create_header()
        self.create_status_bar()
        self.create_chat_area()
        self.create_toolbar()
        self._refresh_dashboard_metrics()
        self.after(2200, self._greet_user)

    def _configure_window(self) -> None:
        """Apply the core window settings."""
        self.title(self.language_manager.translate("app_title"))
        self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.minsize(980, 600)
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self.close_application)
        self._apply_app_icon()
        self._center_window()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

    def _apply_app_icon(self) -> None:
        """Apply the branded icon when the .ico asset exists."""
        if not APP_ICON_PATH.exists():
            return

        try:
            self.iconbitmap(str(APP_ICON_PATH))
        except Exception:
            return

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
        """Create the top branded title section."""
        header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#07111F")
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)

        logo_label = ctk.CTkLabel(
            header_frame,
            text="HR",
            width=54,
            height=54,
            corner_radius=27,
            fg_color="#0F172A",
            text_color="#38BDF8",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        logo_label.grid(row=0, column=0, padx=(24, 14), pady=(18, 16), sticky="w")

        title_label = ctk.CTkLabel(
            header_frame,
            text=self.language_manager.translate("app_title"),
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color="#F9FAFB",
        )
        title_label.grid(row=0, column=1, pady=(18, 16), sticky="w")

        version_label = ctk.CTkLabel(
            header_frame,
            text="v1.0 Preview",
            font=ctk.CTkFont(size=14),
            text_color="#9CA3AF",
        )
        version_label.grid(row=0, column=2, padx=24, pady=(18, 16), sticky="e")

    def create_status_bar(self) -> None:
        """Create a compact assistant status section."""
        status_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#0B1220")
        status_frame.grid(row=1, column=0, sticky="ew")
        status_frame.grid_columnconfigure(2, weight=1)

        status_title = ctk.CTkLabel(
            status_frame,
            text=f"{self.language_manager.translate('status')}:",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#D1D5DB",
        )
        status_title.grid(row=0, column=0, padx=(24, 8), pady=12, sticky="w")

        self.status_value_label = ctk.CTkLabel(
            status_frame,
            text="Ready",
            font=ctk.CTkFont(size=16),
            text_color="#22C55E",
        )
        self.status_value_label.grid(row=0, column=1, padx=(0, 24), pady=12, sticky="w")

        mode_label = ctk.CTkLabel(
            status_frame,
            text="Default assistant mode - greets and listens automatically",
            font=ctk.CTkFont(size=13),
            text_color="#94A3B8",
        )
        mode_label.grid(row=0, column=2, padx=(0, 24), pady=12, sticky="e")

    def create_chat_area(self) -> None:
        """Create the Jarvis-style command center dashboard."""
        assistant_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#080F1D")
        assistant_frame.grid(row=2, column=0, sticky="nsew")
        assistant_frame.grid_columnconfigure(0, weight=0)
        assistant_frame.grid_columnconfigure(1, weight=1)
        assistant_frame.grid_columnconfigure(2, weight=0)
        assistant_frame.grid_rowconfigure(0, weight=1)

        self._create_system_panel(assistant_frame)

        center_frame = ctk.CTkFrame(
            assistant_frame,
            fg_color="transparent",
        )
        center_frame.grid(row=0, column=1, padx=20, pady=22, sticky="nsew")
        center_frame.grid_columnconfigure(0, weight=1)
        center_frame.grid_rowconfigure(0, weight=1)

        core_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        core_frame.grid(row=0, column=0, sticky="nsew")
        core_frame.grid_columnconfigure(0, weight=1)
        core_frame.grid_rowconfigure(0, weight=1)

        self.voice_animation = VoiceAnimation(core_frame)
        self.voice_animation.grid(row=0, column=0, pady=(0, 18))
        self.voice_animation.set_status("Ready")

        heading_label = ctk.CTkLabel(
            core_frame,
            text="HI ROLEX COMMAND CORE",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#22C55E",
        )
        heading_label.grid(row=1, column=0, pady=(0, 8))

        self.status_detail_label = ctk.CTkLabel(
            core_frame,
            text="I will greet you, then listen for your command.",
            font=ctk.CTkFont(size=17),
            text_color="#CBD5E1",
            wraplength=760,
            justify="center",
        )
        self.status_detail_label.grid(row=2, column=0, pady=(0, 18))

        action_frame = ctk.CTkFrame(core_frame, fg_color="#0B1220", corner_radius=8)
        action_frame.grid(row=3, column=0, sticky="ew")
        action_frame.grid_columnconfigure(0, weight=1)

        self.command_entry = ctk.CTkEntry(
            action_frame,
            height=44,
            placeholder_text="Ask a question or type a task...",
            font=ctk.CTkFont(size=15),
            fg_color="#0F172A",
            border_color="#1E293B",
            corner_radius=8,
        )
        self.command_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.command_entry.bind("<Return>", self._handle_command_entry_return)

        run_button = ctk.CTkButton(
            action_frame,
            text="Run",
            command=self.run_typed_command,
            width=92,
            height=44,
            corner_radius=8,
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        run_button.grid(row=0, column=1, padx=(0, 10))

        self._create_activity_panel(assistant_frame)

    def _create_system_panel(self, parent: ctk.CTkFrame) -> None:
        """Create the left live system monitor panel."""
        panel = ctk.CTkFrame(
            parent,
            width=270,
            fg_color="#050B12",
            border_width=1,
            border_color="#123524",
            corner_radius=8,
        )
        panel.grid(row=0, column=0, padx=(22, 8), pady=22, sticky="ns")
        panel.grid_propagate(False)
        panel.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            panel,
            text="SYSTEM MONITOR",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#22C55E",
        )
        title.grid(row=0, column=0, padx=18, pady=(20, 12), sticky="w")

        subtitle = ctk.CTkLabel(
            panel,
            text="Safe Windows access",
            font=ctk.CTkFont(size=12),
            text_color="#94A3B8",
        )
        subtitle.grid(row=1, column=0, padx=18, pady=(0, 14), sticky="w")

        metric_names = ("CPU", "RAM", "DISK", "BATTERY", "NETWORK", "VOLUME")
        for index, name in enumerate(metric_names, start=2):
            card = ctk.CTkFrame(panel, fg_color="#08111D", corner_radius=8)
            card.grid(row=index, column=0, padx=14, pady=7, sticky="ew")
            card.grid_columnconfigure(1, weight=1)

            label = ctk.CTkLabel(
                card,
                text=name,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#86EFAC",
            )
            label.grid(row=0, column=0, padx=(12, 8), pady=10, sticky="w")

            value = ctk.CTkLabel(
                card,
                text="Loading",
                font=ctk.CTkFont(size=12),
                text_color="#E5E7EB",
                anchor="e",
            )
            value.grid(row=0, column=1, padx=(4, 12), pady=10, sticky="e")
            self.metric_labels[name] = value

        hint = ctk.CTkLabel(
            panel,
            text="Try: open Chrome, set volume to 50, what is Python",
            font=ctk.CTkFont(size=12),
            text_color="#64748B",
            wraplength=220,
            justify="left",
        )
        hint.grid(row=9, column=0, padx=18, pady=(18, 12), sticky="ew")

    def _create_activity_panel(self, parent: ctk.CTkFrame) -> None:
        """Create the right conversation and activity panel."""
        panel = ctk.CTkFrame(
            parent,
            width=330,
            fg_color="#050B12",
            border_width=1,
            border_color="#123524",
            corner_radius=8,
        )
        panel.grid(row=0, column=2, padx=(8, 22), pady=22, sticky="ns")
        panel.grid_propagate(False)
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)

        title = ctk.CTkLabel(
            panel,
            text="CONVERSATION",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#22C55E",
        )
        title.grid(row=0, column=0, padx=18, pady=(20, 12), sticky="w")

        self.activity_textbox = ctk.CTkTextbox(
            panel,
            wrap="word",
            fg_color="#07111F",
            text_color="#D1FAE5",
            border_width=1,
            border_color="#123524",
            corner_radius=8,
            font=ctk.CTkFont(size=13),
        )
        self.activity_textbox.grid(row=1, column=0, padx=14, pady=(0, 14), sticky="nsew")
        self.activity_textbox.insert(
            "end",
            "HI ROLEX is online.\nVoice control is ready after greeting.\n",
        )
        self.activity_textbox.configure(state="disabled")

    def create_toolbar(self) -> None:
        """Create the bottom command toolbar."""
        toolbar_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#07111F")
        toolbar_frame.grid(row=3, column=0, sticky="ew")
        toolbar_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        buttons: list[tuple[str, Callable[[], None]]] = [
            (self.language_manager.translate("chat"), self.open_chat_window),
            (self.language_manager.translate("settings"), self.open_settings_window),
            (self.language_manager.translate("files"), self.open_file_manager_window),
            ("Hardware", self.open_hardware_window),
            ("Memory", self.open_memory_window),
            (self.language_manager.translate("exit"), self.close_application),
        ]

        for column_index, (button_text, command) in enumerate(buttons):
            is_exit_button = column_index == len(buttons) - 1
            button = ctk.CTkButton(
                toolbar_frame,
                text=button_text,
                command=command,
                height=44,
                font=ctk.CTkFont(size=15, weight="bold"),
                corner_radius=8,
                fg_color="#991B1B" if is_exit_button else "#1D4ED8",
                hover_color="#B91C1C" if is_exit_button else "#2563EB",
            )
            button.grid(
                row=0,
                column=column_index,
                padx=10,
                pady=18,
                sticky="ew",
            )

    def open_settings_window(self) -> None:
        """Open the settings window."""
        if self.settings_window is not None and self.settings_window.winfo_exists():
            self.settings_window.focus()
            return

        self.settings_window = SettingsWindow(
            self,
            self.settings_manager,
            self.language_manager,
        )

    def apply_runtime_settings(self, settings: dict[str, str]) -> None:
        """Apply settings that can safely change while the app is running."""
        ctk.set_appearance_mode(settings.get("theme", "Dark"))
        self.language_manager.change_language(settings.get("language", "English"))
        self.title(self.language_manager.translate("app_title"))
        self._set_status_detail(
            f"Settings updated. Language: {settings.get('language', 'English')}. "
            f"Theme: {settings.get('theme', 'Dark')}."
        )

    def open_voice_test_window(self) -> None:
        """Open the voice test window."""
        if self.voice_test_window is not None and self.voice_test_window.winfo_exists():
            self.voice_test_window.focus()
            return

        self.voice_test_window = VoiceTestWindow(self, self.speech_manager)

    def open_chat_window(self) -> None:
        """Open the AI chat window."""
        if self.chat_window is not None and self.chat_window.winfo_exists():
            self.chat_window.focus()
            return

        self.chat_window = ChatWindow(self, self.speech_manager)

    def open_file_manager_window(self) -> None:
        """Open the File Manager window."""
        if self.file_manager_window is not None and self.file_manager_window.winfo_exists():
            self.file_manager_window.focus()
            return

        self.file_manager_window = FileManagerWindow(self)

    def open_hardware_window(self) -> None:
        """Open the Hardware window."""
        if self.hardware_window is not None and self.hardware_window.winfo_exists():
            self.hardware_window.focus()
            return

        self.hardware_window = HardwareWindow(self)

    def open_memory_window(self) -> None:
        """Open the Memory window."""
        if self.memory_window is not None and self.memory_window.winfo_exists():
            self.memory_window.focus()
            return

        self.memory_window = MemoryWindow(self)

    def listen_once_from_dashboard(self) -> None:
        """Listen for one spoken command without requiring a wake word."""
        if self._is_listening_once or self._is_closing:
            return

        self._is_listening_once = True
        self.set_status("Listening")
        self._append_chat_message("HI ROLEX", "Listening...")
        thread = threading.Thread(target=self._listen_once_in_background, daemon=True)
        thread.start()

    def run_typed_command(self) -> None:
        """Run text typed on the main assistant screen."""
        if self.command_entry is None or self._is_closing:
            return

        command = self.command_entry.get().strip()
        if not command:
            self._set_status_detail("Type a question or task first.")
            return

        self.command_entry.delete(0, "end")
        self._set_status_detail(f"Working on: {command}")
        self.set_status("Processing")
        thread = threading.Thread(
            target=self._run_command_in_background,
            args=(command, "typed"),
            daemon=True,
        )
        thread.start()

    def _handle_command_entry_return(self, event: object) -> str:
        """Run the typed command when Enter is pressed."""
        self.run_typed_command()
        return "break"

    def _run_command_in_background(self, command: str, source: str) -> None:
        """Run a command without freezing the dashboard."""
        result = self.command_router.handle_user_input(command, source=source)
        self.after(0, lambda: self._show_voice_result(result))
        self._speak_feedback_blocking(result)
        self.set_status("Ready")

    def _listen_once_in_background(self) -> None:
        """Capture one voice command, execute it, and speak the result."""
        command = self.speech_manager.listen_once()
        if self._is_recognition_error(command):
            self.after(0, lambda: self._handle_listen_error(command))
            return

        self.after(0, lambda: self._append_chat_message("You", command))
        self.set_status("Processing")
        result = self.command_router.handle_user_input(command, source="voice")
        self.after(0, lambda: self._handle_voice_result(result))

    def _handle_voice_result(self, result: RouterCommandResult) -> None:
        """Display a compact voice result and finish the listening cycle."""
        self._show_voice_result(result)
        self._is_listening_once = False
        self._speak_short_feedback(result)

    def _handle_listen_error(self, message: str) -> None:
        """Recover cleanly when voice capture fails."""
        self._is_listening_once = False
        self._set_status_detail(message)
        self.set_status("Speaking")
        threading.Thread(
            target=self._speak_and_set_ready,
            args=("I did not catch that. Please try again.",),
            daemon=True,
        ).start()

    def _is_recognition_error(self, text: str) -> bool:
        """Return True when speech-to-text returned a friendly error message."""
        return text in self.LISTENING_ERRORS or text.startswith("Microphone error:")

    def _greet_user(self) -> None:
        """Greet Ronak by voice after the app has opened."""
        if self._is_closing:
            return
        self._set_status_detail(self.GREETING_TEXT)
        self.set_status("Speaking")
        threading.Thread(
            target=self._speak_greeting_then_listen,
            args=(self.GREETING_TEXT,),
            daemon=True,
        ).start()

    def _speak_greeting_then_listen(self, text: str) -> None:
        """Speak the startup greeting, then listen once by default."""
        self.speech_manager.speak(text)
        self.set_status("Ready")
        self._set_status_detail("Listening for your command...")
        self.after(500, self.listen_once_from_dashboard)

    def set_status(self, status: str) -> None:
        """Update the status indicator from any thread."""
        if self._is_closing:
            return
        self.after(0, lambda: self._apply_status(status))

    def _apply_status(self, status: str) -> None:
        """Apply status text, color, and animation state on the GUI thread."""
        if self.status_value_label is None:
            return

        status_colors = {
            "Sleeping": "#38BDF8",
            "Listening": "#22C55E",
            "Processing": "#F59E0B",
            "Thinking": "#F59E0B",
            "Speaking": "#A78BFA",
            "Ready": "#22C55E",
        }
        self.status_value_label.configure(
            text=status,
            text_color=status_colors.get(status, "#E5E7EB"),
        )
        if self.voice_animation is not None:
            self.voice_animation.set_status(status)

    def display_recognized_command(self, command: str) -> None:
        """Route a recognized voice command and display the result."""
        if self._is_closing:
            return
        command_result = self.command_router.handle_user_input(command, source="voice")
        self.after(0, lambda: self._append_router_result(command_result))
        self._speak_short_feedback(command_result)

    def display_wake_error(self, message: str) -> None:
        """Display wake-listener errors without crashing the GUI."""
        if self._is_closing:
            return
        self.after(0, lambda: self._set_status_detail(message))

    def _append_chat_message(self, sender: str, message: str) -> None:
        """Show the latest voice assistant event without a chat transcript."""
        self._set_status_detail(f"{sender}: {message}")
        self._append_activity_message(sender, message)

    def _set_status_detail(self, message: str) -> None:
        """Update the large assistant detail line from any thread."""
        if self._is_closing:
            return
        self.after(0, lambda: self._apply_status_detail(message))

    def _apply_status_detail(self, message: str) -> None:
        """Apply assistant detail text on the GUI thread."""
        if self.status_detail_label is not None:
            self.status_detail_label.configure(text=message[:220])

    def _append_activity_message(self, sender: str, message: str) -> None:
        """Append a compact activity line to the right command feed."""
        if self._is_closing:
            return
        self.after(0, lambda: self._apply_activity_message(sender, message))

    def _apply_activity_message(self, sender: str, message: str) -> None:
        """Update the activity feed on the GUI thread."""
        if self.activity_textbox is None:
            return

        self.activity_textbox.configure(state="normal")
        self.activity_textbox.insert("end", f"\n{sender}\n{message[:700]}\n")
        self.activity_textbox.see("end")
        self.activity_textbox.configure(state="disabled")

    def _refresh_dashboard_metrics(self) -> None:
        """Refresh safe hardware metrics shown on the dashboard."""
        if self._is_closing:
            return

        try:
            metrics = {
                "CPU": self.hardware_manager.get_cpu_usage(),
                "RAM": self.hardware_manager.get_ram_usage(),
                "DISK": self.hardware_manager.get_disk_usage(),
                "BATTERY": self.hardware_manager.get_battery(),
                "NETWORK": self.hardware_manager.get_network_status(),
                "VOLUME": self._format_optional_percent(self.hardware_manager.get_volume()),
            }
        except Exception:
            metrics = {}

        for key, value in metrics.items():
            label = self.metric_labels.get(key)
            if label is not None:
                label.configure(text=str(value)[:34])

        self.after(3000, self._refresh_dashboard_metrics)

    def _append_automation_result(self, result: AutomationResult) -> None:
        """Append automation command details to the activity log."""
        status_text = "Success" if result.success else "Error"
        message = (
            f"User Command: {result.user_command}\n"
            f"Assistant Action: {result.assistant_action}\n"
            f"Execution Result: {status_text} - {result.execution_result}"
        )
        self._append_chat_message("Automation", message)

    def _append_router_result(self, result: RouterCommandResult) -> None:
        """Append routed command result details to the activity log."""
        self._show_voice_result(result)

    def _show_voice_result(self, result: RouterCommandResult) -> None:
        """Show a compact latest result for the voice-only dashboard."""
        prefix = "Done" if result.success else "Needs attention"
        self._set_status_detail(f"{prefix}: {result.message}")
        self._append_activity_message("HI ROLEX", f"{prefix}: {result.message}")

    def _format_optional_percent(self, value: int | None) -> str:
        """Format optional integer percentages for the dashboard."""
        if value is None:
            return "Unavailable"
        return f"{value}%"

    def _speak_short_feedback(self, result: RouterCommandResult) -> None:
        """Speak a short result for voice commands when TTS is available."""
        self.set_status("Speaking")
        threading.Thread(
            target=self._speak_feedback_and_set_ready,
            args=(result,),
            daemon=True,
        ).start()

    def _speak_feedback_and_set_ready(self, result: RouterCommandResult) -> None:
        """Speak result feedback, then return to Ready."""
        self._speak_feedback_blocking(result)
        self.set_status("Ready")

    def _speak_feedback_blocking(self, result: RouterCommandResult) -> None:
        """Speak a full useful response for voice-first interaction."""
        if result.confirmation_required:
            feedback = "Please confirm this action."
        elif result.success:
            feedback = result.message.strip()[:900]
        else:
            feedback = result.message.strip()[:450] or "I could not complete that request."

        self.set_status("Speaking")
        self.speech_manager.speak(feedback)

    def _speak_and_set_ready(self, text: str) -> None:
        """Speak text without freezing the GUI, then return to Ready."""
        self.speech_manager.speak(text)
        self.set_status("Ready")

    def close_application(self) -> None:
        """Close the HI ROLEX application."""
        if self._is_closing:
            return

        self._is_closing = True
        try:
            self.withdraw()
        except Exception:
            pass

        self._stop_background_services()
        self._close_child_windows()

        try:
            self.quit()
        except Exception:
            pass

        try:
            self.destroy()
        except Exception:
            pass

    def _stop_background_services(self) -> None:
        """Stop voice, wake-word, and animation services during shutdown."""
        if self.voice_animation is not None:
            try:
                self.voice_animation.stop()
            except Exception:
                pass
        try:
            self.speech_manager.stop()
        except Exception:
            pass

    def _close_child_windows(self) -> None:
        """Destroy open child windows before the root window closes."""
        windows = (
            self.chat_window,
            self.file_manager_window,
            self.hardware_window,
            self.memory_window,
            self.settings_window,
            self.voice_test_window,
        )
        for window in windows:
            try:
                if window is not None and window.winfo_exists():
                    window.destroy()
            except Exception:
                continue

"""Online AI chat window for HI ROLEX."""

from __future__ import annotations

import threading
import time

import customtkinter as ctk

from ai.ai_manager import AIManager
from ai.conversation_manager import ConversationManager
from assistant.command_models import CommandResult
from assistant.command_router import CommandRouter
from assistant.task_executor import TaskExecutor
from speech.speech_manager import SpeechManager


class ChatWindow(ctk.CTkToplevel):
    """CustomTkinter window for online AI chat."""

    WINDOW_WIDTH: int = 820
    WINDOW_HEIGHT: int = 620

    def __init__(self, master: ctk.CTk, speech_manager: SpeechManager | None = None) -> None:
        super().__init__(master)
        self.conversation_manager = ConversationManager()
        self.ai_manager = AIManager(self.conversation_manager)
        self.command_router = CommandRouter(
            task_executor=TaskExecutor(ai_manager=self.ai_manager)
        )
        self.speech_manager = speech_manager

        self.chat_display: ctk.CTkTextbox | None = None
        self.input_box: ctk.CTkTextbox | None = None
        self.status_label: ctk.CTkLabel | None = None
        self.confirm_button: ctk.CTkButton | None = None
        self.cancel_button: ctk.CTkButton | None = None

        self._configure_window()
        self.create_layout()
        self.load_previous_conversation()

    def _configure_window(self) -> None:
        """Configure window title, size, and behavior."""
        self.title("HI ROLEX Chat")
        self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.minsize(700, 520)
        self.resizable(True, True)
        self._center_window()
        self.transient(self.master)
        self.focus()

    def _center_window(self) -> None:
        """Center the chat window on screen."""
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_position = int((screen_width - self.WINDOW_WIDTH) / 2)
        y_position = int((screen_height - self.WINDOW_HEIGHT) / 2)
        self.geometry(
            f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}+{x_position}+{y_position}"
        )

    def create_layout(self) -> None:
        """Build the chat display, input area, and controls."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, corner_radius=0, fg_color="#07111F")
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header,
            text=f"HI ROLEX Chat - {self.ai_manager.get_status_text()}",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#F9FAFB",
        )
        title.grid(row=0, column=0, padx=24, pady=(18, 6), sticky="w")

        self.status_label = ctk.CTkLabel(
            header,
            text=self._status_text(),
            text_color="#93C5FD",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self.status_label.grid(row=1, column=0, padx=24, pady=(0, 14), sticky="w")

        self.chat_display = ctk.CTkTextbox(
            self,
            wrap="word",
            font=ctk.CTkFont(size=15),
            fg_color="#080F1D",
            text_color="#E5E7EB",
            border_width=1,
            border_color="#1E293B",
            corner_radius=8,
        )
        self.chat_display.grid(row=1, column=0, padx=24, pady=18, sticky="nsew")
        self.chat_display.configure(state="disabled")

        input_frame = ctk.CTkFrame(self, fg_color="#07111F", corner_radius=0)
        input_frame.grid(row=2, column=0, sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)

        self.input_box = ctk.CTkTextbox(
            input_frame,
            height=70,
            wrap="word",
            fg_color="#0F172A",
            border_width=1,
            border_color="#1E293B",
            corner_radius=8,
            font=ctk.CTkFont(size=14),
        )
        self.input_box.grid(row=0, column=0, padx=24, pady=(18, 12), sticky="ew")
        self.input_box.bind("<Return>", self._handle_enter_key)
        self.input_box.bind("<Shift-Return>", self._handle_shift_enter_key)

        controls = ctk.CTkFrame(input_frame, fg_color="transparent")
        controls.grid(row=1, column=0, padx=24, pady=(0, 18), sticky="ew")
        controls.grid_columnconfigure(1, weight=1)

        clear_button = ctk.CTkButton(
            controls,
            text="Clear Chat",
            command=self.clear_chat,
            fg_color="#374151",
            hover_color="#4B5563",
        )
        clear_button.grid(row=0, column=0, padx=(0, 10), sticky="w")

        self.confirm_button = ctk.CTkButton(
            controls,
            text="Confirm",
            command=self.confirm_pending_action,
            fg_color="#15803D",
            hover_color="#166534",
        )
        self.confirm_button.grid(row=0, column=2, padx=(10, 6), sticky="e")
        self.confirm_button.grid_remove()

        self.cancel_button = ctk.CTkButton(
            controls,
            text="Cancel",
            command=self.cancel_pending_action,
            fg_color="#7F1D1D",
            hover_color="#991B1B",
        )
        self.cancel_button.grid(row=0, column=3, padx=(6, 0), sticky="e")
        self.cancel_button.grid_remove()

    def load_previous_conversation(self) -> None:
        """Load saved conversation history into the display."""
        history = self.conversation_manager.get_history()
        if not history:
            self._append_display("System", "Chat ready. Basic AI mode works without setup.")
            return

        for message in history:
            role = "You" if message["role"] == "user" else "HI ROLEX"
            self._append_display(role, message["content"])

    def send_message(self) -> None:
        """Send the user's message to the AI manager."""
        user_message = self._get_input_text()
        if not user_message:
            self._set_status("Please type a message first.")
            return

        self._clear_input()
        self._append_display("You", user_message)
        self._set_status("Thinking...")
        self.after(100, lambda: self._set_status(self.ai_manager.get_thinking_status()))

        self._hide_confirmation_controls()
        thread = threading.Thread(
            target=self._route_command_in_background,
            args=(user_message,),
            daemon=True,
        )
        thread.start()

    def _handle_enter_key(self, event: object) -> str:
        """Send the current message when Enter is pressed."""
        self.send_message()
        return "break"

    def _handle_shift_enter_key(self, event: object) -> None:
        """Allow Shift+Enter to insert a new line."""
        return None

    def confirm_pending_action(self) -> None:
        """Confirm and execute the pending command-router action."""
        self._hide_confirmation_controls()
        self._set_status("Executing confirmed action...")
        thread = threading.Thread(
            target=self._confirm_in_background,
            daemon=True,
        )
        thread.start()

    def cancel_pending_action(self) -> None:
        """Cancel the pending command-router action."""
        self._hide_confirmation_controls()
        result = self.command_router.cancel_pending_action()
        self._handle_command_result(result)

    def clear_chat(self) -> None:
        """Clear the display and saved conversation history."""
        self.conversation_manager.clear_history()
        if self.chat_display is not None:
            self.chat_display.configure(state="normal")
            self.chat_display.delete("1.0", "end")
            self.chat_display.configure(state="disabled")
        self._append_display("System", "Chat cleared.")
        self._set_status(self._status_text())

    def _route_command_in_background(self, user_message: str) -> None:
        """Route a command without blocking the GUI."""
        started_at = time.perf_counter()
        result = self.command_router.handle_user_input(user_message, source="chat")
        elapsed_seconds = time.perf_counter() - started_at
        self.after(0, lambda: self._handle_command_result(result, elapsed_seconds))

    def _confirm_in_background(self) -> None:
        """Execute a confirmed pending action without blocking the GUI."""
        result = self.command_router.confirm_pending_action()
        self.after(0, lambda: self._handle_command_result(result))

    def _handle_command_result(
        self,
        result: CommandResult,
        elapsed_seconds: float | None = None,
    ) -> None:
        """Display router plan/result and update confirmation controls."""
        is_ai_response = result.action_details.strip() == "1. Ask AI"
        if result.action_details:
            plan_label = "AI Request" if is_ai_response else "Assistant Action"
            self._append_display(plan_label, result.action_details)

        response_label = "AI Response" if is_ai_response else "Execution Result"
        self._append_display(response_label, result.message)
        if result.confirmation_required:
            self._set_status("Confirmation required.")
        elif result.success:
            self._set_status(self._completion_status("Completed", elapsed_seconds))
        else:
            status = "AI unavailable." if "AI unavailable" in result.message else "Request not completed."
            self._set_status(self._completion_status(status, elapsed_seconds))

        if result.confirmation_required:
            self._show_confirmation_controls()
        else:
            self._hide_confirmation_controls()

        if is_ai_response and result.success:
            self._speak_ai_response(result.message)

    def _handle_ai_response(self, response: str) -> None:
        """Display and optionally speak the AI response."""
        self._append_display("HI ROLEX", response)
        self._set_status(f"{self.ai_manager.last_provider_used} response completed.")

        self._speak_ai_response(response)

    def _speak_ai_response(self, response: str) -> None:
        """Speak AI chat responses automatically when TTS is available."""
        if self.speech_manager is None:
            return

        speech_text = response.strip()
        if not speech_text:
            return

        threading.Thread(
            target=self.speech_manager.speak,
            args=(speech_text[:700],),
            daemon=True,
        ).start()

    def _show_confirmation_controls(self) -> None:
        """Show Confirm and Cancel buttons."""
        if self.confirm_button is not None:
            self.confirm_button.grid()
        if self.cancel_button is not None:
            self.cancel_button.grid()

    def _hide_confirmation_controls(self) -> None:
        """Hide Confirm and Cancel buttons."""
        if self.confirm_button is not None:
            self.confirm_button.grid_remove()
        if self.cancel_button is not None:
            self.cancel_button.grid_remove()

    def _get_input_text(self) -> str:
        """Return trimmed text from the user input box."""
        if self.input_box is None:
            return ""
        return self.input_box.get("1.0", "end").strip()

    def _clear_input(self) -> None:
        """Clear the user input box."""
        if self.input_box is not None:
            self.input_box.delete("1.0", "end")

    def _append_display(self, sender: str, message: str) -> None:
        """Append a message to the chat display."""
        if self.chat_display is None:
            return

        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"\n{sender}\n")
        self.chat_display.insert("end", f"{message}\n")
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")

    def _set_status(self, message: str) -> None:
        """Update the chat status label."""
        if self.status_label is not None:
            self.status_label.configure(text=message)

    def _status_text(self) -> str:
        """Return current AI mode status."""
        mode = self.ai_manager.get_ai_mode()
        if mode == "Online":
            return "Online AI mode. Gemini will answer when available."
        if mode == "Offline":
            return f"Offline AI mode. Ollama model: {self.ai_manager.offline_ai.get_model()}."
        return "Hybrid Mode. Online AI first, Offline AI fallback."

    def _completion_status(
        self,
        message: str,
        elapsed_seconds: float | None,
    ) -> str:
        """Return a status message with optional response timing."""
        if elapsed_seconds is None:
            return message
        return f"{message} in {elapsed_seconds:.1f}s."

"""Memory management window for HI ROLEX."""

from __future__ import annotations

from tkinter import messagebox

import customtkinter as ctk

from memory.memory_manager import MemoryManager
from memory.profile_manager import ProfileManager


class MemoryWindow(ctk.CTkToplevel):
    """CustomTkinter window for safe local memory management."""

    WINDOW_WIDTH: int = 860
    WINDOW_HEIGHT: int = 660

    def __init__(self, master: ctk.CTk) -> None:
        super().__init__(master)
        self.memory_manager = MemoryManager()
        self.profile_manager = ProfileManager()

        self.memory_display: ctk.CTkTextbox | None = None
        self.search_entry: ctk.CTkEntry | None = None
        self.category_entry: ctk.CTkEntry | None = None
        self.key_entry: ctk.CTkEntry | None = None
        self.value_entry: ctk.CTkEntry | None = None
        self.delete_id_entry: ctk.CTkEntry | None = None
        self.profile_entries: dict[str, ctk.CTkEntry] = {}
        self.status_label: ctk.CTkLabel | None = None

        self._configure_window()
        self.create_layout()
        self.refresh_memories()
        self.load_profile()

    def _configure_window(self) -> None:
        """Configure the Memory window."""
        self.title("HI ROLEX Memory")
        self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.minsize(760, 560)
        self.resizable(True, True)
        self._center_window()
        self.transient(self.master)
        self.focus()

    def _center_window(self) -> None:
        """Center the Memory window on screen."""
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_position = int((screen_width - self.WINDOW_WIDTH) / 2)
        y_position = int((screen_height - self.WINDOW_HEIGHT) / 2)
        self.geometry(
            f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}+{x_position}+{y_position}"
        )

    def create_layout(self) -> None:
        """Create the complete Memory window layout."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(self, corner_radius=0, fg_color="#111827")
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header,
            text="HI ROLEX Memory",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#F9FAFB",
        )
        title.grid(row=0, column=0, padx=24, pady=18, sticky="w")

        self.create_memory_controls()
        self.create_memory_display()
        self.create_profile_section()

        self.status_label = ctk.CTkLabel(self, text="Memory ready.", text_color="#D1D5DB")
        self.status_label.grid(row=4, column=0, padx=24, pady=(0, 16), sticky="w")

    def create_memory_controls(self) -> None:
        """Create search, add, delete, refresh, and clear controls."""
        controls = ctk.CTkFrame(self, fg_color="#111827", corner_radius=8)
        controls.grid(row=1, column=0, padx=24, pady=(18, 12), sticky="ew")
        controls.grid_columnconfigure((1, 3, 5), weight=1)

        self.search_entry = ctk.CTkEntry(controls, placeholder_text="Search memories")
        self.search_entry.grid(row=0, column=0, columnspan=2, padx=10, pady=8, sticky="ew")
        ctk.CTkButton(controls, text="Search", command=self.search_memories).grid(
            row=0,
            column=2,
            padx=6,
            pady=8,
            sticky="ew",
        )
        ctk.CTkButton(controls, text="Refresh", command=self.refresh_memories).grid(
            row=0,
            column=3,
            padx=6,
            pady=8,
            sticky="ew",
        )

        self.category_entry = ctk.CTkEntry(controls, placeholder_text="Category")
        self.category_entry.grid(row=1, column=0, padx=10, pady=8, sticky="ew")
        self.key_entry = ctk.CTkEntry(controls, placeholder_text="Key")
        self.key_entry.grid(row=1, column=1, padx=6, pady=8, sticky="ew")
        self.value_entry = ctk.CTkEntry(controls, placeholder_text="Value")
        self.value_entry.grid(row=1, column=2, columnspan=2, padx=6, pady=8, sticky="ew")
        ctk.CTkButton(controls, text="Add Memory", command=self.add_memory).grid(
            row=1,
            column=4,
            padx=6,
            pady=8,
            sticky="ew",
        )

        self.delete_id_entry = ctk.CTkEntry(controls, placeholder_text="Memory ID")
        self.delete_id_entry.grid(row=2, column=0, padx=10, pady=8, sticky="ew")
        ctk.CTkButton(
            controls,
            text="Delete Selected",
            command=self.delete_selected_memory,
            fg_color="#7F1D1D",
            hover_color="#991B1B",
        ).grid(row=2, column=1, padx=6, pady=8, sticky="ew")
        ctk.CTkButton(
            controls,
            text="Clear All Memories",
            command=self.clear_all_memories,
            fg_color="#7F1D1D",
            hover_color="#991B1B",
        ).grid(row=2, column=2, columnspan=2, padx=6, pady=8, sticky="ew")

    def create_memory_display(self) -> None:
        """Create the memory list display."""
        self.memory_display = ctk.CTkTextbox(self, wrap="word", fg_color="#0B1120")
        self.memory_display.grid(row=2, column=0, padx=24, pady=(0, 12), sticky="nsew")
        self.memory_display.configure(state="disabled")

    def create_profile_section(self) -> None:
        """Create profile editing controls."""
        profile_frame = ctk.CTkFrame(self, fg_color="#111827", corner_radius=8)
        profile_frame.grid(row=3, column=0, padx=24, pady=(0, 12), sticky="ew")
        profile_frame.grid_columnconfigure((1, 3), weight=1)

        fields = [
            ("display_name", "Display Name"),
            ("preferred_language", "Preferred Language"),
            ("preferred_voice", "Preferred Voice"),
            ("favorite_applications", "Favorite Applications"),
        ]
        for index, (key, label_text) in enumerate(fields):
            row = index // 2
            column = (index % 2) * 2
            ctk.CTkLabel(profile_frame, text=label_text).grid(
                row=row,
                column=column,
                padx=(12, 8),
                pady=8,
                sticky="w",
            )
            entry = ctk.CTkEntry(profile_frame)
            entry.grid(row=row, column=column + 1, padx=(0, 12), pady=8, sticky="ew")
            self.profile_entries[key] = entry

        ctk.CTkButton(profile_frame, text="Save Profile", command=self.save_profile).grid(
            row=2,
            column=0,
            columnspan=4,
            padx=12,
            pady=(4, 12),
            sticky="ew",
        )

    def refresh_memories(self) -> None:
        """Load all memories into the display."""
        self._display_memories(self.memory_manager.get_all_memories())
        self._set_status("Memories refreshed.")

    def search_memories(self) -> None:
        """Search saved memories."""
        query = self.search_entry.get().strip() if self.search_entry else ""
        if not query:
            self.refresh_memories()
            return
        self._display_memories(self.memory_manager.search_memories(query))
        self._set_status(f"Search complete for: {query}")

    def add_memory(self) -> None:
        """Add one memory from the form."""
        category = self.category_entry.get().strip() if self.category_entry else ""
        key = self.key_entry.get().strip() if self.key_entry else ""
        value = self.value_entry.get().strip() if self.value_entry else ""
        if not category or not key or not value:
            self._set_status("Category, key, and value are required.")
            return

        if self.memory_manager.add_memory(category, key, value):
            self._set_status("Memory saved.")
            self.refresh_memories()
            return
        self._set_status("Memory was not saved. It may contain sensitive information.")

    def delete_selected_memory(self) -> None:
        """Delete one selected memory after confirmation."""
        raw_id = self.delete_id_entry.get().strip() if self.delete_id_entry else ""
        if not raw_id.isdigit():
            self._set_status("Enter a valid Memory ID.")
            return

        confirmed = messagebox.askyesno(
            "Confirm Delete",
            f"Delete memory ID {raw_id}?",
            parent=self,
        )
        if not confirmed:
            self._set_status("Delete cancelled.")
            return

        if self.memory_manager.delete_memory(int(raw_id)):
            self._set_status("Memory deleted.")
            self.refresh_memories()
            return
        self._set_status("Memory could not be deleted.")

    def clear_all_memories(self) -> None:
        """Clear all long-term memories after strong confirmation."""
        confirmed = messagebox.askyesno(
            "Strong Confirmation",
            "This will delete ALL saved long-term memories. Continue?",
            parent=self,
        )
        if not confirmed:
            self._set_status("Clear all cancelled.")
            return

        if self.memory_manager.clear_memories():
            self._set_status("All memories cleared.")
            self.refresh_memories()
            return
        self._set_status("Could not clear memories.")

    def load_profile(self) -> None:
        """Load profile values into the form."""
        profile = self.profile_manager.get_profile()
        for key, entry in self.profile_entries.items():
            entry.delete(0, "end")
            entry.insert(0, profile.get(key, ""))

    def save_profile(self) -> None:
        """Save profile form values."""
        saved_all = True
        for key, entry in self.profile_entries.items():
            value = entry.get().strip()
            if value:
                saved_all = self.profile_manager.set_profile_value(key, value) and saved_all

        self._set_status("Profile saved." if saved_all else "Some profile values were not saved.")

    def _display_memories(self, memories: list[object]) -> None:
        """Render memories in the display textbox."""
        if self.memory_display is None:
            return

        self.memory_display.configure(state="normal")
        self.memory_display.delete("1.0", "end")
        if not memories:
            self.memory_display.insert("1.0", "No saved memories.")
        else:
            lines = [
                f"ID {memory.memory_id} | {memory.category} | {memory.key}: "
                f"{memory.value} ({memory.created_at})"
                for memory in memories
            ]
            self.memory_display.insert("1.0", "\n".join(lines))
        self.memory_display.configure(state="disabled")

    def _set_status(self, message: str) -> None:
        """Update the Memory window status label."""
        if self.status_label is not None:
            self.status_label.configure(text=message)

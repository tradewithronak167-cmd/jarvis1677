"""File Manager window for HI ROLEX."""

from __future__ import annotations

from collections.abc import Callable
from tkinter import messagebox

import customtkinter as ctk

from automation.favorites import FavoritesManager
from automation.file_manager import FileManager
from automation.file_search import FileSearch
from automation.operation_history import OperationHistory


class FileManagerWindow(ctk.CTkToplevel):
    """Desktop window for local Windows file management."""

    WINDOW_WIDTH: int = 780
    WINDOW_HEIGHT: int = 560

    def __init__(self, master: ctk.CTk) -> None:
        super().__init__(master)
        self.file_manager = FileManager()
        self.file_search = FileSearch()
        self.favorites_manager = FavoritesManager()
        self.operation_history = OperationHistory()

        self.path_entry: ctk.CTkEntry | None = None
        self.destination_entry: ctk.CTkEntry | None = None
        self.output_textbox: ctk.CTkTextbox | None = None

        self._configure_window()
        self.create_layout()

    def _configure_window(self) -> None:
        """Configure window title, size, and behavior."""
        self.title("HI ROLEX File Manager")
        self.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.minsize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.resizable(True, True)
        self._center_window()
        self.transient(self.master)
        self.focus()

    def _center_window(self) -> None:
        """Center the File Manager window on screen."""
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_position = int((screen_width - self.WINDOW_WIDTH) / 2)
        y_position = int((screen_height - self.WINDOW_HEIGHT) / 2)
        self.geometry(
            f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}+{x_position}+{y_position}"
        )

    def create_layout(self) -> None:
        """Build the File Manager controls."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        title_label = ctk.CTkLabel(
            self,
            text="File Manager",
            font=ctk.CTkFont(size=26, weight="bold"),
        )
        title_label.grid(row=0, column=0, padx=24, pady=(20, 12), sticky="w")

        input_frame = ctk.CTkFrame(self)
        input_frame.grid(row=1, column=0, padx=24, pady=(0, 12), sticky="ew")
        input_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(input_frame, text="Path").grid(
            row=0,
            column=0,
            padx=(14, 10),
            pady=10,
            sticky="w",
        )
        self.path_entry = ctk.CTkEntry(input_frame, placeholder_text="Example: Projects or notes.txt")
        self.path_entry.grid(row=0, column=1, padx=(0, 14), pady=10, sticky="ew")

        ctk.CTkLabel(input_frame, text="Destination / Pattern").grid(
            row=1,
            column=0,
            padx=(14, 10),
            pady=10,
            sticky="w",
        )
        self.destination_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Example: final_report.txt or .txt",
        )
        self.destination_entry.grid(row=1, column=1, padx=(0, 14), pady=10, sticky="ew")

        self.create_buttons()

        self.output_textbox = ctk.CTkTextbox(self, wrap="word")
        self.output_textbox.grid(row=3, column=0, padx=24, pady=(0, 24), sticky="nsew")
        self._set_output("File Manager ready.")

    def create_buttons(self) -> None:
        """Create File Manager action buttons."""
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=2, column=0, padx=24, pady=(0, 14), sticky="ew")
        button_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        buttons: list[tuple[str, Callable[[], None]]] = [
            ("Create File", self.create_file),
            ("Create Folder", self.create_folder),
            ("Rename", self.rename),
            ("Copy", self.copy),
            ("Move", self.move),
            ("Delete", self.delete),
            ("Open", self.open_path),
            ("Search", self.search),
            ("Favorites", self.favorites),
            ("History", self.history),
        ]

        for index, (text, command) in enumerate(buttons):
            button = ctk.CTkButton(
                button_frame,
                text=text,
                command=command,
                height=38,
                font=ctk.CTkFont(size=13, weight="bold"),
            )
            button.grid(row=index // 5, column=index % 5, padx=5, pady=5, sticky="ew")

    def create_file(self) -> None:
        """Create a file from the path entry."""
        self._run_operation("Create File", self.file_manager.create_file(self._path()))

    def create_folder(self) -> None:
        """Create a folder from the path entry."""
        self._run_operation("Create Folder", self.file_manager.create_folder(self._path()))

    def rename(self) -> None:
        """Rename a file or folder."""
        self._run_operation(
            "Rename",
            self.file_manager.rename(self._path(), self._destination()),
        )

    def copy(self) -> None:
        """Copy a file or folder."""
        self._run_operation("Copy", self.file_manager.copy(self._path(), self._destination()))

    def move(self) -> None:
        """Move a file or folder."""
        self._run_operation("Move", self.file_manager.move(self._path(), self._destination()))

    def delete(self) -> None:
        """Delete a file or folder only after confirmation."""
        path = self._path()
        if not path:
            self._set_output("Please enter a file or folder path.")
            return

        confirmed = messagebox.askyesno(
            "Confirm Delete",
            f"Do you want to delete this path?\n\n{path}",
            parent=self,
        )
        if not confirmed:
            self._set_output("Delete cancelled.")
            return

        if self.file_manager.exists(path):
            file_result = self.file_manager.delete_file(path)
            if file_result[0] or "File not found" not in file_result[1]:
                self._run_operation("Delete", file_result)
                return
            self._run_operation("Delete", self.file_manager.delete_folder(path))
            return

        self._set_output(f"Path not found: {path}")

    def open_path(self) -> None:
        """Open a file or folder."""
        path = self._path()
        file_result = self.file_manager.open_file(path)
        if file_result[0] or "File not found" not in file_result[1]:
            self._run_operation("Open", file_result)
            return
        self._run_operation("Open", self.file_manager.open_folder(path))

    def search(self) -> None:
        """Search by name, extension, or recent files."""
        folder = self._path() or "."
        pattern = self._destination()
        if not pattern:
            results = self.file_search.search_recent(folder)
        elif pattern.startswith("."):
            results = self.file_search.search_by_extension(folder, pattern)
        else:
            results = self.file_search.search_by_name(folder, pattern)

        self._set_output(self._format_results("Search Results", results))

    def favorites(self) -> None:
        """Add the current path to favorites or display favorites."""
        path = self._path()
        if path:
            success, result = self.favorites_manager.add_favorite(path)
            self._set_output(("Success: " if success else "Error: ") + result)
            return

        self._set_output(
            self._format_results("Favorites", self.favorites_manager.get_favorites())
        )

    def history(self) -> None:
        """Display saved file-operation history."""
        history = self.operation_history.get_history()
        lines = [
            f"{item['timestamp']} - {item['operation']} - {item['result']}"
            for item in history
        ]
        self._set_output(self._format_results("History", lines))

    def _run_operation(self, operation: str, result: tuple[bool, str]) -> None:
        """Display and save the result of a file operation."""
        success, message = result
        self.operation_history.add_operation(operation, message)
        self._set_output(("Success: " if success else "Error: ") + message)

    def _path(self) -> str:
        """Return the primary path entry value."""
        if self.path_entry is None:
            return ""
        return self.path_entry.get().strip()

    def _destination(self) -> str:
        """Return the destination or search pattern entry value."""
        if self.destination_entry is None:
            return ""
        return self.destination_entry.get().strip()

    def _format_results(self, title: str, results: list[str]) -> str:
        """Format result lists for the output textbox."""
        if not results:
            return f"{title}:\nNo results."
        return f"{title}:\n" + "\n".join(results)

    def _set_output(self, text: str) -> None:
        """Write text to the output area."""
        if self.output_textbox is None:
            return

        self.output_textbox.configure(state="normal")
        self.output_textbox.delete("1.0", "end")
        self.output_textbox.insert("1.0", text)
        self.output_textbox.configure(state="disabled")

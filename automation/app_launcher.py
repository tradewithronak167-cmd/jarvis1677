"""Windows application launcher for HI ROLEX."""

from __future__ import annotations

import os
from pathlib import Path
import re
import shutil
import subprocess
import time
from dataclasses import dataclass

try:
    import winreg
except ImportError:  # pragma: no cover - Windows project, kept for safe imports.
    winreg = None


@dataclass(frozen=True)
class AppDefinition:
    """Windows launch and close configuration for an application."""

    launch_commands: list[list[str]]
    process_names: list[str]


class AppLauncher:
    """Launches Windows applications through known and discovered sources."""

    APPLICATIONS: dict[str, AppDefinition] = {
        "chrome": AppDefinition(
            [
                ["chrome.exe"],
                ["cmd", "/c", "start", "", "chrome"],
            ],
            ["chrome.exe"],
        ),
        "vscode": AppDefinition(
            [
                ["code.cmd"],
                ["code"],
                ["Code.exe"],
            ],
            ["Code.exe"],
        ),
        "notepad": AppDefinition([["notepad.exe"]], ["notepad.exe"]),
        "calculator": AppDefinition(
            [
                ["calc.exe"],
                [
                    "explorer.exe",
                    "shell:AppsFolder\\Microsoft.WindowsCalculator_8wekyb3d8bbwe!App",
                ],
            ],
            ["CalculatorApp.exe", "calc.exe"],
        ),
        "paint": AppDefinition([["mspaint.exe"]], ["mspaint.exe"]),
        "command prompt": AppDefinition(
            [["cmd", "/c", "start", "", "cmd.exe"]],
            ["cmd.exe"],
        ),
        "powershell": AppDefinition(
            [
                ["powershell.exe"],
                ["pwsh.exe"],
                ["cmd", "/c", "start", "", "powershell.exe"],
            ],
            ["powershell.exe", "pwsh.exe"],
        ),
        "file explorer": AppDefinition([["explorer.exe"]], ["explorer.exe"]),
        "task manager": AppDefinition([["taskmgr.exe"]], ["Taskmgr.exe"]),
        "settings": AppDefinition(
            [["cmd", "/c", "start", "", "ms-settings:"]],
            ["SystemSettings.exe"],
        ),
        "control panel": AppDefinition([["control.exe"]], ["control.exe"]),
        "device manager": AppDefinition(
            [["mmc.exe", "devmgmt.msc"], ["devmgmt.msc"]],
            ["mmc.exe"],
        ),
        "system information": AppDefinition([["msinfo32.exe"]], ["msinfo32.exe"]),
        "resource monitor": AppDefinition([["resmon.exe"]], ["resmon.exe"]),
        "performance monitor": AppDefinition(
            [["perfmon.exe"]],
            ["perfmon.exe", "mmc.exe"],
        ),
        "event viewer": AppDefinition(
            [["eventvwr.exe"], ["mmc.exe", "eventvwr.msc"]],
            ["eventvwr.exe", "mmc.exe"],
        ),
    }
    BLOCKED_GENERIC_APPS: tuple[str, ...] = (
        "regedit",
        "registry editor",
        "registry",
        "bios",
        "uefi",
        "format",
        "diskpart",
        "cmd command",
        "powershell command",
    )

    def open_application(self, name: str) -> tuple[bool, str]:
        """Open a Windows application by known name or installed app shortcut."""
        normalized_name = self._normalize_app_name(name)
        app = self.APPLICATIONS.get(normalized_name)
        if app is None:
            return self._open_installed_application(name)

        launch_errors: list[str] = []
        for command in self._candidate_commands(normalized_name, app):
            try:
                subprocess.Popen(command)
                if self._wait_for_any_process(app.process_names):
                    return True, f"Opened {normalized_name}."
                return True, f"Launch requested for {normalized_name}."
            except FileNotFoundError:
                launch_errors.append(f"not found: {command[0]}")
            except Exception as error:
                launch_errors.append(str(error))

        details = "; ".join(dict.fromkeys(launch_errors))
        return False, details or f"Application unavailable: {normalized_name}"

    def close_application(self, name: str) -> tuple[bool, str]:
        """Close a known Windows application by process name."""
        normalized_name = self._normalize_app_name(name)
        if normalized_name == "file explorer":
            return False, "Closing File Explorer is not supported for safety."

        app = self.APPLICATIONS.get(normalized_name)
        if app is None:
            return False, f"Closing unknown apps is not supported yet: {name}"

        results: list[str] = []
        closed_any = False
        for process_name in app.process_names:
            try:
                completed_process = subprocess.run(
                    ["taskkill", "/IM", process_name, "/F"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
            except Exception as error:
                results.append(str(error))
                continue

            if completed_process.returncode == 0:
                closed_any = True
            output = completed_process.stdout.strip() or completed_process.stderr.strip()
            if output:
                results.append(output)

        if closed_any:
            return True, f"Closed {normalized_name}."

        detail = " ".join(results).strip()
        return False, detail or f"{normalized_name} is not running."

    def _open_installed_application(self, name: str) -> tuple[bool, str]:
        """Try to open an installed Windows app that is not in the known list."""
        normalized_name = self._normalize_app_name(name)
        if not normalized_name:
            return False, "Please include an app name."
        if self._is_blocked_generic_app(normalized_name):
            return False, "I cannot open that system tool safely."

        shortcut = self._find_start_menu_shortcut(normalized_name)
        if shortcut is not None:
            try:
                os.startfile(shortcut)  # type: ignore[attr-defined]
                return True, f"Launch requested for {shortcut.stem}."
            except Exception as error:
                return False, f"Could not open {shortcut.stem}: {error}"

        app_path = self._find_registered_app_path(normalized_name)
        if app_path is not None:
            try:
                subprocess.Popen([str(app_path)])
                return True, f"Launch requested for {app_path.stem}."
            except Exception as error:
                return False, f"Could not open {app_path.stem}: {error}"

        for command in self._generic_launch_commands(normalized_name):
            try:
                subprocess.Popen(command)
                return True, f"Launch requested for {name}."
            except Exception:
                continue

        return False, f"I could not find an installed app named {name}."

    def _candidate_commands(
        self,
        name: str,
        app: AppDefinition,
    ) -> list[list[str]]:
        """Return launch commands plus common Windows install paths."""
        commands = [*app.launch_commands]
        if name == "chrome":
            commands.extend(self._existing_path_commands(self._chrome_paths()))
        elif name == "vscode":
            commands.extend(self._existing_path_commands(self._vscode_paths()))
        return self._dedupe_commands(commands)

    def _wait_for_any_process(self, process_names: list[str]) -> bool:
        """Briefly wait for one expected process to appear."""
        for _ in range(8):
            if any(self._is_process_running(process_name) for process_name in process_names):
                return True
            time.sleep(0.25)
        return False

    def _is_process_running(self, process_name: str) -> bool:
        """Return True when a process appears in the Windows task list."""
        try:
            completed_process = subprocess.run(
                ["tasklist", "/FI", f"IMAGENAME eq {process_name}"],
                capture_output=True,
                text=True,
                check=False,
            )
        except Exception:
            return False
        return process_name.casefold() in completed_process.stdout.casefold()

    def _existing_path_commands(self, paths: list[Path]) -> list[list[str]]:
        """Return executable paths that exist on this machine."""
        return [[str(path)] for path in paths if path.exists()]

    def _chrome_paths(self) -> list[Path]:
        """Return common Google Chrome install paths."""
        return [
            Path(os.environ.get("ProgramFiles", "")) / "Google/Chrome/Application/chrome.exe",
            Path(os.environ.get("ProgramFiles(x86)", ""))
            / "Google/Chrome/Application/chrome.exe",
            Path(os.environ.get("LOCALAPPDATA", ""))
            / "Google/Chrome/Application/chrome.exe",
        ]

    def _vscode_paths(self) -> list[Path]:
        """Return common Visual Studio Code install paths."""
        return [
            Path(os.environ.get("LOCALAPPDATA", ""))
            / "Programs/Microsoft VS Code/Code.exe",
            Path(os.environ.get("ProgramFiles", "")) / "Microsoft VS Code/Code.exe",
        ]

    def _dedupe_commands(self, commands: list[list[str]]) -> list[list[str]]:
        """Remove duplicate commands while preserving order."""
        unique_commands: list[list[str]] = []
        seen: set[tuple[str, ...]] = set()
        for command in commands:
            if self._command_available(command):
                key = tuple(command)
                if key not in seen:
                    seen.add(key)
                    unique_commands.append(command)
        return unique_commands

    def _command_available(self, command: list[str]) -> bool:
        """Return True when a command can plausibly launch."""
        if not command:
            return False
        executable = command[0]
        if executable.lower() in {"cmd", "cmd.exe", "explorer.exe", "calc.exe"}:
            return True
        if Path(executable).exists():
            return True
        return shutil.which(executable) is not None

    def _find_start_menu_shortcut(self, normalized_name: str) -> Path | None:
        """Find the best Start Menu shortcut for an installed app name."""
        shortcuts = self._start_menu_shortcuts()
        exact_matches = [
            shortcut for shortcut in shortcuts
            if self._normalize_app_name(shortcut.stem) == normalized_name
        ]
        if exact_matches:
            return exact_matches[0]

        compact_target = self._compact_name(normalized_name)
        contains_matches = [
            shortcut for shortcut in shortcuts
            if compact_target in self._compact_name(shortcut.stem)
        ]
        if contains_matches:
            return sorted(contains_matches, key=lambda path: len(path.stem))[0]
        return None

    def _start_menu_shortcuts(self) -> list[Path]:
        """Return Start Menu shortcuts visible to the current Windows user."""
        roots = [
            Path(os.environ.get("APPDATA", ""))
            / "Microsoft/Windows/Start Menu/Programs",
            Path(os.environ.get("ProgramData", ""))
            / "Microsoft/Windows/Start Menu/Programs",
        ]
        shortcut_paths: list[Path] = []
        for root in roots:
            if not root.exists():
                continue
            for extension in ("*.lnk", "*.url", "*.appref-ms"):
                shortcut_paths.extend(root.rglob(extension))
        return shortcut_paths

    def _find_registered_app_path(self, normalized_name: str) -> Path | None:
        """Find registered executable paths from Windows App Paths registry keys."""
        if winreg is None:
            return None

        executable_names = self._possible_executable_names(normalized_name)
        registry_roots = (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE)
        for root in registry_roots:
            for executable_name in executable_names:
                sub_key = f"Software\\Microsoft\\Windows\\CurrentVersion\\App Paths\\{executable_name}"
                try:
                    with winreg.OpenKey(root, sub_key) as key:
                        value, _ = winreg.QueryValueEx(key, "")
                except OSError:
                    continue
                path = Path(str(value).strip('"'))
                if path.exists():
                    return path
        return None

    def _generic_launch_commands(self, normalized_name: str) -> list[list[str]]:
        """Build safe generic commands for apps available on PATH or via shell."""
        commands: list[list[str]] = []
        for executable_name in self._possible_executable_names(normalized_name):
            resolved = shutil.which(executable_name)
            if resolved is not None:
                commands.append([resolved])
        return self._dedupe_generic_commands(commands)

    def _possible_executable_names(self, normalized_name: str) -> list[str]:
        """Create common executable filename variants from a spoken app name."""
        candidates = {
            normalized_name,
            normalized_name.replace(" ", ""),
            normalized_name.replace(" ", "-"),
        }
        names: list[str] = []
        for candidate in candidates:
            if not re.fullmatch(r"[a-z0-9_. -]+", candidate):
                continue
            names.append(candidate if candidate.endswith(".exe") else f"{candidate}.exe")
        return names

    def _dedupe_generic_commands(self, commands: list[list[str]]) -> list[list[str]]:
        """Remove duplicate generic commands without requiring PATH validation."""
        unique_commands: list[list[str]] = []
        seen: set[tuple[str, ...]] = set()
        for command in commands:
            key = tuple(command)
            if key not in seen:
                seen.add(key)
                unique_commands.append(command)
        return unique_commands

    def _is_blocked_generic_app(self, normalized_name: str) -> bool:
        """Return True for high-risk tools that should not be opened generically."""
        return any(term in normalized_name for term in self.BLOCKED_GENERIC_APPS)

    def _normalize_app_name(self, name: str) -> str:
        """Normalize an app name while preserving human-readable words."""
        return " ".join(name.casefold().strip().split())

    def _compact_name(self, name: str) -> str:
        """Create a punctuation-free comparison key for app names."""
        return re.sub(r"[^a-z0-9]+", "", name.casefold())

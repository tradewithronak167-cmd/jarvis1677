"""Windows application launcher for HI ROLEX."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class AppDefinition:
    """Windows launch and close configuration for an application."""

    launch_commands: list[list[str]]
    process_names: list[str]


class AppLauncher:
    """Launches and closes known Windows applications."""

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
    }

    def open_application(self, name: str) -> tuple[bool, str]:
        """Open a known Windows application."""
        app = self.APPLICATIONS.get(name)
        if app is None:
            return False, f"Application not supported: {name}"

        launch_errors: list[str] = []
        for command in self._candidate_commands(name, app):
            try:
                subprocess.Popen(command)
                if self._wait_for_any_process(app.process_names):
                    return True, f"Opened {name}."
                return True, f"Launch requested for {name}."
            except FileNotFoundError:
                launch_errors.append(f"not found: {command[0]}")
            except Exception as error:
                launch_errors.append(str(error))

        details = "; ".join(dict.fromkeys(launch_errors))
        return False, details or f"Application unavailable: {name}"

    def close_application(self, name: str) -> tuple[bool, str]:
        """Close a known Windows application by process name."""
        if name == "file explorer":
            return False, "Closing File Explorer is not supported for safety."

        app = self.APPLICATIONS.get(name)
        if app is None:
            return False, f"Application not supported: {name}"

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
            return True, f"Closed {name}."

        detail = " ".join(results).strip()
        return False, detail or f"{name} is not running."

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

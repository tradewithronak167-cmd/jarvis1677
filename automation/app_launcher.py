"""Windows application launcher for HI ROLEX."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class AppDefinition:
    """Windows launch and close configuration for an application."""

    launch_command: list[str]
    process_names: list[str]


class AppLauncher:
    """Launches and closes known Windows applications."""

    APPLICATIONS: dict[str, AppDefinition] = {
        "chrome": AppDefinition(["cmd", "/c", "start", "", "chrome"], ["chrome.exe"]),
        "vscode": AppDefinition(["cmd", "/c", "start", "", "code"], ["Code.exe"]),
        "notepad": AppDefinition(["notepad"], ["notepad.exe"]),
        "calculator": AppDefinition(["calc"], ["CalculatorApp.exe", "calc.exe"]),
        "paint": AppDefinition(["mspaint"], ["mspaint.exe"]),
        "command prompt": AppDefinition(["cmd", "/c", "start", "", "cmd"], ["cmd.exe"]),
        "powershell": AppDefinition(
            ["cmd", "/c", "start", "", "powershell"],
            ["powershell.exe", "pwsh.exe"],
        ),
        "file explorer": AppDefinition(["explorer"], ["explorer.exe"]),
    }

    def open_application(self, name: str) -> tuple[bool, str]:
        """Open a known Windows application."""
        app = self.APPLICATIONS.get(name)
        if app is None:
            return False, f"Application not supported: {name}"

        try:
            subprocess.Popen(app.launch_command)
            return True, f"Opened {name}."
        except FileNotFoundError:
            return False, f"Application unavailable: {name}"
        except Exception as error:
            return False, f"Could not open {name}: {error}"

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

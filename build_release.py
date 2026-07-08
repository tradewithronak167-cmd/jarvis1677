"""Build a Windows release folder for HI ROLEX."""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
APP_ENTRY = PROJECT_ROOT / "app.py"
BUILD_DIR = PROJECT_ROOT / "build"
DIST_DIR = PROJECT_ROOT / "dist"
RELEASE_ROOT = PROJECT_ROOT / "release"
RELEASE_DIR = RELEASE_ROOT / "HI-ROLEX-v1.0"
EXECUTABLE_NAME = "HI ROLEX.exe"
APP_NAME = "HI ROLEX"
RUNTIME_FOLDERS = ("assets", "config", "language", "data")
SAFE_RELEASE_FILES = ("README.md", ".env.example")
DANGEROUS_FILES = (".env",)


def main() -> int:
    """Run the release build and return a process exit code."""
    print("HI ROLEX Release Builder")
    print("========================")

    rerun_code = _rerun_with_python_312_if_needed()
    if rerun_code is not None:
        return rerun_code

    if not _check_app_entry():
        return 1

    if not _check_pyinstaller():
        return 1

    _create_required_folders()

    if not _run_pyinstaller():
        return 1

    if not _prepare_release_folder():
        return 1

    print("\n[SUCCESS] Release build completed.")
    print(f"[OK] Release folder: {RELEASE_DIR}")
    print(f"[OK] Executable: {RELEASE_DIR / EXECUTABLE_NAME}")
    print("[OK] Real .env file was not copied.")
    return 0


def _rerun_with_python_312_if_needed() -> int | None:
    """Relaunch with Python 3.12 when the default python points elsewhere."""
    if sys.version_info[:2] == (3, 12):
        return None

    print(
        f"[WARN] Running on Python {sys.version_info.major}."
        f"{sys.version_info.minor}; packaging uses Python 3.12."
    )
    try:
        result = subprocess.run(
            ["py", "-3.12", str(Path(__file__).resolve())],
            cwd=PROJECT_ROOT,
            check=False,
        )
    except OSError as error:
        print(f"[ERROR] Could not launch Python 3.12 with py launcher: {error}")
        print("Run this command instead:")
        print("  py -3.12 build_release.py")
        return 1

    return result.returncode


def _check_app_entry() -> bool:
    """Check that app.py exists before packaging."""
    if APP_ENTRY.exists():
        print(f"[OK] Found app entry: {APP_ENTRY.name}")
        return True

    print("[ERROR] app.py was not found. Run this script from the project root.")
    return False


def _check_pyinstaller() -> bool:
    """Check whether PyInstaller is installed in the active Python."""
    if importlib.util.find_spec("PyInstaller") is not None:
        print("[OK] PyInstaller is installed.")
        return True

    print("[ERROR] PyInstaller is not installed for this Python environment.")
    print("Install it with:")
    print("  python -m pip install pyinstaller")
    return False


def _create_required_folders() -> None:
    """Create build, dist, release, and versioned release folders."""
    for folder in (BUILD_DIR, DIST_DIR, RELEASE_ROOT, RELEASE_DIR):
        folder.mkdir(parents=True, exist_ok=True)
    print("[OK] Build folders are ready.")


def _run_pyinstaller() -> bool:
    """Run PyInstaller with safe, explicit arguments."""
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--name",
        APP_NAME,
    ]

    for folder_name in RUNTIME_FOLDERS:
        folder = PROJECT_ROOT / folder_name
        if folder.exists():
            command.extend(["--add-data", _format_add_data(folder, folder_name)])
            print(f"[OK] Including runtime folder: {folder_name}")
        else:
            print(f"[WARN] Runtime folder missing, skipping: {folder_name}")

    icon_path = PROJECT_ROOT / "assets" / "icons" / "hi_rolex.ico"
    if icon_path.exists():
        command.extend(["--icon", str(icon_path)])
        print(f"[OK] Using icon: {icon_path}")
    else:
        print("[WARN] Icon missing, building without a custom icon.")

    command.append(str(APP_ENTRY))

    print("\n[INFO] Running PyInstaller...")
    result = subprocess.run(command, cwd=PROJECT_ROOT, check=False)
    if result.returncode == 0:
        print("[OK] PyInstaller finished successfully.")
        return True

    print(f"[ERROR] PyInstaller failed with exit code {result.returncode}.")
    return False


def _prepare_release_folder() -> bool:
    """Copy the built app and safe release files into release/HI-ROLEX-v1.0."""
    if RELEASE_DIR.exists():
        _safe_rmtree(RELEASE_DIR)
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)

    built_app_folder = DIST_DIR / APP_NAME
    built_exe = built_app_folder / EXECUTABLE_NAME
    one_file_exe = DIST_DIR / EXECUTABLE_NAME

    if built_app_folder.exists() and built_exe.exists():
        _copy_folder_contents(built_app_folder, RELEASE_DIR)
    elif one_file_exe.exists():
        shutil.copy2(one_file_exe, RELEASE_DIR / EXECUTABLE_NAME)
    else:
        print("[ERROR] Built executable was not found in dist/.")
        return False

    _copy_runtime_folders_for_easy_access()
    _copy_safe_release_files()
    _remove_dangerous_files()
    return True


def _copy_runtime_folders_for_easy_access() -> None:
    """Copy runtime folders beside the executable for editable settings/data."""
    for folder_name in RUNTIME_FOLDERS:
        source = PROJECT_ROOT / folder_name
        target = RELEASE_DIR / folder_name
        if source.exists() and not target.exists():
            shutil.copytree(source, target, ignore=_ignore_sensitive_runtime_files)
            print(f"[OK] Copied runtime folder to release: {folder_name}")


def _copy_safe_release_files() -> None:
    """Copy release documentation and templates, never secrets."""
    for filename in SAFE_RELEASE_FILES:
        source = PROJECT_ROOT / filename
        if source.exists():
            shutil.copy2(source, RELEASE_DIR / filename)
            print(f"[OK] Copied {filename}")
        else:
            print(f"[WARN] Optional release file missing: {filename}")


def _remove_dangerous_files() -> None:
    """Remove files that must never ship in the release folder."""
    for filename in DANGEROUS_FILES:
        for target in RELEASE_DIR.rglob(filename):
            if target.is_file():
                target.unlink()
                print(f"[OK] Removed unsafe file from release: {target.name}")

    for log_dir in RELEASE_DIR.rglob("logs"):
        if log_dir.is_dir():
            _safe_rmtree(log_dir)
            print(f"[OK] Removed logs folder from release: {log_dir}")

    for journal_file in RELEASE_DIR.rglob("*.db-journal"):
        if journal_file.is_file():
            journal_file.unlink()
            print(f"[OK] Removed database journal from release: {journal_file.name}")


def _format_add_data(source: Path, destination: str) -> str:
    """Format a PyInstaller --add-data argument for the current OS."""
    separator = ";" if os.name == "nt" else ":"
    return f"{source}{separator}{destination}"


def _copy_folder_contents(source: Path, destination: Path) -> None:
    """Copy all files from a PyInstaller onedir output into the release folder."""
    for item in source.iterdir():
        target = destination / item.name
        if item.is_dir():
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)


def _ignore_sensitive_runtime_files(folder: str, names: list[str]) -> set[str]:
    """Ignore secrets and transient files while copying runtime folders."""
    ignored = {".env", "hi_rolex.log"}
    ignored.update(name for name in names if name.endswith(".db-journal"))
    if Path(folder).name == "logs":
        ignored.update(names)
    return ignored


def _safe_rmtree(path: Path) -> None:
    """Remove only the expected versioned release directory."""
    resolved_release_root = RELEASE_ROOT.resolve()
    resolved_path = path.resolve()
    if resolved_path == resolved_release_root or resolved_release_root not in resolved_path.parents:
        raise RuntimeError(f"Refusing to remove unexpected path: {resolved_path}")
    shutil.rmtree(resolved_path)


if __name__ == "__main__":
    raise SystemExit(main())

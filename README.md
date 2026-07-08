# HI ROLEX

HI ROLEX is a Windows desktop AI assistant with online/offline AI, voice, automation, memory, and hardware tools. It is built with Python and CustomTkinter for Windows 11.

## Features

- Wake word: Hi Rolex
- Voice input and output
- Online Gemini AI
- Offline Ollama AI
- Hybrid mode
- App launcher
- Browser automation
- File manager
- Hardware dashboard
- Memory system
- Multi-language UI
- Smart command router

## Developer Installation

Use Python 3.12 for best Windows voice and hardware package support.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

If your default `python` command points to another Python version, use:

```powershell
py -3.12 app.py
```

## Environment Setup

Copy `.env.example` to `.env`, then add your Gemini key if you want Online AI.

```text
GEMINI_API_KEY=your_gemini_api_key_here
```

Never share `.env`, API keys, tokens, or secrets.

## Offline AI Setup

Install Ollama, then pull the default model:

```powershell
ollama pull qwen2.5:3b
```

Use `Offline` or `Hybrid` mode in HI ROLEX settings.

## Health Check

```powershell
python tools/health_check.py
```

## Tests

```powershell
pytest
```

Or:

```powershell
python -m pytest
```

## Build Executable

```powershell
python build_release.py
```

The release output is created at:

```text
release/HI-ROLEX-v1.0/
```

The executable is:

```text
release/HI-ROLEX-v1.0/HI ROLEX.exe
```

The release folder includes `README.md` and `.env.example`. It must never include the real `.env` file.

## Final Testing Checklist

After building, test:

1. Open `HI ROLEX.exe`.
2. Open Settings.
3. Open Chat.
4. Ask an online AI question.
5. Ask an offline AI question if Ollama is installed.
6. Test command: `open notepad`.
7. Test command: `search google for Python tutorials`.
8. Test memory: `remember my name is Rahul`.
9. Test the hardware window.
10. Test dangerous command: `format my drive`.

HI ROLEX should refuse dangerous commands.

## Safety Notes

HI ROLEX should not execute dangerous system commands without confirmation. It should not store passwords, API keys, access tokens, PINs, card numbers, banking details, private keys, or other sensitive secrets in memory or logs.

Dangerous commands remain blocked, including:

- format drive
- registry edit
- disable antivirus
- delete system files
- arbitrary terminal command execution

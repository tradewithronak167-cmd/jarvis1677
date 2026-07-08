# HI ROLEX

HI ROLEX is a Windows desktop AI assistant built with Python and CustomTkinter.

Current preview features include settings, language support, voice foundation, wake word, Windows automation, file management, hardware dashboard, Gemini online AI, Ollama offline AI, hybrid routing, local memory, and a smart command router.

## Requirements

- Windows 11
- Python 3.12+
- VS Code recommended

## Install

```powershell
pip install -r requirements.txt
```

Some hardware and voice features depend on optional Windows packages and device support. Missing optional packages should not stop the app from opening.

## Run

```powershell
python app.py
```

## Health Check

```powershell
python tools/health_check.py
```

The health check verifies project files, settings, language files, memory database, `.env`, Gemini key, Ollama server, important packages, and safety blocks.

## Tests

```powershell
pytest
```

The test suite uses safe temporary files and does not run destructive commands.

## Gemini Online AI

Create a `.env` file in the project root:

```text
GEMINI_API_KEY=your_real_key_here
```

Never share your API key or commit it to source control.

## Ollama Offline AI

Install Ollama, then pull the default model:

```powershell
ollama pull qwen2.5:3b
ollama run qwen2.5:3b
```

In HI ROLEX Settings, use:

```text
AI Mode: Offline or Hybrid
Offline Model: qwen2.5:3b
```

## Safety Notes

HI ROLEX blocks or requires confirmation for risky actions. It does not implement shutdown, restart, sleep, drive formatting, registry editing, BIOS control, antivirus disabling, arbitrary terminal commands, or unknown script execution.

Sensitive information such as passwords, API keys, tokens, PINs, card numbers, and private keys should not be stored in memory or logs.

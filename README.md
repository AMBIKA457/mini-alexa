# Jarvis — Mini Alexa Voice Assistant

A lightweight, beginner-friendly voice assistant with English and Hinglish command handling. Common tasks run locally through deterministic rules; an optional Anthropic-powered fallback handles open-ended questions.

> **Project status:** Learning project / early prototype. Review the security and privacy notes before exposing the web UI or using it with sensitive information.

## Features

- Voice input and text-based CLI mode
- Optional Streamlit chat interface
- Time and date responses
- Weather lookup using wttr.in
- Restricted arithmetic evaluator (no `eval` or `exec`)
- Local SQLite notes
- In-process reminders (not persistent across restarts)
- Allow-listed website opening
- Wikipedia summaries and optional AI fallback
- English/Hinglish-friendly responses

## Requirements

- Python 3.10+
- Microphone and audio drivers for voice mode
- Internet access for weather, Wikipedia, speech recognition, and optional AI

## Quick start

```bash
git clone https://github.com/AMBIKA457/mini-alexa.git
cd mini-alexa
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
source .venv/bin/activate
```

Install dependencies and configure environment:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and edit values as needed. AI fallback is disabled when `ANTHROPIC_API_KEY` is empty. Use a model ID currently supported by your Anthropic account.

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS / Linux:

```bash
cp .env.example .env
```

Run:

```bash
# Keyboard mode
python main.py --text

# Voice mode
python main.py

# Local web chat
streamlit run app_ui.py
```

## Tests

```bash
python -m pytest -q
```

GitHub Actions runs the test suite on pushes and pull requests to `main` with Python 3.10, 3.11, and 3.12.

## Security and privacy notes

- Keep API keys in `.env`; never commit secrets.
- `.env`, SQLite databases, and Python cache files are ignored by Git.
- Calculator input is parsed through a restricted AST evaluator.
- Website navigation uses a fixed allow-list.
- SQLite writes use parameterized SQL statements.
- HTTP requests use a timeout.
- Voice recognition uses Google's online recognition service; do not assume microphone audio stays on-device.
- Notes are stored locally without encryption. The Streamlit app has no authentication or per-user isolation; chat history and optional AI conversation history are process-wide. Use it only on a trusted local machine unless you add appropriate access controls.
- Reminders run in memory and are lost when the process exits.

See [SECURITY.md](SECURITY.md) for vulnerability reporting guidance.

## Roadmap

- Persistent, restart-safe reminders
- Hindi text-to-speech support
- Wake-word detection
- Authentication and multi-user data isolation for the web UI
- More intent tests and integration tests

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Contributions should include tests and must not contain secrets or personal data.

## License

MIT — see [LICENSE](LICENSE).

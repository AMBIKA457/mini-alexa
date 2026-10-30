"""Single entry point used by both the voice CLI and the web UI."""
from . import ai, commands


def respond(text: str) -> str:
    return commands.handle(text) or ai.ask(text)

"""Optional Claude fallback. Token-saving: small model, tiny max_tokens, short history."""
from collections import deque
from . import config

_history: deque = deque(maxlen=6)  # last 3 exchanges only
SYSTEM = "You are Jarvis, a friendly voice assistant. Reply in the user's language (Hinglish ok) in max 2 short sentences."
_client = None


def ask(text: str) -> str:
    global _client
    if not config.ANTHROPIC_API_KEY:
        return "Ye command samajh nahi aaya. 'help' bolo, ya AI mode ke liye .env me ANTHROPIC_API_KEY daalo."
    try:
        if _client is None:
            import anthropic
            _client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        _history.append({"role": "user", "content": text})
        resp = _client.messages.create(model=config.AI_MODEL, max_tokens=config.AI_MAX_TOKENS,
                                       system=SYSTEM, messages=list(_history))
        reply = resp.content[0].text.strip()
        _history.append({"role": "assistant", "content": reply})
        return reply
    except Exception:
        _history.clear()
        return "AI abhi available nahi hai. Thodi der baad try karo."

"""Rule-based commands (Hinglish + English). Zero AI tokens, zero shell access.

Security: only whitelisted websites open, math uses a safe AST evaluator,
no eval/exec/os.system anywhere.
"""
import ast
import operator
import random
import re
import threading
import webbrowser
from datetime import datetime
from urllib.parse import quote

import requests

from . import config, storage

SITES = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "github": "https://github.com",
    "gmail": "https://mail.google.com",
    "stackoverflow": "https://stackoverflow.com",
}
JOKES = [
    "Programmer ko chai kyun pasand hai? Kyunki usme Java hota hai.",
    "Computer ko thand kyun lagi? Kyunki uski Windows khuli thi.",
    "Bug aur feature me fark? Documentation me likh do to feature ban jata hai.",
]
HEADERS = {"User-Agent": "JarvisMiniAlexa/1.0 (student project)"}

_notify = print


def set_notifier(fn) -> None:
    """Reminders call this when they fire (voice mode passes speak())."""
    global _notify
    _notify = fn


# ---------- helpers ----------
_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.Mod: operator.mod, ast.USub: operator.neg}


def _safe_eval(node):
    """Evaluate a deliberately small arithmetic AST; never execute Python code."""
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        value = node.value
        if abs(value) > 10**12:
            raise ValueError("number too large")
        return value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        left, right = _safe_eval(node.left), _safe_eval(node.right)
        result = _OPS[type(node.op)](left, right)
        if not isinstance(result, (int, float)) or abs(result) > 10**12:
            raise ValueError("result out of range")
        return result
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        result = _OPS[type(node.op)](_safe_eval(node.operand))
        if abs(result) > 10**12:
            raise ValueError("result out of range")
        return result
    raise ValueError("unsafe expression")


# ---------- intents ----------
def calc(t: str) -> str:
    for word, sym in [("divided by", "/"), ("multiplied by", "*"), ("bhaag", "/"), ("gunaa", "*"),
                      ("times", "*"), ("into", "*"), ("plus", "+"), ("jod", "+"),
                      ("minus", "-"), ("ghata", "-")]:
        t = t.replace(word, f" {sym} ")
    # Remove the intent keyword, then reject unsupported characters rather
    # than silently stripping arbitrary input into a different expression.
    expr = re.sub(r"\bcalculate\b", " ", t, flags=re.IGNORECASE).strip()
    if len(expr) > 100 or not re.fullmatch(r"[\d.+\-*/()% ]+", expr):
        return "Calculation samajh nahi aayi. Sirf numbers aur +, -, *, /, % use karo."
    try:
        result = _safe_eval(ast.parse(expr, mode="eval"))
        return f"Jawab hai {round(result, 4):g}"
    except Exception:
        return "Calculation samajh nahi aayi. Jaise bolo: 'calculate 12 plus 8'."


def get_time(_t: str) -> str:
    return "Abhi samay hai " + datetime.now().strftime("%I:%M %p")


def get_date(_t: str) -> str:
    return "Aaj ki tareekh hai " + datetime.now().strftime("%A, %d %B %Y")


def open_site(t: str) -> str:
    for name, url in SITES.items():
        if re.search(rf"\b{re.escape(name)}\b", t):
            webbrowser.open(url)
            return f"{name.title()} khol raha hu."
    return "Ye website allowed list me nahi hai. Allowed: " + ", ".join(SITES)


def joke(_t: str) -> str:
    return random.choice(JOKES)


def weather(t: str) -> str:
    m = re.search(r"(?:in|at)\s+([a-z ]+)$", t) or re.search(r"([a-z ]+?)\s+(?:ka|ki)\s+(?:mausam|weather)", t)
    city = (m.group(1).strip() if m else config.DEFAULT_CITY) or config.DEFAULT_CITY
    try:
        r = requests.get(f"https://wttr.in/{quote(city)}", params={"format": "%C, %t, humidity %h"},
                         headers=HEADERS, timeout=config.HTTP_TIMEOUT)
        r.raise_for_status()
        return f"{city.title()} me abhi: {r.text.strip()}"
    except requests.RequestException:
        return "Weather abhi nahi mil paya. Internet check karo."


def wiki(t: str) -> str:
    topic = re.sub(r"\b(who is|what is|tell me about|wikipedia|kaun hai|kya hai|kaun|kya|ke bare me batao|batao)\b", " ", t)
    topic = " ".join(topic.split())
    if not topic:
        return "Kis topic ke bare me jaanna hai?"
    try:
        s = requests.get("https://en.wikipedia.org/w/api.php", headers=HEADERS, timeout=config.HTTP_TIMEOUT,
                         params={"action": "opensearch", "search": topic, "limit": 1, "format": "json"}).json()
        if not s[1]:
            return f"'{topic}' ke bare me kuch nahi mila."
        d = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(s[1][0])}",
                         headers=HEADERS, timeout=config.HTTP_TIMEOUT).json()
        return " ".join(d.get("extract", "").split(". ")[:2])[:400] or "Summary nahi mili."
    except (requests.RequestException, ValueError, IndexError):
        return "Wikipedia abhi reach nahi ho raha."


def notes(t: str) -> str:
    if any(k in t for k in ("clear", "delete", "saaf", "hata")):
        storage.clear_notes()
        return "Saare notes hata diye."
    if any(k in t for k in ("show", "list", "dikha", "padh", "mere notes", "my notes")):
        items = storage.list_notes()
        return "Tumhare notes: " + "; ".join(items) if items else "Abhi koi note nahi hai."
    m = re.search(r"(?:note(?:\s+(?:kar|karo|likho|that))?|yaad rakho(?:\s+ki)?)\s*[:,]?\s*(.+)", t)
    if m and m.group(1).strip():
        storage.add_note(m.group(1).strip())
        return "Note save ho gaya."
    return "Kya note karna hai?"


UNITS = {"sec": 1, "second": 1, "min": 60, "minute": 60, "hour": 3600, "ghante": 3600, "ghanta": 3600}


def remind(t: str) -> str:
    m = re.search(r"(\d+)\s*(second|sec|minute|min|hour|ghante|ghanta)", t)
    if not m:
        return "Kitne time baad? Jaise: '5 minute baad pani peena yaad dilana'."
    seconds = int(m.group(1)) * UNITS[m.group(2)]
    if not 1 <= seconds <= 86400:
        return "Reminder 1 second se 24 ghante ke beech hi set ho sakta hai."
    msg = t[:m.start()] + " " + t[m.end():]
    msg = re.sub(r"\b(remind me|reminder|yaad dilana|yaad dilao|yaad dila do|yaad dila|me|in|to|about|baad|ke|mujhe)\b", " ", msg)
    msg = " ".join(msg.split()) or "samay ho gaya"
    timer = threading.Timer(seconds, lambda: _notify(f"Reminder: {msg}"))
    timer.daemon = True
    timer.start()
    return f"Theek hai, {m.group(1)} {m.group(2)} baad yaad dilaunga: {msg}."


def help_text(_t: str) -> str:
    return ("Main ye kar sakta hu: time, date, weather, calculate, notes, reminder, "
            "website kholna (google/youtube/github), jokes, aur Wikipedia se jawab.")


# Order matters: first match wins.
INTENTS = [
    (("remind", "yaad dila", "reminder"), remind),
    (("note", "yaad rakho"), notes),
    (("calculate", "plus", "minus", "times", "divided", "multiplied", "gunaa", "bhaag", "jod", "ghata"), calc),
    (("weather", "mausam"), weather),
    (("time", "samay", "kitne baje"), get_time),
    (("date", "tareekh", "tarikh", "what day"), get_date),
    (("open", "kholo", "khol do"), open_site),
    (("joke", "chutkula", "hasao"), joke),
    (("help", "madad", "what can you do"), help_text),
    (("who is", "what is", "tell me about", "wikipedia", "kaun hai", "kya hai"), wiki),
]


def handle(text: str):
    """Return a reply string, or None if no rule matches (caller may fall back to AI)."""
    t = text.lower().strip()
    for keys, fn in INTENTS:
        if any(k in t for k in keys):
            return fn(t)
    return None

"""Voice I/O. Imports are lazy so the rest of the app works without audio drivers."""
import threading
from . import config

_lock = threading.Lock()
_engine = None


def speak(text: str) -> None:
    global _engine
    print(f"{config.NAME}: {text}")
    with _lock:
        try:
            if _engine is None:
                import pyttsx3
                _engine = pyttsx3.init()
                _engine.setProperty("rate", 170)
            _engine.say(text)
            _engine.runAndWait()
        except Exception:
            pass  # text is already printed; never crash on audio issues


def listen() -> str:
    """Listen once from the mic. Returns '' if nothing was understood."""
    import speech_recognition as sr
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            print("Sun raha hu...")
            audio = r.listen(source, timeout=6, phrase_time_limit=10)
        return r.recognize_google(audio, language=config.LANG)
    except (sr.WaitTimeoutError, sr.UnknownValueError):
        return ""
    except sr.RequestError:
        print("Speech service reach nahi hui (internet?).")
        return ""

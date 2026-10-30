"""Run: python main.py        (voice mode)
       python main.py --text (keyboard mode, handy when mic is unavailable)"""
import argparse
from assistant import brain, commands, config, speech

EXIT_WORDS = ("exit", "quit", "bye", "band karo", "ruko", "alvida")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", action="store_true", help="type instead of speaking")
    args = parser.parse_args()

    commands.set_notifier(speech.speak)
    speech.speak(f"Namaste, main {config.NAME} hu. Boliye, kya madad karu?")
    while True:
        text = input("You: ") if args.text else speech.listen()
        if not text:
            continue
        if not args.text:
            print(f"You: {text}")
        text = text.lower().replace(config.NAME.lower(), "", 1).strip()
        if any(w in text for w in EXIT_WORDS):
            speech.speak("Alvida! Phir milenge.")
            break
        speech.speak(brain.respond(text))


if __name__ == "__main__":
    main()

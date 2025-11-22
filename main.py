"""
Console entry point for the AI Therapist (educational).
"""

from core.therapist_engine import generate_reply
from core.storage import log_message
from core.safety import DISCLAIMER

INTRO = (
    "Hi, I'm an AI-based supportive chat assistant.\n"
    "I'm here to listen and help you explore your feelings.\n"
    f"{DISCLAIMER}\n\n"
    "Type 'exit' or 'quit' anytime to stop.\n"
)

def main():
    print("=" * 60)
    print("        AI Therapist (Educational Prototype)        ")
    print("=" * 60)
    print(INTRO)

    while True:
        user_text = input("You: ").strip()

        if user_text.lower() in {"exit", "quit"}:
            print("AI: Thank you for sharing with me today. Take care. ❤️")
            log_message("user", user_text)
            log_message("ai", "[Session ended]")
            break

        if not user_text:
            continue

        log_message("user", user_text)
        reply, is_crisis = generate_reply(user_text)
        print("\nAI:", reply, "\n")
        log_message("ai", reply)

if __name__ == "__main__":
    main()

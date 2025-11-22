"""
Safety and crisis detection utilities.
"""
from typing import Tuple

CRISIS_KEYWORDS = [
    "suicide", "kill myself", "end my life", "self harm", "self-harm",
    "cut myself", "no reason to live", "want to die", "give up on life"
]

DISCLAIMER = (
    "I am an AI program and **not a licensed therapist or doctor**.\n"
    "I can't diagnose, treat, or handle emergencies. "
    "If you're in crisis, please reach out to a trusted person or local emergency services."
)

def check_crisis(text: str) -> Tuple[bool, str]:
    """Return (is_crisis, crisis_message)."""
    lowered = text.lower()
    for kw in CRISIS_KEYWORDS:
        if kw in lowered:
            message = (
                "It sounds like you're going through something extremely painful.\n"
                "Your safety matters. Please reach out to someone you trust or a professional.\n\n"
                + DISCLAIMER
            )
            return True, message
    return False, ""

"""
Core logic for the AI therapist.

Phase 2.5+: Hybrid mood detection using ML-based sentiment (VADER)
+ rule-based fallback, with sentiment logging and friendlier replies.
"""

import random
from typing import Dict, Tuple
from pathlib import Path
import json

from .safety import check_crisis, DISCLAIMER
from .storage import log_message, log_sentiment
from .sentiment import analyze_sentiment

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
COPING_FILE = DATA_DIR / "coping_strategies.json"


def load_coping_strategies() -> Dict[str, list]:
    if COPING_FILE.exists():
        with open(COPING_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


COPING_STRATEGIES = load_coping_strategies()

# Fallback lexicon-based mood detection (Phase 1).
NEGATIVE_WORDS = [
    "sad",
    "down",
    "depressed",
    "anxious",
    "anxiety",
    "stressed",
    "overwhelmed",
    "lonely",
    "tired",
    "burned out",
    "worthless",
]

POSITIVE_WORDS = [
    "happy",
    "excited",
    "grateful",
    "hopeful",
    "good",
    "okay",
]


def detect_mood_rule_based(text: str) -> str:
    """
    Original Phase 1 rule-based mood detector.
    Used as a backup if ML sentiment is not available.
    """
    text_l = text.lower()
    neg_hits = sum(1 for w in NEGATIVE_WORDS if w in text_l)
    pos_hits = sum(1 for w in POSITIVE_WORDS if w in text_l)

    if neg_hits > pos_hits and neg_hits > 0:
        return "negative"
    if pos_hits > neg_hits and pos_hits > 0:
        return "positive"
    return "neutral"


def detect_mood(text: str) -> str:
    """
    Hybrid mood detector:
    1. Try NLTK VADER sentiment and log scores.
    2. If unavailable, fall back to rule-based.
    """
    result = analyze_sentiment(text)
    if result.get("available"):
        # Log sentiment analysis details for research/analytics
        log_sentiment(result, context=text)
        return result.get("label", "neutral")

    # Fallback to rule-based if ML sentiment not available
    return detect_mood_rule_based(text)


def friendly_reflection(user_text: str, mood: str) -> str:
    """
    Make a short, friendly reflection instead of repeating the full user text.
    Style: like a supportive friend (like ChatGPT), clear and simple.
    """
    cleaned = user_text.strip()
    if len(cleaned) > 160:
        cleaned = cleaned[:160] + "..."

    base_templates = [
        "Thanks for sharing that with me.",
        "I'm glad you felt comfortable telling me this.",
        "I can see this is on your mind.",
        "It sounds like this really matters to you.",
    ]

    negative_templates = [
        "It sounds like you're going through something tough.",
        "That does sound really heavy to carry on your own.",
        "It seems like things have been pretty hard lately.",
    ]

    positive_templates = [
        "It sounds like there are some hopeful things happening for you.",
        "I'm happy to hear there's some positivity in how you're feeling.",
        "It seems like you're noticing some good things in your life.",
    ]

    neutral_templates = [
        "I hear you.",
        "Thanks for explaining what's going on.",
        "Got it, I understand what you're saying.",
    ]

    if mood == "negative":
        first = random.choice(negative_templates)
    elif mood == "positive":
        first = random.choice(positive_templates)
    else:
        first = random.choice(neutral_templates + base_templates)

    # Sometimes include a small echo of what they said
    second_templates = [
        f"From what you said, it feels like: “{cleaned}”.",
        "You're not alone in feeling this way, even if it might feel like it.",
        "It's okay if this feels confusing or heavy.",
        "Feeling like this is completely valid.",
    ]
    second = random.choice(second_templates)

    return first + " " + second


def pick_coping_suggestion(mood: str) -> str:
    """
    Return a gentle, simple suggestion based on mood.
    """
    if mood == "negative":
        bucket = COPING_STRATEGIES.get("sad", []) + COPING_STRATEGIES.get(
            "anxious", []
        )
    elif mood == "stressed":
        bucket = COPING_STRATEGIES.get("stressed", [])
    else:
        bucket = COPING_STRATEGIES.get("general", [])

    if not bucket:
        return (
            "Sometimes doing one small kind thing for yourself can help a little, "
            "even if it feels like a tiny step."
        )
    return random.choice(bucket)


def next_question(mood: str) -> str:
    """
    Ask a simple, friendly follow-up question to keep the conversation going.
    """
    if mood == "negative":
        return (
            "If you feel okay sharing, what's the part that feels hardest right now?"
        )
    if mood == "positive":
        return "What would you like to keep building on from these positive feelings?"
    return "What part of this would you like to talk about a bit more?"


def generate_reply(user_text: str) -> Tuple[str, bool]:
    """
    Main function used by main.py and the Streamlit app.
    Returns: (reply_text, is_crisis_flag)

    Style goal:
    - Friendly
    - Clear and simple
    - Supportive, not robotic
    - Still shows a short safety reminder
    """

    # 1. Crisis check (highest priority)
    is_crisis, crisis_msg = check_crisis(user_text)
    if is_crisis:
        log_message("system", "[CRISIS FLAG TRIGGERED]")
        return crisis_msg, True

    # 2. Mood detection (hybrid with sentiment logging)
    mood = detect_mood(user_text)

    # 3. Friendly reflection
    reflection = friendly_reflection(user_text, mood)

    # 4. Coping suggestion
    suggestion = pick_coping_suggestion(mood)

    # 5. Follow-up question
    followup = next_question(mood)

    # 6. Short, friendly disclaimer
    safety_line = (
        "Just to remind you, I'm an AI and not a professional. "
        "I can't diagnose or handle emergencies."
    )

    reply_parts = [
        reflection,
        "",
        suggestion,
        "",
        followup,
        "",
        f"_(Safety note: {safety_line})_",
    ]

    reply = "\n".join(reply_parts)
    return reply, False

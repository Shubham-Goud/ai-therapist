"""
Sentiment analysis utilities using NLTK VADER.

This module tries to use NLTK's SentimentIntensityAnalyzer.
If anything fails (no internet, no NLTK, etc.), it falls back gracefully.
"""

from typing import Dict, Any

try:
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
except ImportError:
    nltk = None
    SentimentIntensityAnalyzer = None

_sia = None  # Global analyzer instance


def _get_analyzer():
    """
    Lazy-load and cache the SentimentIntensityAnalyzer.
    Returns None if it cannot be initialized.
    """
    global _sia

    if _sia is not None:
        return _sia

    if nltk is None or SentimentIntensityAnalyzer is None:
        return None

    try:
        # Ensure VADER lexicon is downloaded
        try:
            nltk.data.find("sentiment/vader_lexicon")
        except LookupError:
            nltk.download("vader_lexicon", quiet=True)

        _sia = SentimentIntensityAnalyzer()
        return _sia
    except Exception:
        # Any failure -> disable ML sentiment
        return None


def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    Analyze sentiment using VADER.
    Returns:
        {
          "available": bool,
          "label": "positive"|"negative"|"neutral",
          "compound": float,
          "scores": dict
        }
    If not available, returns {"available": False}.
    """
    sia = _get_analyzer()
    if sia is None:
        return {"available": False}

    if not text.strip():
        return {
            "available": True,
            "label": "neutral",
            "compound": 0.0,
            "scores": {"neg": 0.0, "neu": 1.0, "pos": 0.0, "compound": 0.0},
        }

    scores = sia.polarity_scores(text)
    compound = scores.get("compound", 0.0)

    if compound >= 0.05:
        label = "positive"
    elif compound <= -0.05:
        label = "negative"
    else:
        label = "neutral"

    return {
        "available": True,
        "label": label,
        "compound": compound,
        "scores": scores,
    }

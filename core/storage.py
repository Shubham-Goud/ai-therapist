"""
Conversation logging utilities.
"""
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict, Any

LOG_FILE = Path("conversation_log.txt")


def _timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log_message(role: str, text: str) -> None:
    ts = _timestamp()
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[{ts}] {role.upper()}: {text}\n")


def log_turns(turns: List[Tuple[str, str]]) -> None:
    for role, text in turns:
        log_message(role, text)


def log_sentiment(result: Dict[str, Any], context: str = "") -> None:
    """
    Log sentiment analysis results to the same log file.
    result example:
        {
          "available": True,
          "label": "positive",
          "compound": 0.73,
          "scores": {"neg": 0.0, "neu": 0.4, "pos": 0.6, "compound": 0.73}
        }
    """
    if not result.get("available"):
        return

    ts = _timestamp()
    label = result.get("label")
    compound = result.get("compound")
    scores = result.get("scores")

    context_snippet = context.strip()
    if len(context_snippet) > 80:
        context_snippet = context_snippet[:80] + "..."

    line = (
        f"[{ts}] SENTIMENT: label={label}, compound={compound}, "
        f"scores={scores}, context='{context_snippet}'"
    )
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line + "\n")

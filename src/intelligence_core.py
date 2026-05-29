"""
Intelligence Core: Compliance and 2026 Content Standards.
Detects and filters robotic or unnatural language generation.
"""

import re

BANNED_WORDS = [
    "delve",
    "leverage",
    "unleash",
    "tapestry",
    "testament",
    "excited to",
    "dynamic team",
    "innovative environment",
    "cutting-edge",
    "game-changing",
    "revolutionize",
]


def apply_2026_standards(text: str) -> str:
    """
    Applies the anti-robot filter and ensures viral syntax spacing constraints.
    Replaces banned words with simpler alternatives.
    """
    cleaned = text
    # Case-insensitive replacement
    replacements = {
        r"\bdelve\b": "go deep",
        r"\bleverage\b": "use",
        r"\bunleash\b": "show",
        r"\btapestry\b": "structure",
        r"\btestament\b": "proof",
        r"\bexcited to\b": "ready to",
        r"\bcutting-edge\b": "modern",
        r"\bgame-changing\b": "effective",
        r"\brevolutionize\b": "improve",
    }

    for pattern, replacement in replacements.items():
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)

    return cleaned

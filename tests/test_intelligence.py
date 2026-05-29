from src.intelligence_core import BANNED_WORDS, apply_2026_standards


def test_banned_words_contain_manifesto_banned_words():
    assert "delve" in BANNED_WORDS
    assert "leverage" in BANNED_WORDS
    assert "unleash" in BANNED_WORDS


def test_apply_2026_standards_replacements():
    text = "We will leverage our expertise to delve into the case and unleash our strategy."
    cleaned = apply_2026_standards(text)

    assert "leverage" not in cleaned.lower()
    assert "delve" not in cleaned.lower()
    assert "unleash" not in cleaned.lower()

    # Ensure replacements are correct
    assert "use" in cleaned.lower()
    assert "go deep" in cleaned.lower()
    assert "show" in cleaned.lower()


def test_apply_2026_standards_case_insensitive():
    text = "DELVE deep and LEVERAGE assets."
    cleaned = apply_2026_standards(text)

    assert "delve" not in cleaned.lower()
    assert "leverage" not in cleaned.lower()

import json
from pathlib import Path

SUPPORTED_LOCALES = ("zh-TW", "en")
DEFAULT_LOCALE = "zh-TW"

_messages: dict[str, dict[str, str]] = {}


def _load_messages() -> None:
    msg_dir = Path(__file__).parent / "messages"
    for locale in SUPPORTED_LOCALES:
        filepath = msg_dir / f"{locale}.json"
        if filepath.exists():
            with open(filepath, encoding="utf-8") as f:
                _messages[locale] = json.load(f)


def t(key: str, locale: str | None = None, **kwargs: str) -> str:
    """Translate a dotted key like 'auth.invalid_token' for the given locale."""
    if not _messages:
        _load_messages()

    loc = locale if locale in SUPPORTED_LOCALES else DEFAULT_LOCALE
    msgs = _messages.get(loc, {})

    # Support dotted keys
    parts = key.split(".")
    value = msgs
    for part in parts:
        if isinstance(value, dict):
            value = value.get(part)
        else:
            value = None
            break

    if value is None or not isinstance(value, str):
        # Fallback to default locale
        value = _messages.get(DEFAULT_LOCALE, {})
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                value = None
                break

    if value is None or not isinstance(value, str):
        return key  # Return the key itself if no translation found

    # Simple string interpolation
    for k, v in kwargs.items():
        value = value.replace(f"{{{k}}}", v)

    return value


def resolve_locale(accept_language: str | None = None) -> str:
    """Resolve locale from Accept-Language header."""
    if not accept_language:
        return DEFAULT_LOCALE

    # Parse Accept-Language: zh-TW,zh;q=0.9,en;q=0.8
    for part in accept_language.split(","):
        lang = part.split(";")[0].strip()
        if lang in SUPPORTED_LOCALES:
            return lang
        # Handle zh -> zh-TW
        if lang.lower().startswith("zh"):
            return "zh-TW"
        if lang.lower().startswith("en"):
            return "en"

    return DEFAULT_LOCALE

import json
from pathlib import Path
from typing import Any

SUPPORTED_LOCALES = ("zh-TW", "en")
DEFAULT_LOCALE = "zh-TW"

_messages: dict[str, Any] = {}


def _load_messages() -> None:
    msg_dir = Path(__file__).parent / "messages"
    for locale in SUPPORTED_LOCALES:
        filepath = msg_dir / f"{locale}.json"
        if filepath.exists():
            with open(filepath, encoding="utf-8") as f:
                _messages[locale] = json.load(f)


def _resolve(msgs: Any, parts: list[str]) -> str | None:
    """Walk nested dict by dotted key parts, return string or None."""
    current = msgs
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current if isinstance(current, str) else None


def t(key: str, locale: str | None = None, **kwargs: str) -> str:
    """Translate a dotted key like 'auth.invalid_token' for the given locale."""
    if not _messages:
        _load_messages()

    loc = locale if locale in SUPPORTED_LOCALES else DEFAULT_LOCALE
    parts = key.split(".")

    value = _resolve(_messages.get(loc, {}), parts)
    if value is None:
        value = _resolve(_messages.get(DEFAULT_LOCALE, {}), parts)
    if value is None:
        return key

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

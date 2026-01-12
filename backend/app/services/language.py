from fastapi import Request
from app.config import settings


def get_language(request: Request) -> str:
    """
    Extract language from Accept-Language header.
    Returns 'hr', 'en', or 'de' (defaults to 'en').
    """
    accept_language = request.headers.get("Accept-Language", settings.DEFAULT_LANGUAGE)

    # Parse the Accept-Language header
    # Example: "hr,en;q=0.9,de;q=0.8" -> "hr"
    if accept_language:
        # Get the first language preference
        primary_lang = accept_language.split(",")[0].split(";")[0].strip().lower()

        # Map language codes (handle variations like "en-US" -> "en")
        lang_code = primary_lang.split("-")[0]

        if lang_code in settings.SUPPORTED_LANGUAGES:
            return lang_code

    return settings.DEFAULT_LANGUAGE

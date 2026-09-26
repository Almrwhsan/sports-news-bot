# ============================================================
# News Translator
# Arabic-first translation system
# ============================================================

import re
import time
import requests


TRANSLATE_URL = "https://translate.googleapis.com/translate_a/single"

REQUEST_TIMEOUT = 15

# عدد المحاولات عند فشل الترجمة
MAX_RETRIES = 3

# انتظار بسيط بين المحاولات
RETRY_DELAY = 2


ARABIC_RE = re.compile(r"[\u0600-\u06FF]")
LATIN_RE = re.compile(r"[A-Za-z]")


def arabic_ratio(text):
    """
    Calculate the percentage of Arabic characters.
    """

    if not text:
        return 0.0

    arabic_chars = len(ARABIC_RE.findall(text))
    latin_chars = len(LATIN_RE.findall(text))

    total = arabic_chars + latin_chars

    if total == 0:
        return 0.0

    return arabic_chars / total


def latin_ratio(text):
    """
    Calculate the percentage of Latin characters.
    """

    if not text:
        return 0.0

    arabic_chars = len(ARABIC_RE.findall(text))
    latin_chars = len(LATIN_RE.findall(text))

    total = arabic_chars + latin_chars

    if total == 0:
        return 0.0

    return latin_chars / total


def needs_translation(news):
    """
    Determine whether the news item needs Arabic translation.
    """

    title = news.get("title", "") or ""
    summary = news.get("summary", "") or ""

    text = f"{title} {summary}".strip()

    if not text:
        return False

    ar_ratio = arabic_ratio(text)
    lat_ratio = latin_ratio(text)

    # Clearly Arabic
    if ar_ratio >= 0.25:
        return False

    # Clearly foreign
    if lat_ratio >= 0.50:
        return True

    # If source language is not Arabic,
    # prefer translating mixed content.
    language = str(
        news.get("language", "")
    ).lower()

    if language and language != "ar":
        return True

    return False


def translate_text(text):
    """
    Translate text to Arabic using Google Translate endpoint.

    Returns:
        Arabic translated text or None if translation fails.
    """

    if not text:
        return ""

    text = str(text).strip()

    if not text:
        return ""

    params = {
        "client": "gtx",
        "sl": "auto",
        "tl": "ar",
        "dt": "t",
        "q": text,
    }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/140.0 Safari/537.36"
        )
    }

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            response = requests.get(
                TRANSLATE_URL,
                params=params,
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )

            if response.status_code == 200:

                data = response.json()

                if (
                    isinstance(data, list)
                    and len(data) > 0
                    and isinstance(data[0], list)
                ):

                    translated_parts = []

                    for part in data[0]:

                        if (
                            isinstance(part, list)
                            and len(part) > 0
                            and part[0]
                        ):
                            translated_parts.append(
                                str(part[0])
                            )

                    translated = "".join(
                        translated_parts
                    ).strip()

                    if translated:
                        return translated

            elif response.status_code == 429:

                print(
                    f"⚠️ Translation rate limit "
                    f"(429), attempt {attempt}/{MAX_RETRIES}"
                )

            else:

                print(
                    f"⚠️ Translation HTTP "
                    f"{response.status_code}, "
                    f"attempt {attempt}/{MAX_RETRIES}"
                )

        except Exception as e:

            print(
                f"⚠️ Translation error "
                f"(attempt {attempt}/{MAX_RETRIES}): {e}"
            )

        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY * attempt)

    return None


def translate_news_item(news):
    """
    Translate one news item to Arabic.

    Important:
    We NEVER intentionally replace a failed translation
    with the original foreign-language text.
    """

    title = (
        news.get("title", "") or ""
    ).strip()

    summary = (
        news.get("summary", "") or ""
    ).strip()

    language = str(
        news.get("language", "")
    ).lower()

    # --------------------------------------------------------
    # Arabic source / already Arabic
    # --------------------------------------------------------

    if language == "ar" or not needs_translation(news):

        news["arabic_title"] = title
        news["arabic_summary"] = summary
        news["translation_status"] = "not_needed"

        return news

    # --------------------------------------------------------
    # Translate title
    # --------------------------------------------------------

    print(
        f"🌍 Translating: "
        f"{title[:80]}"
    )

    translated_title = translate_text(title)

    # If title translation fails, do not silently
    # publish the original foreign title.
    if not translated_title:

        print(
            "❌ Title translation failed. "
            "News will not be published."
        )

        news["arabic_title"] = ""
        news["arabic_summary"] = ""
        news["translation_status"] = "failed"

        return news

    # --------------------------------------------------------
    # Translate summary
    # --------------------------------------------------------

    translated_summary = ""

    if summary:

        translated_summary = translate_text(
            summary
        )

        # Summary is less critical than the title.
        # If it fails, we can continue with title only.
        if not translated_summary:

            print(
                "⚠️ Summary translation failed. "
                "Using translated title only."
            )

    news["arabic_title"] = translated_title
    news["arabic_summary"] = translated_summary

    news["translation_status"] = "translated"

    return news


def translate_news(news_list):
    """
    Translate all news items.

    Foreign-language items that fail title translation
    are removed instead of publishing untranslated text.
    """

    translated_news = []

    total = len(news_list)

    print(
        f"\n🌍 Starting translation "
        f"for {total} news items..."
    )

    for index, news in enumerate(
        news_list,
        start=1
    ):

        print(
            f"📝 Translation "
            f"{index}/{total}"
        )

        result = translate_news_item(news)

        status = result.get(
            "translation_status",
            ""
        )

        # Never publish an untranslated foreign item
        if status == "failed":

            print(
                "⛔ Skipping news because "
                "Arabic translation failed."
            )

            continue

        translated_news.append(result)

        # Small delay helps reduce 429 errors
        # when many foreign articles arrive together.
        if index < total:
            time.sleep(0.5)

    print(
        f"\n✅ Translation complete: "
        f"{len(translated_news)} ready"
    )

    print(
        f"⛔ Skipped: "
        f"{total - len(translated_news)}"
    )

    return translated_news

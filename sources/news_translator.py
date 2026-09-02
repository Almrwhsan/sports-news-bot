# ============================================================
# ترجمة أخبار كرة القدم إلى العربية
# ============================================================

import re
import urllib.parse
import urllib.request
import json


# ============================================================
# إعدادات الترجمة
# ============================================================

TRANSLATION_TIMEOUT = 15


# ============================================================
# تنظيف النص
# ============================================================

def clean_text(text):

    if not text:

        return ""

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


# ============================================================
# تحديد الحاجة إلى الترجمة
# ============================================================

def needs_translation(news):

    language = (
        news.get(
            "language",
            ""
        )
        .lower()
        .strip()
    )

    return language not in (
        "",
        "ar",
        "arabic",
    )


# ============================================================
# ترجمة نص واحد
# ============================================================

def translate_text(
    text,
    source_language="auto",
    target_language="ar"
):

    text = clean_text(
        text
    )

    if not text:

        return ""

    # --------------------------------------------------------
    # Google Translate endpoint
    # --------------------------------------------------------

    encoded_text = urllib.parse.quote(
        text
    )

    url = (
        "https://translate.googleapis.com/"
        "translate_a/single"
        "?client=gtx"
        f"&sl={source_language}"
        f"&tl={target_language}"
        "&dt=t"
        f"&q={encoded_text}"
    )

    try:

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=TRANSLATION_TIMEOUT
        ) as response:

            data = json.loads(
                response.read().decode(
                    "utf-8"
                )
            )

        translated_parts = []

        for part in data[0]:

            if part and part[0]:

                translated_parts.append(
                    part[0]
                )

        return clean_text(
            " ".join(
                translated_parts
            )
        )

    except Exception as error:

        print(
            f"❌ Translation failed: "
            f"{error}"
        )

        return ""


# ============================================================
# ترجمة خبر واحد
# ============================================================

def translate_news_item(news):

    translated_news = dict(
        news
    )

    # --------------------------------------------------------
    # الخبر عربي أصلًا
    # --------------------------------------------------------

    if not needs_translation(
        news
    ):

        translated_news["arabic_title"] = (
            clean_text(
                news.get(
                    "title",
                    ""
                )
            )
        )

        translated_news["arabic_summary"] = (
            clean_text(
                news.get(
                    "summary",
                    ""
                )
            )
        )

        return translated_news

    # --------------------------------------------------------
    # ترجمة العنوان
    # --------------------------------------------------------

    title = news.get(
        "title",
        ""
    )

    translated_title = translate_text(
        title,
        source_language="auto",
        target_language="ar"
    )

    # --------------------------------------------------------
    # ترجمة الملخص
    # --------------------------------------------------------

    summary = news.get(
        "summary",
        ""
    )

    translated_summary = translate_text(
        summary,
        source_language="auto",
        target_language="ar"
    )

    # --------------------------------------------------------
    # حفظ النتائج
    # --------------------------------------------------------

    translated_news["arabic_title"] = (
        translated_title
        or title
    )

    translated_news["arabic_summary"] = (
        translated_summary
        or summary
    )

    return translated_news


# ============================================================
# ترجمة قائمة الأخبار
# ============================================================

def translate_news(news_list):

    translated = []

    for news in news_list:

        result = translate_news_item(
            news
        )

        translated.append(
            result
        )

    return translated

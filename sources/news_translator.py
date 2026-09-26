# ============================================================
# ترجمة أخبار كرة القدم إلى العربية
# ============================================================

import re
import urllib.parse
import urllib.request
import json
import html
import time


# ============================================================
# إعدادات الترجمة
# ============================================================

TRANSLATION_TIMEOUT = 15

# عدد المحاولات عند حدوث Rate Limit
MAX_RETRIES = 3

# أوقات الانتظار عند 429
RETRY_DELAYS = [5, 15, 30]


# ============================================================
# أنماط الحروف المستخدمة في تحديد لغة النص
# ============================================================

ARABIC_RE = re.compile(
    r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]"
)

LATIN_RE = re.compile(
    r"[A-Za-zÀ-ÖØ-öø-ÿ]"
)


# ============================================================
# تنظيف النص
# ============================================================

def clean_text(text):

    if not text:
        return ""

    text = str(text)

    # فك HTML entities
    text = html.unescape(text)

    # تحويل وسوم HTML الخاصة بالفواصل إلى مسافة
    text = re.sub(
        r"<\s*(br|br/|br\s*/)\s*>",
        " ",
        text,
        flags=re.IGNORECASE
    )

    # إزالة وسوم HTML
    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

    # فك HTML entities مرة ثانية
    text = html.unescape(text)

    # إزالة أي وسوم HTML متبقية
    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

    # تنظيف المسافات والأسطر
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

    title = clean_text(
        news.get(
            "title",
            ""
        )
    )

    summary = clean_text(
        news.get(
            "summary",
            ""
        )
    )

    text = f"{title} {summary}".strip()

    arabic_count = len(
        ARABIC_RE.findall(
            text
        )
    )

    latin_count = len(
        LATIN_RE.findall(
            text
        )
    )

    total_letters = (
        arabic_count
        + latin_count
    )

    if total_letters == 0:

        language = str(
            news.get(
                "language",
                ""
            )
        ).lower().strip()

        return language not in (
            "",
            "ar",
            "arabic",
        )

    arabic_ratio = (
        arabic_count
        / total_letters
    )

    latin_ratio = (
        latin_count
        / total_letters
    )

    # النص عربي بشكل واضح
    if (
        arabic_count >= 3
        and arabic_ratio >= 0.25
    ):

        return False

    # النص لاتيني بشكل واضح
    if latin_ratio >= 0.65:

        return True

    language = str(
        news.get(
            "language",
            ""
        )
    ).lower().strip()

    # مصدر عربي + نص مختلط
    if language in (
        "ar",
        "arabic",
    ):

        return False

    # الحالات غير الواضحة
    return True


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

    for attempt in range(
        MAX_RETRIES
    ):

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

            if (
                isinstance(data, list)
                and len(data) > 0
                and isinstance(data[0], list)
            ):

                for part in data[0]:

                    if (
                        part
                        and len(part) > 0
                        and part[0]
                    ):

                        translated_parts.append(
                            part[0]
                        )

            translated = clean_text(
                " ".join(
                    translated_parts
                )
            )

            if translated:

                return translated

            print(
                "⚠️ Translation returned empty result."
            )

            return ""

        except Exception as error:

            error_text = str(
                error
            )

            # ------------------------------------------------
            # Rate Limit
            # ------------------------------------------------

            if (
                "429" in error_text
                or "Too Many Requests"
                in error_text
            ):

                if attempt < MAX_RETRIES:

                    delay = RETRY_DELAYS[
                        attempt
                    ]

                    print(
                        f"⚠️ Translation rate limit "
                        f"(429). Waiting {delay}s "
                        f"before retry "
                        f"{attempt + 2}/{MAX_RETRIES}..."
                    )

                    time.sleep(
                        delay
                    )

                    continue

            print(
                f"❌ Translation failed: "
                f"{error}"
            )

            return ""

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

        translated_news[
            "arabic_title"
        ] = clean_text(
            news.get(
                "title",
                ""
            )
        )

        translated_news[
            "arabic_summary"
        ] = clean_text(
            news.get(
                "summary",
                ""
            )
        )

        translated_news[
            "translation_status"
        ] = "not_needed"

        return translated_news

    # --------------------------------------------------------
    # ترجمة العنوان
    # --------------------------------------------------------

    title = clean_text(
        news.get(
            "title",
            ""
        )
    )

    print(
        f"🌍 Translating: "
        f"{title[:100]}"
    )

    translated_title = translate_text(
        title,
        source_language="auto",
        target_language="ar"
    )

    # --------------------------------------------------------
    # إذا فشل العنوان
    # لا ننشر الخبر بلغة أجنبية
    # --------------------------------------------------------

    if not translated_title:

        print(
            "❌ Title translation failed. "
            "News will not be published."
        )

        translated_news[
            "arabic_title"
        ] = ""

        translated_news[
            "arabic_summary"
        ] = ""

        translated_news[
            "translation_status"
        ] = "failed"

        return translated_news

    # --------------------------------------------------------
    # ترجمة الملخص
    # --------------------------------------------------------

    summary = clean_text(
        news.get(
            "summary",
            ""
        )
    )

    translated_summary = ""

    if summary:

        translated_summary = translate_text(
            summary,
            source_language="auto",
            target_language="ar"
        )

        # ----------------------------------------------------
        # إذا فشل الملخص، لا نعيد النص الأجنبي.
        # العنوان العربي يكفي لاستمرار الخبر.
        # ----------------------------------------------------

        if not translated_summary:

            print(
                "⚠️ Summary translation failed. "
                "Using Arabic title only."
            )

    # --------------------------------------------------------
    # النتائج النهائية
    # --------------------------------------------------------

    translated_news[
        "arabic_title"
    ] = clean_text(
        translated_title
    )

    translated_news[
        "arabic_summary"
    ] = clean_text(
        translated_summary
    )

    translated_news[
        "translation_status"
    ] = "translated"

    return translated_news


# ============================================================
# ترجمة قائمة الأخبار
# ============================================================

def translate_news(news_list):

    translated = []

    total = len(
        news_list
    )

    for index, news in enumerate(
        news_list,
        start=1
    ):

        print(
            f"📝 Translation "
            f"{index}/{total}"
        )

        result = translate_news_item(
            news
        )

        # ----------------------------------------------------
        # الأخبار العربية أو المترجمة بنجاح
        # ----------------------------------------------------

        if result.get(
            "translation_status"
        ) != "failed":

            translated.append(
                result
            )

        else:

            print(
                "⛔ Skipping news because "
                "Arabic translation failed."
            )

        # ----------------------------------------------------
        # فاصل بسيط بين الأخبار
        # ----------------------------------------------------

        if index < total:

            time.sleep(
                2
            )

    return translated

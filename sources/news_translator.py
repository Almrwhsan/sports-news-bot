# ============================================================
# ترجمة أخبار كرة القدم إلى العربية
# ============================================================

import re
import urllib.parse
import urllib.request
import json
import html


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

    # --------------------------------------------------------
    # التأكد من أن القيمة نص
    # --------------------------------------------------------

    text = str(text)

    # --------------------------------------------------------
    # فك HTML entities
    #
    # مثال:
    # &lt;div&gt;  -> <div>
    # &amp;      -> &
    # &quot;     -> "
    # --------------------------------------------------------

    text = html.unescape(
        text
    )

    # --------------------------------------------------------
    # تحويل وسوم HTML الخاصة بالفواصل إلى مسافة
    # --------------------------------------------------------

    text = re.sub(
        r"<\s*(br|br/|br\s*/)\s*>",
        " ",
        text,
        flags=re.IGNORECASE
    )

    # --------------------------------------------------------
    # إزالة وسوم HTML المتبقية
    #
    # مثال:
    # <div style="direction: rtl;">
    # </div>
    # <p>...</p>
    # --------------------------------------------------------

    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

    # --------------------------------------------------------
    # فك HTML entities مرة ثانية
    #
    # لأن بعض المصادر قد تحتوي على:
    # &lt;div&gt;
    # وبعد فكها تصبح:
    # <div>
    # --------------------------------------------------------

    text = html.unescape(
        text
    )

    # --------------------------------------------------------
    # إزالة أي وسوم HTML متبقية بعد الفك
    # --------------------------------------------------------

    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

    # --------------------------------------------------------
    # تنظيف المسافات والأسطر الزائدة
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # تنظيف النص قبل الترجمة
    # --------------------------------------------------------

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

        # ----------------------------------------------------
        # تنظيف الترجمة أيضًا
        # ----------------------------------------------------

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
    # تنظيف النتائج النهائية
    # --------------------------------------------------------

    translated_news["arabic_title"] = (
        clean_text(
            translated_title
            or title
        )
    )

    translated_news["arabic_summary"] = (
        clean_text(
            translated_summary
            or summary
        )
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

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
TRANSLATION_RETRIES = 2


# ============================================================
# تنظيف النص
# ============================================================

def clean_text(text):

    if not text:
        return ""

    text = str(text)

    # فك ترميز HTML
    text = html.unescape(text)

    # تحويل BR إلى مسافة
    text = re.sub(
        r"<\s*(br|br/|br\s*/)\s*>",
        " ",
        text,
        flags=re.IGNORECASE
    )

    # إزالة HTML
    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

    # فك الترميز مرة أخرى
    text = html.unescape(text)

    # إزالة أي HTML متبقٍ
    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

    # توحيد المسافات
    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


# ============================================================
# التحقق من وجود أحرف عربية
# ============================================================

def contains_arabic(text):

    if not text:
        return False

    return bool(
        re.search(
            r"[\u0600-\u06FF"
            r"\u0750-\u077F"
            r"\u08A0-\u08FF"
            r"\uFB50-\uFDFF"
            r"\uFE70-\uFEFF]",
            str(text)
        )
    )


# ============================================================
# تحديد لغة المصدر
# ============================================================

def normalize_source_language(language):

    if not language:
        return "auto"

    language = str(
        language
    ).lower().strip()

    # أمثلة:
    # es-ES -> es
    # en-US -> en
    # ar-SA -> ar

    if language.startswith("es"):
        return "es"

    if language.startswith("en"):
        return "en"

    if language.startswith("ar"):
        return "ar"

    return "auto"


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

    # إذا كان الخبر عربيًا فلا يحتاج ترجمة
    if language in (
        "ar",
        "arabic",
    ):
        return False

    # إذا لم يتم تحديد اللغة،
    # نتحقق من النص نفسه
    if not language:

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

        if (
            contains_arabic(title)
            or contains_arabic(summary)
        ):
            return False

    return True


# ============================================================
# التحقق من صحة الترجمة
# ============================================================

def is_valid_translation(
    original,
    translated,
    target_language="ar"
):

    original = clean_text(
        original
    )

    translated = clean_text(
        translated
    )

    if not translated:
        return False

    # الترجمة العربية يجب أن تحتوي على أحرف عربية
    if target_language == "ar":

        if not contains_arabic(
            translated
        ):
            return False

    # إذا كانت الترجمة مطابقة تمامًا للنص الأصلي
    # وكان النص الأصلي غير عربي، فهذا ليس ترجمة
    if (
        original
        and translated.casefold()
        == original.casefold()
        and not contains_arabic(original)
    ):
        return False

    return True


# ============================================================
# استخراج الترجمة من استجابة Google
# ============================================================

def extract_translation(data):

    if not data:
        return ""

    try:

        parts = data[0]

    except (
        IndexError,
        TypeError,
    ):
        return ""

    translated_parts = []

    if not isinstance(
        parts,
        list
    ):
        return ""

    for part in parts:

        if not part:
            continue

        if not isinstance(
            part,
            list
        ):
            continue

        if len(part) < 2:
            continue

        translated_part = part[0]

        if translated_part:
            translated_parts.append(
                str(translated_part)
            )

    return clean_text(
        " ".join(
            translated_parts
        )
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

    # إذا كان النص عربيًا بالفعل
    if (
        target_language == "ar"
        and contains_arabic(text)
    ):
        return text

    normalized_source = (
        normalize_source_language(
            source_language
        )
    )

    encoded_text = urllib.parse.quote(
        text
    )

    # ========================================================
    # المحاولة الأولى
    # ========================================================

    source_languages = [
        normalized_source
    ]

    # إذا كانت اللغة غير معروفة،
    # نستخدم auto مباشرة
    if normalized_source == "ar":

        return text

    # في حالة تحديد لغة معينة،
    # نضيف auto كمحاولة احتياطية
    if normalized_source != "auto":

        source_languages.append(
            "auto"
        )

    for current_source in source_languages:

        for attempt in range(
            TRANSLATION_RETRIES
        ):

            url = (
                "https://translate.googleapis.com/"
                "translate_a/single"
                "?client=gtx"
                f"&sl={current_source}"
                f"&tl={target_language}"
                "&dt=t"
                f"&q={encoded_text}"
            )

            try:

                request = urllib.request.Request(
                    url,
                    headers={
                        "User-Agent":
                            "Mozilla/5.0"
                    }
                )

                with urllib.request.urlopen(
                    request,
                    timeout=TRANSLATION_TIMEOUT
                ) as response:

                    raw_data = response.read()

                    data = json.loads(
                        raw_data.decode(
                            "utf-8"
                        )
                    )

                translated = (
                    extract_translation(
                        data
                    )
                )

                # =================================================
                # التحقق الحقيقي من النتيجة
                # =================================================

                if is_valid_translation(
                    text,
                    translated,
                    target_language
                ):

                    return translated

                print(
                    "⚠️ Translation returned "
                    "an invalid/non-Arabic result "
                    f"(source={current_source}, "
                    f"attempt={attempt + 1})"
                )

            except Exception as error:

                print(
                    "⚠️ Translation attempt failed: "
                    f"{error} "
                    f"(source={current_source}, "
                    f"attempt={attempt + 1})"
                )

            # انتظار بسيط قبل إعادة المحاولة
            if attempt < (
                TRANSLATION_RETRIES - 1
            ):

                time.sleep(1)

    # ========================================================
    # فشل نهائي
    # ========================================================

    print(
        "❌ Translation failed after "
        "all attempts."
    )

    # مهم جدًا:
    # لا نعيد النص الأصلي هنا.
    #
    # لأن إعادة النص الأصلي كانت سبب المشكلة
    # التي جعلت الإسبانية تظهر في arabic_title
    # و arabic_summary.
    return ""


# ============================================================
# ترجمة خبر واحد
# ============================================================

def translate_news_item(news):

    translated_news = dict(
        news
    )

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

    # ========================================================
    # الخبر عربي أصلًا
    # ========================================================

    if not needs_translation(
        news
    ):

        translated_news[
            "arabic_title"
        ] = title

        translated_news[
            "arabic_summary"
        ] = summary

        translated_news[
            "translation_failed"
        ] = False

        return translated_news

    # ========================================================
    # تحديد لغة المصدر
    # ========================================================

    source_language = (
        normalize_source_language(
            news.get(
                "language",
                ""
            )
        )
    )

    # ========================================================
    # ترجمة العنوان
    # ========================================================

    translated_title = translate_text(
        title,
        source_language=source_language,
        target_language="ar"
    )

    # ========================================================
    # ترجمة الملخص
    # ========================================================

    translated_summary = translate_text(
        summary,
        source_language=source_language,
        target_language="ar"
    )

    # ========================================================
    # التحقق من العنوان
    # ========================================================

    title_valid = is_valid_translation(
        title,
        translated_title,
        "ar"
    )

    # ========================================================
    # التحقق من الملخص
    # ========================================================

    summary_valid = True

    # إذا كان هناك ملخص أصلًا،
    # فيجب أن تكون ترجمته صحيحة
    if summary:

        summary_valid = is_valid_translation(
            summary,
            translated_summary,
            "ar"
        )

    # ========================================================
    # التعامل مع فشل الترجمة
    # ========================================================

    if not title_valid:

        print(
            "❌ Arabic title translation "
            "failed."
        )

        print(
            f"Original title: {title}"
        )

        translated_news[
            "arabic_title"
        ] = ""

    else:

        translated_news[
            "arabic_title"
        ] = clean_text(
            translated_title
        )

    # ========================================================
    # التعامل مع فشل ترجمة الملخص
    # ========================================================

    if not summary:

        translated_news[
            "arabic_summary"
        ] = ""

    elif not summary_valid:

        print(
            "❌ Arabic summary translation "
            "failed."
        )

        print(
            f"Original summary: {summary}"
        )

        translated_news[
            "arabic_summary"
        ] = ""

    else:

        translated_news[
            "arabic_summary"
        ] = clean_text(
            translated_summary
        )

    # ========================================================
    # حالة الترجمة
    # ========================================================

    translated_news[
        "translation_failed"
    ] = not title_valid

    # ========================================================
    # تشخيص إضافي
    # ========================================================

    if translated_news[
        "translation_failed"
    ]:

        print(
            "⚠️ News translation was "
            "not accepted."
        )

        print(
            "⚠️ The original non-Arabic "
            "title will NOT be stored "
            "as arabic_title."
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

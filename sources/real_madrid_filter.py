# ============================================================
# Real Madrid News Filter
# فلترة أخبار ريال مدريد فقط
# ============================================================

import re
import unicodedata


# ============================================================
# الكلمات الدالة على ريال مدريد
# ============================================================

REAL_MADRID_KEYWORDS = [
    "real madrid",
    "real-madrid",
    "real madrid cf",
    "realmadrid",
    "ريال مدريد",
]


# ============================================================
# استبعاد المحتوى غير الإخباري
# ============================================================

EXCLUDED_KEYWORDS = [
    "podcast",
    "quiz",
    "horoscope",
    "crossword",
    "بودكاست",
    "اختبار",
    "كلمات متقاطعة",
]


# ============================================================
# تنظيف النص وتوحيد الحروف
# ============================================================

def normalize_text(text):
    """
    توحيد النص لتسهيل البحث عن الكلمات.
    لا يترجم النص ولا يغيّر محتواه المنشور.
    """

    if not text:
        return ""

    text = str(text).casefold()

    # إزالة العلامات الصوتية والتشكيل
    text = unicodedata.normalize("NFKD", text)

    text = "".join(
        char
        for char in text
        if not unicodedata.combining(char)
    )

    # توحيد بعض الحروف العربية
    text = (
        text.replace("أ", "ا")
        .replace("إ", "ا")
        .replace("آ", "ا")
        .replace("ى", "ي")
    )

    # توحيد المسافات
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# التحقق من أن الخبر قادم من مصدر متخصص بالنادي
# ============================================================

def is_real_madrid_source(news):
    """
    المصدر المتخصص بالنادي يمكن قبول خبره
    حتى لو لم يذكر العنوان اسم ريال مدريد صراحة.
    """

    category = normalize_text(
        news.get("category", "")
    )

    source_type = normalize_text(
        news.get("type", "")
    )

    source_name = normalize_text(
        news.get("source", "")
    )

    if (
        category == "real_madrid"
        and source_type == "club"
    ):
        return True

    if source_name == "as real madrid":
        return True

    return False


# ============================================================
# التحقق من كلمات ريال مدريد
# ============================================================

def mentions_real_madrid(news):
    title = normalize_text(
        news.get("title", "")
    )

    summary = normalize_text(
        news.get("summary", "")
    )

    text = f"{title} {summary}"

    return any(
        normalize_text(keyword) in text
        for keyword in REAL_MADRID_KEYWORDS
    )


# ============================================================
# استبعاد المحتوى غير الإخباري
# ============================================================

def is_excluded_content(news):
    title = normalize_text(
        news.get("title", "")
    )

    return any(
        normalize_text(keyword) in title
        for keyword in EXCLUDED_KEYWORDS
    )


# ============================================================
# التحقق من انتماء الخبر إلى ريال مدريد
# ============================================================

def is_real_madrid_news(news):
    """
    يقبل الخبر إذا تحقق أحد الشرطين:

    1. قادم من مصدر متخصص بريال مدريد.
    2. يذكر ريال مدريد بوضوح في العنوان أو الملخص.

    مع استبعاد المحتوى غير الإخباري.
    """

    if not isinstance(news, dict):
        return False

    if is_excluded_content(news):
        return False

    if is_real_madrid_source(news):
        return True

    return mentions_real_madrid(news)


# ============================================================
# فلترة قائمة الأخبار
# ============================================================

def filter_real_madrid_news(news_list):
    """
    إرجاع الأخبار المتعلقة بريال مدريد فقط.
    لا يحذف أو يعدّل عناصر القائمة الأصلية.
    """

    if not isinstance(news_list, list):
        return []

    filtered_news = []

    for news in news_list:

        if is_real_madrid_news(news):

            item = dict(news)

            item["category"] = "real_madrid"

            filtered_news.append(item)

    print(
        "⚪ Real Madrid filter: "
        f"{len(filtered_news)} / {len(news_list)}"
    )

    return filtered_news

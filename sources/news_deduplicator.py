# ============================================================
# إزالة الأخبار المتكررة وترتيبها حسب أولوية المصدر
# ============================================================

import re
from difflib import SequenceMatcher


# ============================================================
# إعدادات إزالة التكرار
# ============================================================

SIMILARITY_THRESHOLD = 0.82


# ============================================================
# تنظيف العنوان للمقارنة
# ============================================================

def normalize_title(title):

    title = title.lower()

    # إزالة علامات الترقيم
    title = re.sub(
        r"[^\w\s]",
        " ",
        title,
        flags=re.UNICODE
    )

    # إزالة المسافات الزائدة
    title = re.sub(
        r"\s+",
        " ",
        title
    ).strip()

    return title


# ============================================================
# حساب تشابه عنوانين
# ============================================================

def title_similarity(title_a, title_b):

    normalized_a = normalize_title(
        title_a
    )

    normalized_b = normalize_title(
        title_b
    )

    if not normalized_a or not normalized_b:

        return 0.0

    return SequenceMatcher(
        None,
        normalized_a,
        normalized_b
    ).ratio()


# ============================================================
# اختيار الخبر الأفضل
# ============================================================

def choose_best_news(news_a, news_b):

    priority_a = news_a.get(
        "priority",
        999
    )

    priority_b = news_b.get(
        "priority",
        999
    )

    # الرقم الأصغر = أولوية أعلى
    if priority_a < priority_b:

        return news_a

    if priority_b < priority_a:

        return news_b

    # إذا كانت الأولوية متساوية،
    # نحتفظ بالخبر الأول
    return news_a


# ============================================================
# إزالة الأخبار المتكررة
# ============================================================

def deduplicate_news(news_list):

    unique_news = []

    for news in news_list:

        title = news.get(
            "title",
            ""
        )

        if not title:

            continue

        duplicate_index = None

        for index, existing in enumerate(
            unique_news
        ):

            similarity = title_similarity(
                title,
                existing.get(
                    "title",
                    ""
                )
            )

            if similarity >= SIMILARITY_THRESHOLD:

                duplicate_index = index

                break

        # ----------------------------------------------------
        # لا يوجد تكرار
        # ----------------------------------------------------

        if duplicate_index is None:

            unique_news.append(
                news
            )

            continue

        # ----------------------------------------------------
        # يوجد تكرار
        # ----------------------------------------------------

        existing_news = unique_news[
            duplicate_index
        ]

        best_news = choose_best_news(
            existing_news,
            news
        )

        unique_news[
            duplicate_index
        ] = best_news

    return unique_news

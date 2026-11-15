
# ============================================================
# Arabic News Formatter
# صياغة منشورات نبض مدريد باللغة العربية
# ============================================================


CATEGORY_LABELS = {
    "real_madrid": "ريال مدريد",
}


def clean_text(text):
    """تنظيف النص والمسافات."""

    if not text:
        return ""

    return " ".join(
        str(text).split()
    ).strip()


def get_category_label(category):
    """إرجاع التصنيف العربي."""

    return CATEGORY_LABELS.get(
        category,
        "ريال مدريد"
    )


def build_post_title(news):
    """
    استخدام العنوان العربي فقط.
    لا نسمح بنشر العنوان الأجنبي كبديل.
    """

    return clean_text(
        news.get("arabic_title", "")
    )


def build_post_summary(news):
    """
    استخدام الملخص العربي فقط.
    """

    return clean_text(
        news.get("arabic_summary", "")
    )


def build_post_text(news):
    """إنشاء نص المنشور النهائي."""

    title = build_post_title(news)
    summary = build_post_summary(news)

    category = get_category_label(
        news.get("category")
    )

    if not title:
        return ""

    parts = [
        f"⚪ {title}"
    ]

    if summary:

        if len(summary) > 500:
            summary = (
                summary[:497].rstrip()
                + "..."
            )

        parts.append(
            f"📝 {summary}"
        )

    parts.append(
        f"⚽ {category}"
    )

    parts.append(
        "📍 نبض مدريد"
    )

    return "\n\n".join(parts)


def format_news_item(news):
    """تنسيق خبر واحد."""

    item = dict(news)

    post_title = build_post_title(item)
    post_text = build_post_text(item)

    if not post_title or not post_text:
        return None

    item["post_title"] = post_title
    item["post_text"] = post_text

    return item


def format_news(news_list):
    """تنسيق قائمة الأخبار."""

    formatted_news = []

    for news in news_list:

        try:

            formatted = format_news_item(
                news
            )

            if formatted:
                formatted_news.append(
                    formatted
                )

            else:
                print(
                    "⛔ Skipping news: "
                    "Arabic title is missing."
                )

        except Exception as error:

            print(
                f"⚠️ Formatting error: {error}"
            )

    print(
        "📰 Arabic formatted news: "
        f"{len(formatted_news)}"
    )

    return formatted_news

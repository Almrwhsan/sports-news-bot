# ============================================================
# News Formatter
# Arabic Facebook Post Formatter
# ============================================================


CATEGORY_LABELS = {
    "real_madrid": "ريال مدريد",
    "barcelona": "برشلونة",
    "atletico_madrid": "أتلتيكو مدريد",
    "transfers": "سوق الانتقالات",
    "champions_league": "دوري أبطال أوروبا",
    "la_liga": "الدوري الإسباني",
    "premier_league": "الدوري الإنجليزي",
    "serie_a": "الدوري الإيطالي",
    "bundesliga": "الدوري الألماني",
    "ligue_1": "الدوري الفرنسي",
    "football": "كرة القدم",
    "world_football": "كرة القدم العالمية",
}


def clean_text(text):
    """
    Clean text before publishing.
    """

    if not text:
        return ""

    text = str(text).strip()

    # Remove excessive whitespace
    text = " ".join(
        text.split()
    )

    return text


def get_category_label(category):
    """
    Convert internal category to Arabic label.
    """

    if not category:
        return "كرة القدم"

    return CATEGORY_LABELS.get(
        category,
        "كرة القدم",
    )


def build_post_title(news):
    """
    Build the Arabic post title.
    """

    title = (
        news.get("arabic_title")
        or news.get("title")
        or ""
    )

    return clean_text(title)


def build_post_summary(news):
    """
    Build the Arabic summary.
    """

    summary = (
        news.get("arabic_summary")
        or news.get("summary")
        or ""
    )

    return clean_text(summary)


def build_post_text(news):
    """
    Build final Facebook post.
    """

    title = build_post_title(news)
    summary = build_post_summary(news)

    category = get_category_label(
        news.get("category")
    )

    source = clean_text(
        news.get("source")
    )

    parts = []

    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------

    if title:
        parts.append(
            f"🚨 {title}"
        )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    if summary:

        # Keep posts reasonably concise.
        if len(summary) > 500:
            summary = summary[:497].rstrip() + "..."

        parts.append(
            f"📝 {summary}"
        )

    # --------------------------------------------------------
    # Category + Source
    # --------------------------------------------------------

    parts.append(
        f"🏷️ {category}"
    )

    if source:
        parts.append(
            f"🌐 المصدر: {source}"
        )

    # --------------------------------------------------------
    # Page branding
    # --------------------------------------------------------

    parts.append(
        "📍 نبض مدريد"
    )

    return "\n\n".join(parts)


def format_news_item(news):
    """
    Format one news item for Facebook.
    """

    post_title = build_post_title(
        news
    )

    post_text = build_post_text(
        news
    )

    news["post_title"] = post_title
    news["post_text"] = post_text

    return news


def format_news(news_list):
    """
    Format all news items.
    """

    formatted_news = []

    for news in news_list:

        try:

            formatted = format_news_item(
                news
            )

            # Do not publish completely empty posts
            if not formatted.get(
                "post_title"
            ):
                continue

            if not formatted.get(
                "post_text"
            ):
                continue

            formatted_news.append(
                formatted
            )

        except Exception as e:

            print(
                f"⚠️ Formatting error: {e}"
            )

    print(
        f"📰 Formatted news: "
        f"{len(formatted_news)}"
    )

    return formatted_news

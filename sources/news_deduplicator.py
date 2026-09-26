# ============================================================
# News Deduplicator
# Prevent duplicate football stories from multiple sources
# ============================================================

import re
import difflib
import unicodedata


SIMILARITY_THRESHOLD = 0.82


def normalize_title(title):
    """
    Normalize title for comparison.
    """

    if not title:
        return ""

    text = str(title).lower().strip()

    # Remove Arabic diacritics
    text = re.sub(
        r"[\u064B-\u065F\u0670]",
        "",
        text,
    )

    # Normalize Arabic characters
    text = text.replace("أ", "ا")
    text = text.replace("إ", "ا")
    text = text.replace("آ", "ا")
    text = text.replace("ى", "ي")
    text = text.replace("ة", "ه")

    # Remove URLs
    text = re.sub(
        r"https?://\S+",
        " ",
        text,
    )

    # Remove punctuation
    text = re.sub(
        r"[^\w\s]",
        " ",
        text,
        flags=re.UNICODE,
    )

    # Normalize whitespace
    text = re.sub(
        r"\s+",
        " ",
        text,
    ).strip()

    return text


def title_similarity(title1, title2):
    """
    Calculate similarity between two titles.
    """

    normalized1 = normalize_title(title1)
    normalized2 = normalize_title(title2)

    if not normalized1 or not normalized2:
        return 0.0

    if normalized1 == normalized2:
        return 1.0

    return difflib.SequenceMatcher(
        None,
        normalized1,
        normalized2,
    ).ratio()


def extract_keywords(title):
    """
    Extract useful keywords from a title.
    """

    normalized = normalize_title(title)

    if not normalized:
        return set()

    words = normalized.split()

    # Ignore very common words
    stop_words = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "to",
        "of",
        "in",
        "on",
        "for",
        "with",
        "from",
        "at",
        "is",
        "are",
        "was",
        "were",
        "this",
        "that",

        "في",
        "من",
        "الى",
        "إلى",
        "عن",
        "على",
        "مع",
        "هذا",
        "هذه",
        "هو",
        "هي",
        "بعد",
        "قبل",
        "خلال",
        "و",
        "او",
        "أو",
        "ان",
        "أن",
    }

    return {
        word
        for word in words
        if len(word) >= 3
        and word not in stop_words
    }


def keyword_similarity(title1, title2):
    """
    Compare important keywords between two titles.
    """

    words1 = extract_keywords(title1)
    words2 = extract_keywords(title2)

    if not words1 or not words2:
        return 0.0

    intersection = words1.intersection(words2)
    union = words1.union(words2)

    if not union:
        return 0.0

    return len(intersection) / len(union)


def is_same_story(news1, news2):
    """
    Determine whether two news items are probably
    reporting the same story.
    """

    title1 = news1.get("title", "")
    title2 = news2.get("title", "")

    # Exact URL match
    url1 = str(news1.get("url", "")).strip()
    url2 = str(news2.get("url", "")).strip()

    if url1 and url2 and url1 == url2:
        return True

    # Exact normalized title
    normalized1 = normalize_title(title1)
    normalized2 = normalize_title(title2)

    if normalized1 and normalized1 == normalized2:
        return True

    # Title similarity
    similarity = title_similarity(
        title1,
        title2,
    )

    if similarity >= SIMILARITY_THRESHOLD:
        return True

    # Keyword similarity
    keyword_score = keyword_similarity(
        title1,
        title2,
    )

    # A high keyword overlap can indicate
    # the same story even with different wording.
    if keyword_score >= 0.72:
        return True

    return False


def choose_best_news(news1, news2):
    """
    Select the preferred version of a duplicate story.

    Lower priority number = higher source priority.
    """

    priority1 = news1.get("priority", 5)
    priority2 = news2.get("priority", 5)

    try:
        priority1 = int(priority1)
    except (TypeError, ValueError):
        priority1 = 5

    try:
        priority2 = int(priority2)
    except (TypeError, ValueError):
        priority2 = 5

    # Better priority wins
    if priority1 < priority2:
        return news1

    if priority2 < priority1:
        return news2

    # If same priority, prefer the item with
    # a real image.
    image1 = bool(
        news1.get("image_url")
    )

    image2 = bool(
        news2.get("image_url")
    )

    if image1 and not image2:
        return news1

    if image2 and not image1:
        return news2

    # Prefer longer summary when source quality
    # and priority are equal.
    summary1 = str(
        news1.get("summary", "")
    )

    summary2 = str(
        news2.get("summary", "")
    )

    if len(summary1) > len(summary2):
        return news1

    return news2


def deduplicate_news(news_list):
    """
    Remove duplicate stories.

    Keeps the best source version of each story.
    """

    if not news_list:
        return []

    unique_news = []

    print(
        f"\n🔎 Deduplicating "
        f"{len(news_list)} news items..."
    )

    duplicates = 0

    for news in news_list:

        duplicate_index = None

        for index, existing in enumerate(
            unique_news
        ):

            if is_same_story(
                news,
                existing,
            ):

                duplicate_index = index
                break

        if duplicate_index is None:

            unique_news.append(news)

        else:

            existing = unique_news[
                duplicate_index
            ]

            best = choose_best_news(
                news,
                existing,
            )

            unique_news[
                duplicate_index
            ] = best

            duplicates += 1

    print(
        f"✅ Unique news: "
        f"{len(unique_news)}"
    )

    print(
        f"♻️ Duplicates removed: "
        f"{duplicates}"
    )

    return unique_news

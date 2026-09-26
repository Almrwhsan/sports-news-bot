# ============================================================
# Source Manager
# Fast, Safe and Parallel RSS Fetching
# ============================================================

import feedparser
from concurrent.futures import ThreadPoolExecutor, as_completed


# عدد المصادر التي يمكن جلبها في نفس الوقت
MAX_WORKERS = 8


def extract_image(entry):
    """
    Extract image URL from common RSS/Media formats.
    """

    # media_content
    media_content = entry.get("media_content", [])
    if media_content:
        for media in media_content:
            if isinstance(media, dict):
                url = media.get("url")
                if url:
                    return url

    # media_thumbnail
    media_thumbnail = entry.get("media_thumbnail", [])
    if media_thumbnail:
        for media in media_thumbnail:
            if isinstance(media, dict):
                url = media.get("url")
                if url:
                    return url

    # enclosures
    enclosures = entry.get("enclosures", [])
    if enclosures:
        for enclosure in enclosures:
            if isinstance(enclosure, dict):
                url = enclosure.get("href") or enclosure.get("url")
                if url:
                    return url

    # links
    links = entry.get("links", [])
    for link in links:
        if not isinstance(link, dict):
            continue

        link_type = str(link.get("type", "")).lower()

        if link_type.startswith("image/"):
            url = link.get("href")
            if url:
                return url

    return None


def extract_media_type(entry):
    """
    Determine media type when available.
    """

    media_content = entry.get("media_content", [])

    if media_content:
        for media in media_content:
            if isinstance(media, dict):
                media_type = media.get("type")
                if media_type:
                    return media_type

    enclosures = entry.get("enclosures", [])

    if enclosures:
        for enclosure in enclosures:
            if isinstance(enclosure, dict):
                media_type = enclosure.get("type")
                if media_type:
                    return media_type

    return None


def fetch_source(source):
    """
    Fetch one RSS source safely.

    A failure in one source must never stop the entire bot.
    """

    if not source.get("enabled", True):
        print(f"⏭️ Disabled source: {source.get('name', 'Unknown')}")
        return []

    feed_url = source.get("feed")

    if not feed_url:
        print(f"⚠️ No feed URL: {source.get('name', 'Unknown')}")
        return []

    source_name = source.get("name", "Unknown Source")

    print(f"🌐 Fetching: {source_name}")

    try:
        feed = feedparser.parse(feed_url)

        # feedparser normally exposes bozo when the feed has parsing problems
        if getattr(feed, "bozo", False):
            print(
                f"⚠️ Feed warning: {source_name} - "
                f"{getattr(feed, 'bozo_exception', 'unknown error')}"
            )

        entries = getattr(feed, "entries", [])

        if not entries:
            print(f"⚠️ No entries: {source_name}")
            return []

        news_items = []

        for entry in entries:

            title = entry.get("title", "").strip()
            url = (
                entry.get("link")
                or entry.get("id")
                or ""
            ).strip()

            if not title or not url:
                continue

            summary = (
                entry.get("summary")
                or entry.get("description")
                or ""
            ).strip()

            published = (
                entry.get("published")
                or entry.get("updated")
                or ""
            ).strip()

            image_url = extract_image(entry)
            media_type = extract_media_type(entry)

            item = {
                "title": title,
                "url": url,
                "summary": summary,
                "published": published,
                "source": source_name,
                "language": source.get("language", "unknown"),
                "type": source.get("type", "global"),
                "category": source.get("category", "football"),
                "priority": source.get("priority", 5),
                "image_url": image_url,
                "media_type": media_type,
            }

            news_items.append(item)

        print(
            f"✅ {source_name}: "
            f"{len(news_items)} entries"
        )

        return news_items

    except Exception as e:

        print(
            f"❌ Source failed: {source_name} | "
            f"{type(e).__name__}: {e}"
        )

        return []


def fetch_all_sources(sources):
    """
    Fetch all enabled sources in parallel.

    The final result is sorted by source priority
    so the rest of the bot continues receiving
    predictable ordering.
    """

    if not sources:
        print("⚠️ No sources configured.")
        return []

    enabled_sources = [
        source
        for source in sources
        if source.get("enabled", True)
    ]

    if not enabled_sources:
        print("⚠️ No enabled sources.")
        return []

    print(
        f"\n🚀 Starting parallel fetch "
        f"for {len(enabled_sources)} sources..."
    )

    all_news = []

    # Do not create more workers than necessary
    workers = min(MAX_WORKERS, len(enabled_sources))

    with ThreadPoolExecutor(max_workers=workers) as executor:

        future_to_source = {
            executor.submit(fetch_source, source): source
            for source in enabled_sources
        }

        for future in as_completed(future_to_source):

            source = future_to_source[future]
            source_name = source.get("name", "Unknown Source")

            try:
                news_items = future.result()

                if news_items:
                    all_news.extend(news_items)

            except Exception as e:

                print(
                    f"❌ Unexpected error from "
                    f"{source_name}: {e}"
                )

    # Keep priority ordering predictable
    all_news.sort(
        key=lambda item: (
            item.get("priority", 5),
            item.get("published", ""),
        ),
        reverse=False,
    )

    print(
        f"\n📊 Total fetched news: "
        f"{len(all_news)}"
    )

    return all_news

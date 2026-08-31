import json
import os
import feedparser


RSS_URL = "https://feeds.bbci.co.uk/sport/football/rss.xml"
NEWS_FILE = "news.json"
MAX_NEWS = 500


def load_news():
    if not os.path.exists(NEWS_FILE):
        return []

    try:
        with open(NEWS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return []


def save_news(news):
    news = news[:MAX_NEWS]

    with open(NEWS_FILE, "w", encoding="utf-8") as file:
        json.dump(news, file, ensure_ascii=False, indent=2)


def get_football_news():
    print("Fetching football news...")

    feed = feedparser.parse(RSS_URL)

    if feed.bozo:
        print("Warning: RSS feed may have a problem.")

    return feed.entries


def main():
    print("===================================")
    print("      SPORTS NEWS BOT")
    print("===================================")

    old_news = load_news()
    old_urls = {item["url"] for item in old_news}

    entries = get_football_news()

    new_news = []

    for article in entries:

        title = article.get("title", "").strip()
        url = article.get("link", "").strip()
        published = article.get("published", "Unknown time").strip()

        # RSS قد يسمي الملخص description أو summary
        summary = article.get("summary", "").strip()

        if not title or not url:
            continue

        if url in old_urls:
            continue

        news_item = {
            "title": title,
            "summary": summary,
            "url": url,
            "published": published,
            "source": "BBC Sport Football",
            "language": "en",
            "processed": False
        }

        new_news.append(news_item)
        old_urls.add(url)

    print(f"Total RSS news: {len(entries)}")
    print(f"Previously saved: {len(old_news)}")
    print(f"NEW NEWS: {len(new_news)}")
    print()

    if new_news:

        print("🆕 New football news:")
        print()

        for index, article in enumerate(new_news, start=1):

            print(f"{index}. {article['title']}")
            print(f"   Source: {article['source']}")
            print(f"   Published: {article['published']}")

            if article["summary"]:
                print(f"   Summary: {article['summary'][:300]}")
            else:
                print("   Summary: No summary available")

            print(f"   URL: {article['url']}")
            print()

    else:
        print("No new news.")

    combined_news = new_news + old_news

    save_news(combined_news)

    print("===================================")
    print("Bot finished successfully!")
    print("Saved news:", len(combined_news[:MAX_NEWS]))
    print("===================================")


if __name__ == "__main__":
    main()    return feed.entries


def main():
    print("===================================")
    print("      SPORTS NEWS BOT")
    print("===================================")

    old_news = load_news()
    old_urls = {item["url"] for item in old_news}

    entries = get_football_news()

    new_news = []

    for article in entries:
        title = article.get("title", "").strip()
        url = article.get("link", "").strip()
        published = article.get("published", "Unknown time")

        if not title or not url:
            continue

        if url in old_urls:
            continue

        news_item = {
            "title": title,
            "url": url,
            "published": published,
            "source": "BBC Sport Football"
        }

        new_news.append(news_item)
        old_urls.add(url)

    print(f"Total RSS news: {len(entries)}")
    print(f"Previously saved: {len(old_news)}")
    print(f"NEW NEWS: {len(new_news)}")
    print()

    if new_news:
        print("🆕 New football news:")
        print()

        for index, article in enumerate(new_news, start=1):
            print(f"{index}. {article['title']}")
            print(f"   Source: {article['source']}")
            print(f"   Published: {article['published']}")
            print(f"   URL: {article['url']}")
            print()

    else:
        print("No new news.")

    # إضافة الأخبار الجديدة إلى الذاكرة
    combined_news = new_news + old_news

    # الاحتفاظ بآخر 500 خبر فقط
    save_news(combined_news)

    print("===================================")
    print("Bot finished successfully!")
    print("Saved news:", len(combined_news[:MAX_NEWS]))
    print("===================================")


if __name__ == "__main__":
    main()
    print("===================================")
    print("Bot finished successfully!")
    print("===================================")


if __name__ == "__main__":
    main()

import feedparser


RSS_URL = "https://feeds.bbci.co.uk/sport/football/rss.xml"


def get_football_news():
    print("Fetching football news...")
    print()

    feed = feedparser.parse(RSS_URL)

    if feed.bozo:
        print("Warning: RSS feed may have a problem.")

    print(f"Source: BBC Sport Football")
    print(f"News found: {len(feed.entries)}")
    print()

    for index, article in enumerate(feed.entries[:10], start=1):
        title = article.get("title", "No title")
        url = article.get("link", "No URL")
        published = article.get("published", "Unknown time")

        print(f"{index}. {title}")
        print(f"   URL: {url}")
        print(f"   Published: {published}")
        print()


def main():
    print("===================================")
    print("      SPORTS NEWS BOT")
    print("===================================")

    get_football_news()

    print("===================================")
    print("Bot finished successfully!")
    print("===================================")


if __name__ == "__main__":
    main()

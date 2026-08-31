import json
import os
import feedparser
from google import genai


RSS_URL = "https://feeds.bbci.co.uk/sport/football/rss.xml"
NEWS_FILE = "news.json"
MAX_NEWS = 500

GEMINI_MODEL = "gemini-3.6-flash"


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


IMPORTANT_KEYWORDS = [
    "transfer",
    "transfers",
    "signs",
    "signed",
    "deal",
    "move",
    "joins",
    "leaves",
    "match",
    "win",
    "wins",
    "lost",
    "loss",
    "draw",
    "goal",
    "goals",
    "final",
    "league",
    "champions",
    "injury",
    "injured",
    "returns",
    "sacked",
    "appointed",
    "manager",
    "contract",
    "Manchester United",
    "Manchester City",
    "Liverpool",
    "Chelsea",
    "Arsenal",
    "Tottenham",
    "Real Madrid",
    "Barcelona",
    "Bayern",
    "Juventus",
    "Inter Milan",
    "AC Milan",
    "PSG",
    "Premier League",
    "Champions League",
    "Europa League",
    "World Cup",
    "La Liga",
    "Serie A",
    "Bundesliga",
]


def is_important_news(title, summary):
    text = f"{title} {summary}".lower()

    return any(
        keyword.lower() in text
        for keyword in IMPORTANT_KEYWORDS
    )


def generate_arabic_content(title, summary, source):
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        print("WARNING: GEMINI_API_KEY is not configured.")
        return None

    try:
        client = genai.Client(api_key=api_key)

        prompt = f"""
أنت محرر أخبار كرة قدم لصفحة رياضية عربية.

حوّل المعلومات التالية إلى محتوى عربي مختصر وطبيعي.

القواعد:
- لا تخترع أي معلومات.
- لا تضف أرقامًا أو تصريحات غير موجودة.
- لا تترجم ترجمة حرفية.
- حافظ على أسماء اللاعبين والأندية.
- اجعل العنوان جذابًا بدون مبالغة.
- اجعل الملخص من 2 إلى 4 جمل.
- اجعل المنشور مناسبًا للنشر على Facebook.
- لا تضع الرابط داخل النص.

أعد النتيجة بهذا الشكل:

TITLE:
العنوان العربي

SUMMARY:
الملخص العربي

POST:
المنشور العربي الكامل

المصدر: {source}

العنوان الأصلي:
{title}

الملخص الأصلي:
{summary}
"""

        interaction = client.interactions.create(
            model=GEMINI_MODEL,
            input=prompt
        )

        return interaction.output_text.strip()

    except Exception as error:
        print(f"Gemini error: {error}")
        return None


def parse_gemini_response(text):
    if not text:
        return None

    title = ""
    summary = ""
    post = ""

    if "TITLE:" in text:
        after_title = text.split("TITLE:", 1)[1]

        if "SUMMARY:" in after_title:
            title = after_title.split("SUMMARY:", 1)[0].strip()

            after_summary = after_title.split("SUMMARY:", 1)[1]

            if "POST:" in after_summary:
                summary = after_summary.split("POST:", 1)[0].strip()
                post = after_summary.split("POST:", 1)[1].strip()
            else:
                summary = after_summary.strip()

    if not title:
        title = text[:200].strip()

    return {
        "title_ar": title,
        "summary_ar": summary,
        "post_ar": post
    }


def main():
    print("===================================")
    print("      SPORTS NEWS BOT")
    print("===================================")

    old_news = load_news()

    old_urls = {
        item.get("url")
        for item in old_news
        if item.get("url")
    }

    entries = get_football_news()

    new_news = []

    for article in entries:
        title = article.get("title", "").strip()
        url = article.get("link", "").strip()
        published = article.get(
            "published",
            "Unknown time"
        ).strip()
        summary = article.get("summary", "").strip()

        if not title or not url:
            continue

        if url in old_urls:
            continue

        important = is_important_news(
            title,
            summary
        )

        news_item = {
            "title": title,
            "summary": summary,
            "url": url,
            "published": published,
            "source": "BBC Sport Football",
            "language": "en",
            "important": important,
            "processed": False
        }

        if important:
            print()
            print("⭐ Important news detected:")
            print(title)

            print("Sending to Gemini...")

            generated = generate_arabic_content(
                title,
                summary,
                "BBC Sport Football"
            )

            if generated:
                parsed = parse_gemini_response(
                    generated
                )

                if parsed:
                    news_item.update(parsed)
                    news_item["processed"] = True

                    print(
                        "✅ Arabic content generated successfully."
                    )

                    print()
                    print("Arabic title:")
                    print(news_item["title_ar"])

                    print()
                    print("Arabic summary:")
                    print(news_item["summary_ar"])

                    print()
                    print("Arabic post:")
                    print(news_item["post_ar"])

            else:
                print(
                    "⚠️ Gemini did not generate content."
                )

        else:
            print()
            print("Normal news - Gemini skipped:")
            print(title)

        new_news.append(news_item)
        old_urls.add(url)

    print()
    print(f"Total RSS news: {len(entries)}")
    print(f"Previously saved: {len(old_news)}")
    print(f"NEW NEWS: {len(new_news)}")

    combined_news = new_news + old_news

    save_news(combined_news)

    print()
    print("===================================")
    print("Bot finished successfully!")
    print(
        "Saved news:",
        len(combined_news[:MAX_NEWS])
    )
    print("===================================")


if __name__ == "__main__":
    main()

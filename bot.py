import json
import os
import re
from difflib import SequenceMatcher

import feedparser


NEWS_FILE = "news.json"
MAX_NEWS = 500


# ============================================================
# مصادر الأخبار
# ============================================================

RSS_SOURCES = [
    {
        "name": "BBC Sport Football",
        "url": "https://feeds.bbci.co.uk/sport/football/rss.xml",
        "language": "en",
    },

    {
        "name": "Al-Jazirah Sports",
        "url": "https://www.al-jazirah.com/rss/",
        "language": "ar",
    },
]


# ============================================================
# كلمات تساعدنا على التأكد أن الخبر متعلق بكرة القدم
# ============================================================

FOOTBALL_KEYWORDS = [
    # English
    "football",
    "soccer",
    "premier league",
    "champions league",
    "europa league",
    "conference league",
    "world cup",
    "transfer",
    "transfers",
    "signing",
    "contract",
    "manager",
    "coach",
    "striker",
    "midfielder",
    "defender",
    "goalkeeper",
    "match",
    "fixture",
    "club",

    # Arabic
    "كرة القدم",
    "الدوري الإنجليزي",
    "الدوري الإسباني",
    "الدوري الإيطالي",
    "الدوري الألماني",
    "دوري أبطال أوروبا",
    "الدوري الأوروبي",
    "كأس العالم",
    "انتقال",
    "صفقة",
    "تعاقد",
    "مباراة",
    "هدف",
    "مدرب",
    "لاعب",
    "نادي",
    "إصابة",
]


# ============================================================
# تحميل الأخبار القديمة
# ============================================================

def load_news():
    if not os.path.exists(NEWS_FILE):
        return []

    try:
        with open(NEWS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

            if isinstance(data, list):
                return data

            return []

    except (json.JSONDecodeError, OSError):
        return []


# ============================================================
# حفظ الأخبار
# ============================================================

def save_news(news):

    news = news[:MAX_NEWS]

    with open(NEWS_FILE, "w", encoding="utf-8") as file:
        json.dump(
            news,
            file,
            ensure_ascii=False,
            indent=2
        )


# ============================================================
# تنظيف النص
# ============================================================

def clean_text(text):

    if not text:
        return ""

    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# تطبيع العنوان للمقارنة
# ============================================================

def normalize_title(title):

    title = title.lower()

    title = re.sub(
        r"[^a-zA-Z0-9\u0600-\u06FF\s]",
        " ",
        title
    )

    title = re.sub(r"\s+", " ", title)

    return title.strip()


# ============================================================
# اكتشاف كرة القدم
# ============================================================

def is_football_news(title, summary):

    text = f"{title} {summary}".lower()

    for keyword in FOOTBALL_KEYWORDS:

        if keyword.lower() in text:
            return True

    return False


# ============================================================
# مقارنة الأخبار
# ============================================================

def similar_titles(title1, title2):

    a = normalize_title(title1)
    b = normalize_title(title2)

    if not a or not b:
        return False

    similarity = SequenceMatcher(
        None,
        a,
        b
    ).ratio()

    return similarity >= 0.82


# ============================================================
# تحديد تصنيف الخبر
# ============================================================

def detect_category(title, summary):

    text = f"{title} {summary}".lower()

    transfer_words = [
        "transfer",
        "transfers",
        "signing",
        "deal",
        "joins",
        "move",
        "انتقال",
        "صفقة",
        "تعاقد",
        "ينضم",
        "ينتقل",
    ]

    injury_words = [
        "injury",
        "injured",
        "fitness",
        "إصابة",
        "مصاب",
    ]

    match_words = [
        "match",
        "fixture",
        "result",
        "win",
        "draw",
        "defeat",
        "مباراة",
        "نتيجة",
        "فوز",
        "تعادل",
        "خسارة",
    ]

    if any(word in text for word in transfer_words):
        return "transfers"

    if any(word in text for word in injury_words):
        return "injuries"

    if any(word in text for word in match_words):
        return "matches"

    return "football"


# ============================================================
# عنوان عربي مبدئي
#
# ملاحظة:
# هذه ليست ترجمة بالذكاء الاصطناعي.
# سنطورها لاحقًا.
# ============================================================

def build_arabic_post(title, summary, category):

    category_labels = {
        "transfers": "انتقالات",
        "injuries": "إصابات",
        "matches": "مباريات",
        "football": "كرة القدم",
    }

    label = category_labels.get(
        category,
        "كرة القدم"
    )

    # الأخبار العربية تبقى كما هي تقريبًا.
    if re.search(r"[\u0600-\u06FF]", title):

        post_title = title

        body = summary

    else:

        # لا ندّعي ترجمة العنوان الإنجليزي.
        # نحتفظ به مؤقتًا إلى أن نبني نظام الترجمة.
        post_title = title

        body = summary

    post = (
        f"⚽ {label}\n\n"
        f"🔴 {post_title}\n\n"
        f"{body}\n\n"
        f"⚽ {label}"
    )

    return {
        "post_title": post_title,
        "post_body": body,
        "post_text": post,
    }


# ============================================================
# جلب مصدر واحد
# ============================================================

def fetch_source(source):

    print()
    print("-----------------------------------")
    print(f"Fetching: {source['name']}")
    print("-----------------------------------")

    try:

        feed = feedparser.parse(
            source["url"]
        )

        if feed.bozo:
            print("Warning: RSS feed may have a problem.")

        print(
            f"Entries received: "
            f"{len(feed.entries)}"
        )

        return feed.entries

    except Exception as error:

        print(
            f"Source error: {error}"
        )

        return []


# ============================================================
# البرنامج الرئيسي
# ============================================================

def main():

    print("===================================")
    print("      SPORTS NEWS BOT")
    print("===================================")

    old_news = load_news()

    print(
        f"Previously saved: "
        f"{len(old_news)}"
    )

    # --------------------------------------------------------
    # الروابط الموجودة
    # --------------------------------------------------------

    old_urls = {
        item.get("url")
        for item in old_news
        if item.get("url")
    }

    new_news = []

    # --------------------------------------------------------
    # جلب المصادر
    # --------------------------------------------------------

    for source in RSS_SOURCES:

        entries = fetch_source(source)

        for article in entries:

            title = clean_text(
                article.get("title", "")
            )

            url = clean_text(
                article.get("link", "")
            )

            summary = clean_text(
                article.get("summary", "")
            )

            published = clean_text(
                article.get(
                    "published",
                    "Unknown time"
                )
            )

            if not title or not url:
                continue

            # ------------------------------------------------
            # منع تكرار الرابط
            # ------------------------------------------------

            if url in old_urls:
                continue

            # ------------------------------------------------
            # فلترة كرة القدم
            # ------------------------------------------------

            if not is_football_news(
                title,
                summary
            ):
                continue

            # ------------------------------------------------
            # منع التكرار بين المصادر
            # ------------------------------------------------

            duplicate = False

            for existing in (
                new_news + old_news
            ):

                existing_title = existing.get(
                    "title",
                    ""
                )

                if similar_titles(
                    title,
                    existing_title
                ):

                    duplicate = True
                    break

            if duplicate:
                continue

            # ------------------------------------------------
            # تصنيف الخبر
            # ------------------------------------------------

            category = detect_category(
                title,
                summary
            )

            # ------------------------------------------------
            # بناء المنشور
            # ------------------------------------------------

            post = build_arabic_post(
                title,
                summary,
                category
            )

            news_item = {

                # البيانات الأصلية
                "title": title,
                "summary": summary,
                "url": url,
                "published": published,

                # المصدر داخلي فقط
                "source": source["name"],
                "language": source["language"],

                # التصنيف
                "category": category,

                # بيانات المنشور
                "post_title": post[
                    "post_title"
                ],

                "post_body": post[
                    "post_body"
                ],

                "post_text": post[
                    "post_text"
                ],

                # حالة المعالجة
                "processed": False,
                "published_to_facebook": False,

                # الصورة سنضيفها لاحقًا
                "image": None,
                "image_source": None,
                "image_license": None,
            }

            new_news.append(
                news_item
            )

            old_urls.add(url)

    # ========================================================
    # النتائج
    # ========================================================

    print()
    print("===================================")
    print(
        f"NEW FOOTBALL NEWS: "
        f"{len(new_news)}"
    )
    print("===================================")

    if new_news:

        for index, article in enumerate(
            new_news,
            start=1
        ):

            print()
            print(
                f"🆕 NEWS #{index}"
            )

            print(
                f"Source: "
                f"{article['source']}"
            )

            print(
                f"Original title: "
                f"{article['title']}"
            )

            print(
                f"Category: "
                f"{article['category']}"
            )

            print()
            print(
                "POST PREVIEW:"
            )

            print(
                article["post_text"]
            )

            print()
            print(
                f"Internal URL: "
                f"{article['url']}"
            )

    else:

        print(
            "No new football news."
        )

    # ========================================================
    # حفظ
    # ========================================================

    combined_news = (
        new_news +
        old_news
    )

    save_news(
        combined_news
    )

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

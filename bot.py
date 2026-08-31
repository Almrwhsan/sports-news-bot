import json
import os
import re
from difflib import SequenceMatcher
from datetime import datetime, timezone

import feedparser


# ============================================================
# إعدادات
# ============================================================

NEWS_FILE = "news.json"

MAX_NEWS_PER_SOURCE = 10
MAX_NEW_NEWS = 20
MAX_NEWS = 500

MAX_SUMMARY_LENGTH = 450


# ============================================================
# المصادر
# ============================================================

RSS_SOURCES = [
    {
        "name": "BBC Sport Football",
        "url": "https://feeds.bbci.co.uk/sport/football/rss.xml",
        "language": "en",
    },

    {
        "name": "Al-Anba Arabic Sports",
        "url": "https://www.alanba.com.kw/rss/arabic-sports",
        "language": "ar",
    },

    {
        "name": "Al Jadeed Football",
        "url": "https://www.aljadeed.tv/Rss/News/1065/كرة-القدم/ar",
        "language": "ar",
    },
]


# ============================================================
# كلمات كرة القدم
# ============================================================

FOOTBALL_KEYWORDS = [
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
    "league",
    "cup",

    "كرة القدم",
    "الدوري الإنجليزي",
    "الدوري الإسباني",
    "الدوري الإيطالي",
    "الدوري الألماني",
    "الدوري الفرنسي",
    "الدوري السعودي",
    "الدوري الإماراتي",
    "الدوري القطري",
    "الدوري المصري",
    "الدوري المغربي",
    "الدوري التونسي",
    "دوري أبطال أوروبا",
    "الدوري الأوروبي",
    "دوري المؤتمر",
    "كأس العالم",
    "انتقال",
    "صفقة",
    "تعاقد",
    "ينضم",
    "ينتقل",
    "مباراة",
    "هدف",
    "مدرب",
    "لاعب",
    "نادي",
    "إصابة",
    "دوري",
    "كأس",
]


# ============================================================
# تحميل الأخبار
# ============================================================

def load_news():

    if not os.path.exists(NEWS_FILE):
        return []

    try:

        with open(
            NEWS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, list):
                return data

            return []

    except (
        json.JSONDecodeError,
        OSError
    ):

        return []


# ============================================================
# حفظ الأخبار
# ============================================================

def save_news(news):

    news = news[:MAX_NEWS]

    with open(
        NEWS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            news,
            file,
            ensure_ascii=False,
            indent=2
        )


# ============================================================
# تنظيف HTML
# ============================================================

def clean_text(text):

    if not text:
        return ""

    text = str(text)

    # HTML
    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

    # HTML entities الشائعة
    text = (
        text.replace("&nbsp;", " ")
            .replace("&amp;", "&")
            .replace("&quot;", '"')
            .replace("&#39;", "'")
    )

    # مسافات متعددة
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# تنظيف ملخص RSS
# ============================================================

def clean_summary(text):

    text = clean_text(text)

    if not text:
        return ""

    # إزالة عبارات RSS الشائعة
    unwanted = [
        "Read more",
        "اقرأ المزيد",
        "تابع المزيد",
        "المزيد",
    ]

    for phrase in unwanted:

        text = re.sub(
            re.escape(phrase),
            "",
            text,
            flags=re.IGNORECASE
        )

    # إزالة كلمة news التي تظهر أحيانًا كجزء زائد
    text = re.sub(
        r"\s+(news|النيوز)\s*$",
        "",
        text,
        flags=re.IGNORECASE
    )

    # تنظيف علامات زائدة في النهاية
    text = re.sub(
        r"[\s\-–—|:،]+$",
        "",
        text
    )

    return text.strip()


# ============================================================
# تطبيع العنوان
# ============================================================

def normalize_title(title):

    title = clean_text(title).lower()

    # إزالة التشكيل
    title = re.sub(
        r"[\u064B-\u065F\u0670]",
        "",
        title
    )

    # توحيد الحروف
    title = title.replace("أ", "ا")
    title = title.replace("إ", "ا")
    title = title.replace("آ", "ا")
    title = title.replace("ى", "ي")
    title = title.replace("ة", "ه")

    # إزالة علامات الترقيم
    title = re.sub(
        r"[^a-zA-Z0-9\u0600-\u06FF\s]",
        " ",
        title
    )

    title = re.sub(
        r"\s+",
        " ",
        title
    )

    return title.strip()


# ============================================================
# تشابه العناوين
# ============================================================

def similar_titles(title1, title2):

    a = normalize_title(title1)
    b = normalize_title(title2)

    if not a or not b:
        return False

    if a == b:
        return True

    similarity = SequenceMatcher(
        None,
        a,
        b
    ).ratio()

    return similarity >= 0.82


# ============================================================
# فلترة كرة القدم
# ============================================================

def is_football_news(title, summary):

    text = f"{title} {summary}".lower()

    return any(
        keyword.lower() in text
        for keyword in FOOTBALL_KEYWORDS
    )


# ============================================================
# التصنيف
# ============================================================

def detect_category(title, summary):

    text = f"{title} {summary}".lower()

    if any(
        word in text
        for word in [
            "transfer",
            "transfers",
            "signing",
            "deal",
            "joins",
            "join",
            "move",
            "انتقال",
            "صفقة",
            "تعاقد",
            "ينضم",
            "ينتقل",
        ]
    ):
        return "transfers"

    if any(
        word in text
        for word in [
            "injury",
            "injured",
            "fitness",
            "إصابة",
            "مصاب",
            "يغيب",
            "غياب",
        ]
    ):
        return "injuries"

    if any(
        word in text
        for word in [
            "national team",
            "world cup",
            "منتخب",
            "كأس العالم",
        ]
    ):
        return "national_teams"

    if any(
        word in text
        for word in [
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
    ):
        return "matches"

    return "football"


# ============================================================
# اسم التصنيف
# ============================================================

def category_label(category):

    labels = {
        "transfers": "انتقالات",
        "injuries": "إصابات",
        "matches": "مباريات",
        "national_teams": "منتخبات",
        "football": "كرة القدم",
    }

    return labels.get(
        category,
        "كرة القدم"
    )


# ============================================================
# تحديد ما إذا كان النص عربيًا
# ============================================================

def contains_arabic(text):

    if not text:
        return False

    return bool(
        re.search(
            r"[\u0600-\u06FF]",
            text
        )
    )


# ============================================================
# تنظيف العنوان العربي
# ============================================================

def clean_arabic_title(title):

    title = clean_text(title)

    if not title:
        return ""

    title = re.sub(
        r"\s+",
        " ",
        title
    )

    return title.strip()


# ============================================================
# إنشاء المنشور
# ============================================================

def build_post(
    title,
    summary,
    category,
    language
):

    label = category_label(category)

    title = clean_text(title)

    summary = clean_summary(summary)

    # --------------------------------------------------------
    # خبر عربي
    # --------------------------------------------------------

    if language == "ar" or contains_arabic(title):

        post_title = clean_arabic_title(
            title
        )

        body = summary

    # --------------------------------------------------------
    # خبر إنجليزي
    #
    # لا نترجمه هنا.
    # سنضيف محرك الترجمة في المرحلة التالية.
    # --------------------------------------------------------

    else:

        post_title = title
        body = summary

    # --------------------------------------------------------
    # حماية من الملخصات الطويلة
    # --------------------------------------------------------

    if len(body) > MAX_SUMMARY_LENGTH:

        body = (
            body[:MAX_SUMMARY_LENGTH - 3]
            .rstrip()
            + "..."
        )

    if not body:

        body = (
            "تطور جديد في عالم كرة القدم."
        )

    # --------------------------------------------------------
    # المنشور النهائي
    # --------------------------------------------------------

    post_text = (
        f"🔴 {post_title}\n\n"
        f"{body}\n\n"
        f"⚽ {label}"
    )

    return {
        "post_title": post_title,
        "post_body": body,
        "post_text": post_text,
    }


# ============================================================
# استخراج وقت الخبر
# ============================================================

def get_entry_timestamp(article):

    parsed_time = (
        article.get("published_parsed")
        or article.get("updated_parsed")
    )

    if parsed_time:

        try:

            dt = datetime(
                parsed_time.tm_year,
                parsed_time.tm_mon,
                parsed_time.tm_mday,
                parsed_time.tm_hour,
                parsed_time.tm_min,
                parsed_time.tm_sec,
                tzinfo=timezone.utc
            )

            return dt.timestamp()

        except (
            ValueError,
            TypeError
        ):

            pass

    return 0


# ============================================================
# جلب المصدر
# ============================================================

def fetch_source(source):

    print()
    print("-----------------------------------")
    print(
        f"Fetching: {source['name']}"
    )
    print("-----------------------------------")

    try:

        feed = feedparser.parse(
            source["url"]
        )

        if feed.bozo:

            print(
                "Warning: RSS feed may have a problem."
            )

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
# ترتيب الأخبار
# ============================================================

def sort_entries(entries):

    return sorted(
        entries,
        key=get_entry_timestamp,
        reverse=True
    )


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

    old_urls = {
        item.get("url")
        for item in old_news
        if item.get("url")
    }

    old_titles = [
        item.get("title", "")
        for item in old_news
        if item.get("title")
    ]

    new_news = []

    # ========================================================
    # المصادر
    # ========================================================

    for source in RSS_SOURCES:

        entries = fetch_source(source)

        entries = sort_entries(entries)

        entries = entries[
            :MAX_NEWS_PER_SOURCE
        ]

        source_added = 0

        for article in entries:

            if len(new_news) >= MAX_NEW_NEWS:
                break

            # ------------------------------------------------
            # البيانات
            # ------------------------------------------------

            title = clean_text(
                article.get(
                    "title",
                    ""
                )
            )

            url = clean_text(
                article.get(
                    "link",
                    ""
                )
            )

            summary = clean_summary(
                article.get(
                    "summary",
                    ""
                )
            )

            published = clean_text(
                article.get(
                    "published",
                    article.get(
                        "updated",
                        "Unknown time"
                    )
                )
            )

            # ------------------------------------------------
            # تحقق
            # ------------------------------------------------

            if not title or not url:
                continue

            if url in old_urls:
                continue

            if not is_football_news(
                title,
                summary
            ):
                continue

            # ------------------------------------------------
            # تكرار مع الأخبار القديمة
            # ------------------------------------------------

            duplicate = False

            for old_title in old_titles:

                if similar_titles(
                    title,
                    old_title
                ):

                    duplicate = True
                    break

            if duplicate:
                continue

            # ------------------------------------------------
            # تكرار داخل التشغيل الحالي
            # ------------------------------------------------

            for existing in new_news:

                if similar_titles(
                    title,
                    existing.get(
                        "title",
                        ""
                    )
                ):

                    duplicate = True
                    break

            if duplicate:
                continue

            # ------------------------------------------------
            # التصنيف
            # ------------------------------------------------

            category = detect_category(
                title,
                summary
            )

            # ------------------------------------------------
            # المنشور
            # ------------------------------------------------

            post = build_post(
                title,
                summary,
                category,
                source["language"]
            )

            # ------------------------------------------------
            # الخبر
            # ------------------------------------------------

            news_item = {

                "title": title,

                "summary": summary,

                "url": url,

                "published": published,

                "source": source["name"],

                "language": source["language"],

                "category": category,

                "post_title": post[
                    "post_title"
                ],

                "post_body": post[
                    "post_body"
                ],

                "post_text": post[
                    "post_text"
                ],

                "processed": False,

                "published_to_facebook": False,

                "image": None,

                "image_source": None,

                "image_license": None,
            }

            new_news.append(
                news_item
            )

            old_urls.add(url)

            source_added += 1

        print(
            f"New football news from "
            f"{source['name']}: "
            f"{source_added}"
        )

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

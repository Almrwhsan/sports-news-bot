import json
import os
import re
from difflib import SequenceMatcher
from datetime import datetime, timezone

import feedparser
from image_fetcher import fetch_news_image


# ============================================================
# إعدادات
# ============================================================

NEWS_FILE = "news.json"

MAX_NEWS_PER_SOURCE = 10
MAX_NEW_NEWS = 20
MAX_NEWS = 500

MAX_SUMMARY_LENGTH = 450


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
# كلمات تساعد على التأكد أن الخبر متعلق بكرة القدم
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
    "league",
    "cup",

    # Arabic
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
# محتوى رياضي لا نريد اعتباره خبرًا
# ============================================================

NON_NEWS_KEYWORDS = [

    # English
    "watch:",
    "watch ",
    "highlights",
    "highlight",
    "quiz",
    "quizzes",
    "podcast",
    "podcasts",
    "live:",
    "live ",
    "live stream",
    "listen:",
    "listen ",
    "video:",
    "video ",
    "sportscene",
    "preview:",
    "preview ",

    # Arabic
    "شاهد",
    "فيديو",
    "فيديو:",
    "ملخص",
    "ملخصات",
    "أهداف",
    "استمع",
    "بودكاست",
    "اختبار",
    "اختبارات",
    "بث مباشر",
]


# ============================================================
# تحميل الأخبار القديمة
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
# تنظيف النص
# ============================================================

def clean_text(text):

    if not text:
        return ""

    text = str(text)

    # إزالة HTML
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
        .replace("&apos;", "'")
    )

    # إزالة المسافات الزائدة
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

    unwanted = [
        "Read more",
        "اقرأ المزيد",
        "تابع المزيد",
    ]

    for phrase in unwanted:

        text = re.sub(
            re.escape(phrase),
            "",
            text,
            flags=re.IGNORECASE
        )

    # إزالة كلمات زائدة تظهر أحيانًا في نهاية RSS
    text = re.sub(
        r"\s+(news|النيوز)\s*$",
        "",
        text,
        flags=re.IGNORECASE
    )

    # إزالة علامات الترقيم الزائدة من النهاية
    text = re.sub(
        r"[\s\-–—|:،]+$",
        "",
        text
    )

    return text.strip()


# ============================================================
# تطبيع العنوان للمقارنة
# ============================================================

def normalize_title(title):

    title = clean_text(title).lower()

    # إزالة التشكيل العربي
    title = re.sub(
        r"[\u064B-\u065F\u0670]",
        "",
        title
    )

    # توحيد بعض الحروف العربية
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

    # مسافات متعددة
    title = re.sub(
        r"\s+",
        " ",
        title
    )

    return title.strip()


# ============================================================
# مقارنة الأخبار
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
# التأكد أن المحتوى خبر كرة قدم
# ============================================================

def is_football_news(title, summary):

    text = f"{title} {summary}".lower()

    return any(
        keyword.lower() in text
        for keyword in FOOTBALL_KEYWORDS
    )


# ============================================================
# استبعاد المحتوى غير الإخباري
# ============================================================

def is_non_news_content(title, summary):

    text = f"{title} {summary}".lower()

    return any(
        keyword.lower() in text
        for keyword in NON_NEWS_KEYWORDS
    )


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
        "join",
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
        "يغيب",
        "غياب",
    ]

    national_team_words = [
        "national team",
        "world cup",
        "منتخب",
        "كأس العالم",
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

    if any(
        word in text
        for word in transfer_words
    ):
        return "transfers"

    if any(
        word in text
        for word in injury_words
    ):
        return "injuries"

    if any(
        word in text
        for word in national_team_words
    ):
        return "national_teams"

    if any(
        word in text
        for word in match_words
    ):
        return "matches"

    return "football"


# ============================================================
# اسم التصنيف بالعربية
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
# التحقق من وجود اللغة العربية
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
# بناء المنشور
# ============================================================


    # ============================================================
# بناء المنشور النهائي
# ============================================================

def build_post(
    title,
    summary,
    category,
    language
):

    # --------------------------------------------------------
    # اسم التصنيف بالعربية
    # --------------------------------------------------------

    label = category_label(
        category
    )

    # --------------------------------------------------------
    # تنظيف العنوان
    # --------------------------------------------------------

    title = clean_text(
        title
    )

    # --------------------------------------------------------
    # تنظيف الملخص
    # --------------------------------------------------------

    summary = clean_summary(
        summary
    )

    # --------------------------------------------------------
    # العنوان
    #
    # حاليًا نحتفظ بالعنوان كما جاء من المصدر.
    # لا توجد ترجمة آلية في هذه المرحلة.
    # --------------------------------------------------------

    post_title = title

    # --------------------------------------------------------
    # الملخص
    # --------------------------------------------------------

    body = summary

    # --------------------------------------------------------
    # حماية من الملخصات الطويلة
    # --------------------------------------------------------

    if len(body) > MAX_SUMMARY_LENGTH:

        body = (
            body[
                :MAX_SUMMARY_LENGTH - 3
            ].rstrip()
            + "..."
        )

    # --------------------------------------------------------
    # في حالة عدم وجود ملخص
    # --------------------------------------------------------

    if not body:

        body = (
            "تطور جديد في عالم كرة القدم."
        )

    # --------------------------------------------------------
    # اسم الصفحة
    # --------------------------------------------------------

    page_name = "نبض مدريد"

    # --------------------------------------------------------
    # بناء المنشور النهائي
    # --------------------------------------------------------

    post_text = (
        f"🔴 {post_title}\n\n"
        f"{body}\n\n"
        f"⚽ {label}\n\n"
        f"📍 {page_name}"
    )

    # --------------------------------------------------------
    # إرجاع بيانات المنشور
    # --------------------------------------------------------

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
# جلب مصدر واحد
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
# ترتيب الأخبار من الأحدث إلى الأقدم
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

    # --------------------------------------------------------
    # الروابط الموجودة
    # --------------------------------------------------------

    old_urls = {
        item.get("url")
        for item in old_news
        if item.get("url")
    }

    # --------------------------------------------------------
    # عناوين الأخبار القديمة
    # --------------------------------------------------------

    old_titles = [
        item.get(
            "title",
            ""
        )
        for item in old_news
        if item.get("title")
    ]

    new_news = []

    # ========================================================
    # جلب المصادر
    # ========================================================

    for source in RSS_SOURCES:

        entries = fetch_source(
            source
        )

        # الأحدث أولًا
        entries = sort_entries(
            entries
        )

        # معالجة أحدث 10 أخبار من كل مصدر
        entries = entries[
            :MAX_NEWS_PER_SOURCE
        ]

        source_added = 0

        # ====================================================
        # معالجة الأخبار
        # ====================================================

        for article in entries:

            if len(new_news) >= MAX_NEW_NEWS:
                break

            # ------------------------------------------------
            # البيانات الأساسية
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
            # التحقق من البيانات
            # ------------------------------------------------

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
            # استبعاد المحتوى غير الإخباري
            # ------------------------------------------------

            if is_non_news_content(
                title,
                summary
            ):

                print(
                    f"Skipped non-news content: "
                    f"{title}"
                )

                continue

            # ------------------------------------------------
            # منع التكرار مع الأخبار القديمة
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
            # منع التكرار داخل التشغيل الحالي
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
            # تحديد التصنيف
            # ------------------------------------------------

            category = detect_category(
                title,
                summary
            )

            # ------------------------------------------------
            # بناء المنشور
            # ------------------------------------------------

            post = build_post(
                title,
                summary,
                category,
                source["language"]
            )

            # ------------------------------------------------
            # إنشاء سجل الخبر
            # ------------------------------------------------

            news_item = {

                # البيانات الأصلية
                "title": title,

                "summary": summary,

                "url": url,

                "published": published,

                # المصدر
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

                # الصور ستضاف لاحقًا
                "image": None,

                "image_source": None,

                "image_license": None,
            }
            # ------------------------------------------------
# تحميل صورة الخبر
# ------------------------------------------------

print()
print(
    "Searching for news image..."
)

image_result = fetch_news_image(
    title=title
)

if image_result:

    news_item["image"] = image_result[
        "image_path"
    ]

    news_item["image_source"] = image_result[
        "source_url"
    ]

    news_item["image_license"] = image_result[
        "license"
    ]

    print(
        "News image attached successfully."
    )

else:

    print(
        "No image found for this news."
    )

            # ------------------------------------------------
            # إضافة الخبر
            # ------------------------------------------------

            new_news.append(
                news_item
            )

            old_urls.add(
                url
            )

            old_titles.append(
                title
            )

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
    # دمج الأخبار الجديدة مع القديمة
    # ========================================================

    combined_news = (
        new_news +
        old_news
    )

    # ========================================================
    # حفظ الأخبار
    # ========================================================

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


# ============================================================
# تشغيل البرنامج
# ============================================================

if __name__ == "__main__":
    main()

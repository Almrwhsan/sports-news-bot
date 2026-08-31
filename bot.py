import json
import os
import re
from difflib import SequenceMatcher
from datetime import datetime, timezone

import feedparser


# ============================================================
# إعدادات البوت
# ============================================================

NEWS_FILE = "news.json"

# الحد الأقصى لكل مصدر في كل تشغيل
MAX_NEWS_PER_SOURCE = 10

# الحد الأقصى لإجمالي الأخبار الجديدة في التشغيل الواحد
MAX_NEW_NEWS = 20

# الحد الأقصى للأخبار المحفوظة
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
# تحميل الأخبار
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

    # إزالة HTML
    text = re.sub(r"<[^>]+>", " ", str(text))

    # إزالة المسافات الزائدة
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# تنظيف النص من بعض العناصر غير المرغوبة
# ============================================================

def clean_summary(text):

    text = clean_text(text)

    if not text:
        return ""

    # إزالة بعض العبارات الشائعة في خلاصات RSS
    unwanted_patterns = [
        r"Read more",
        r"اقرأ المزيد",
        r"تابع المزيد",
        r"المزيد",
    ]

    for pattern in unwanted_patterns:
        text = re.sub(
            pattern,
            "",
            text,
            flags=re.IGNORECASE
        )

    text = re.sub(r"\s+", " ", text)

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

    title = re.sub(r"\s+", " ", title)

    return title.strip()


# ============================================================
# مقارنة الأخبار
# ============================================================

def similar_titles(title1, title2):

    a = normalize_title(title1)
    b = normalize_title(title2)

    if not a or not b:
        return False

    # تطابق مباشر
    if a == b:
        return True

    similarity = SequenceMatcher(
        None,
        a,
        b
    ).ratio()

    return similarity >= 0.82


# ============================================================
# اكتشاف هل الخبر عن كرة القدم
# ============================================================

def is_football_news(title, summary):

    text = f"{title} {summary}".lower()

    for keyword in FOOTBALL_KEYWORDS:

        if keyword.lower() in text:
            return True

    return False


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

    national_team_words = [
        "national team",
        "world cup",
        "منتخب",
        "كأس العالم",
    ]

    if any(word in text for word in transfer_words):
        return "transfers"

    if any(word in text for word in injury_words):
        return "injuries"

    if any(word in text for word in national_team_words):
        return "national_teams"

    if any(word in text for word in match_words):
        return "matches"

    return "football"


# ============================================================
# اسم التصنيف بالعربية
# ============================================================

def get_category_label(category):

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
# إنشاء المنشور
#
# Gemini غير مستخدم هنا.
# الترجمة الإنجليزية ستضاف في مرحلة مستقلة لاحقًا.
# ============================================================

def build_arabic_post(
    title,
    summary,
    category,
    language
):

    label = get_category_label(category)

    # --------------------------------------------------------
    # خبر عربي
    # --------------------------------------------------------

    if language == "ar":

        post_title = title
        body = summary

    # --------------------------------------------------------
    # خبر إنجليزي
    #
    # حاليًا نحتفظ بالنص الأصلي.
    # لا نستخدم ترجمة آلية رديئة.
    # --------------------------------------------------------

    else:

        post_title = title
        body = summary

    # --------------------------------------------------------
    # إذا لم يوجد ملخص
    # --------------------------------------------------------

    if not body:

        body = "تطور جديد في عالم كرة القدم."

    # --------------------------------------------------------
    # تقليل طول الملخص
    # --------------------------------------------------------

    if len(body) > 500:

        body = body[:497].rstrip() + "..."

    # --------------------------------------------------------
    # بناء المنشور
    # --------------------------------------------------------

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
# استخراج وقت الخبر
# ============================================================

def get_entry_timestamp(article):

    # feedparser يوفر parsed time غالبًا
    parsed_time = article.get("published_parsed")

    if not parsed_time:
        parsed_time = article.get("updated_parsed")

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

        except (ValueError, TypeError):
            pass

    return 0


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
    # الروابط القديمة
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
        item.get("title", "")
        for item in old_news
        if item.get("title")
    ]

    new_news = []

    # ========================================================
    # معالجة المصادر
    # ========================================================

    for source in RSS_SOURCES:

        entries = fetch_source(source)

        # ----------------------------------------------------
        # الأحدث أولًا
        # ----------------------------------------------------

        entries = sort_entries(entries)

        # ----------------------------------------------------
        # الحد الأقصى لكل مصدر
        # ----------------------------------------------------

        entries = entries[
            :MAX_NEWS_PER_SOURCE
        ]

        source_added = 0

        # ----------------------------------------------------
        # الأخبار
        # ----------------------------------------------------

        for article in entries:

            # إذا وصلنا للحد الإجمالي
            if len(new_news) >= MAX_NEW_NEWS:

                break

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
            # بيانات أساسية ناقصة
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
            # منع التكرار مع الأخبار القديمة
            # ------------------------------------------------

            duplicate = False

            for existing_title in old_titles:

                if similar_titles(
                    title,
                    existing_title
                ):

                    duplicate = True
                    break

            if duplicate:

                continue

            # ------------------------------------------------
            # منع التكرار بين الأخبار الجديدة
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
            # بناء المنشور
            # ------------------------------------------------

            post = build_arabic_post(
                title,
                summary,
                category,
                source["language"]
            )

            # ------------------------------------------------
            # الخبر النهائي
            # ------------------------------------------------

            news_item = {

                # ============================================
                # البيانات الأصلية
                # ============================================

                "title": title,
                "summary": summary,
                "url": url,
                "published": published,

                # ============================================
                # المصدر
                #
                # للاستخدام الداخلي فقط
                # ============================================

                "source": source["name"],
                "language": source["language"],

                # ============================================
                # التصنيف
                # ============================================

                "category": category,

                # ============================================
                # المنشور
                # ============================================

                "post_title": post[
                    "post_title"
                ],

                "post_body": post[
                    "post_body"
                ],

                "post_text": post[
                    "post_text"
                ],

                # ============================================
                # حالة المعالجة
                # ============================================

                "processed": False,

                "published_to_facebook": False,

                # ============================================
                # الصورة
                #
                # سنستخدمها لاحقًا
                # ============================================

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
    # الحفظ
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


# ============================================================
# تشغيل البرنامج
# ============================================================

if __name__ == "__main__":
    main()

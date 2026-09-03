# ============================================================
# SPORTS NEWS BOT
# ============================================================

import json
import os
import re

from sources.sources_config import ALL_SOURCES
from sources.source_manager import fetch_all_sources
from sources.news_filter import filter_news
from sources.news_deduplicator import deduplicate_news
from sources.news_translator import translate_news
from sources.news_formatter import format_news

from image_fetcher import fetch_news_image
from image_generator import generate_news_image

from facebook_publisher import publish_post

# ============================================================
# إعدادات
# ============================================================

NEWS_FILE = "news.json"

MAX_NEWS_PER_SOURCE = 10
MAX_NEW_NEWS = 20
MAX_NEWS = 500

MAX_SUMMARY_LENGTH = 450


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
# تنظيف الملخص
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
# تحديد الحد الأقصى لكل مصدر
# ============================================================

def limit_news_per_source(
    news_list,
    max_per_source=MAX_NEWS_PER_SOURCE
):

    counters = {}
    limited = []

    for news in news_list:

        source = news.get(
            "source",
            "Unknown"
        )

        current_count = counters.get(
            source,
            0
        )

        if current_count >= max_per_source:
            continue

        limited.append(
            news
        )

        counters[source] = (
            current_count + 1
        )

    return limited


# ============================================================
# منع الأخبار الموجودة مسبقًا
# ============================================================

def remove_existing_news(
    news_list,
    old_news
):

    old_urls = {
        item.get("url")
        for item in old_news
        if item.get("url")
    }

    old_titles = [
        item.get(
            "title",
            ""
        )
        for item in old_news
        if item.get("title")
    ]

    result = []

    for news in news_list:

        url = clean_text(
            news.get(
                "url",
                ""
            )
        )

        title = clean_text(
            news.get(
                "title",
                ""
            )
        )

        if not title or not url:
            continue

        # ----------------------------------------------------
        # الرابط موجود مسبقًا
        # ----------------------------------------------------

        if url in old_urls:
            continue

        # ----------------------------------------------------
        # العنوان موجود مسبقًا
        # ----------------------------------------------------

        from sources.news_deduplicator import title_similarity

        duplicate = False

        for old_title in old_titles:

            if title_similarity(
                title,
                old_title
            ) >= 0.82:

                duplicate = True
                break

        if duplicate:
            continue

        result.append(
            news
        )

    return result


# ============================================================
# تجهيز بيانات الخبر الأساسية
# ============================================================

def prepare_news_item(news):

    item = dict(
        news
    )

    item["title"] = clean_text(
        item.get(
            "title",
            ""
        )
    )

    item["summary"] = clean_summary(
        item.get(
            "summary",
            ""
        )
    )

    item["url"] = clean_text(
        item.get(
            "url",
            ""
        )
    )

    item["published"] = clean_text(
        item.get(
            "published",
            "Unknown time"
        )
    )

    item["source"] = clean_text(
        item.get(
            "source",
            ""
        )
    )

    item["language"] = clean_text(
        item.get(
            "language",
            ""
        )
    )

    return item


# ============================================================
# إنشاء حالة الخبر
# ============================================================

def initialize_news_state(news):

    item = dict(
        news
    )

    # --------------------------------------------------------
    # حالة المعالجة
    # --------------------------------------------------------

    item.setdefault(
        "processed",
        False
    )

    item.setdefault(
        "published_to_facebook",
        False
    )

    item.setdefault(
        "facebook_post_id",
        None
    )

    item.setdefault(
        "facebook_error",
        None
    )

    # --------------------------------------------------------
    # بيانات الصورة
    # --------------------------------------------------------

    item.setdefault(
        "image",
        None
    )

    item.setdefault(
        "image_type",
        None
    )

    item.setdefault(
        "image_source",
        None
    )

    item.setdefault(
        "image_license",
        None
    )

    item.setdefault(
        "image_artist",
        None
    )

    return item


# ============================================================
# تجهيز صورة الخبر
# ============================================================

def prepare_news_image(news):

    title = (
        news.get(
            "arabic_title"
        )
        or news.get(
            "title"
        )
        or "Football News"
    )

    category = news.get(
        "category",
        "football"
    )

    print()
    print("-----------------------------------")
    print("IMAGE PIPELINE")
    print("-----------------------------------")

    print(
        "Searching for real news image..."
    )

    # ========================================================
    # المحاولة الأولى: صورة حقيقية
    # ========================================================

    real_image = fetch_news_image(
        title=title
    )

    if real_image:

        real_image_path = real_image.get(
            "image_path"
        )

        print()
        print(
            "✅ Real image found."
        )

        print(
            "Image:",
            real_image_path
        )

        # ----------------------------------------------------
        # إدخال الصورة الحقيقية في التصميم النهائي
        # ----------------------------------------------------

        print()
        print(
            "Generating final news image..."
        )

        final_image = generate_news_image(
            title=title,
            category=category,
            image_path=real_image_path,
        )

        if final_image:

            print()
            print(
                "✅ Final image generated."
            )

            print(
                "Final image:",
                final_image
            )

            news["image"] = final_image
            news["image_type"] = "real"

        else:

            # ------------------------------------------------
            # إذا فشل التصميم، نستخدم الصورة الحقيقية
            # ------------------------------------------------

            print()
            print(
                "⚠️ Final image generation failed."
            )

            print(
                "Using real image directly."
            )

            news["image"] = real_image_path
            news["image_type"] = "real"

        news["image_source"] = real_image.get(
            "source_url"
        )

        news["image_license"] = real_image.get(
            "license"
        )

        news["image_artist"] = real_image.get(
            "artist"
        )

        return news

    # ========================================================
    # المحاولة الثانية: توليد صورة
    # ========================================================

    print()
    print(
        "⚠️ No real image found."
    )

    print(
        "Trying generated fallback..."
    )

    generated_image = generate_news_image(
        title=title,
        category=category,
        image_path=None,
    )

    if generated_image:

        print()
        print(
            "✅ Generated fallback image created."
        )

        print(
            "Image:",
            generated_image
        )

        news["image"] = generated_image
        news["image_type"] = "generated"

        news["image_source"] = None
        news["image_license"] = None
        news["image_artist"] = None

        return news

    # ========================================================
    # المحاولة الثالثة: بدون صورة
    # ========================================================

    print()
    print(
        "❌ Image generation failed."
    )

    print(
        "Continuing with text-only news."
    )

    news["image"] = None
    news["image_type"] = "text_only"

    news["image_source"] = None
    news["image_license"] = None
    news["image_artist"] = None

    return news


# ============================================================
# البرنامج الرئيسي
# ============================================================

def main():

    print()
    print("===================================")
    print("      SPORTS NEWS BOT")
    print("===================================")

    # ========================================================
    # 1. تحميل الحالة القديمة
    # ========================================================

    old_news = load_news()

    print()
    print(
        f"Previously saved: "
        f"{len(old_news)}"
    )

    # ========================================================
    # 2. جلب جميع المصادر
    # ========================================================

    print()
    print("===================================")
    print("1. FETCHING SOURCES")
    print("===================================")

    raw_news = fetch_all_sources(
        ALL_SOURCES
    )

    print()
    print(
        f"Raw news received: "
        f"{len(raw_news)}"
    )

    if not raw_news:

        print()
        print(
            "❌ No news received from sources."
        )

        return

    # ========================================================
    # 3. الحد الأقصى لكل مصدر
    # ========================================================

    limited_news = limit_news_per_source(
        raw_news,
        MAX_NEWS_PER_SOURCE
    )

    print()
    print(
        f"After source limits: "
        f"{len(limited_news)}"
    )

    # ========================================================
    # 4. تجهيز البيانات
    # ========================================================

    prepared_news = []

    for news in limited_news:

        prepared_news.append(
            prepare_news_item(
                news
            )
        )

    # ========================================================
    # 5. إزالة الأخبار الموجودة مسبقًا
    # ========================================================

    new_candidate_news = remove_existing_news(
        prepared_news,
        old_news
    )

    print()
    print(
        f"New candidates: "
        f"{len(new_candidate_news)}"
    )

    if not new_candidate_news:

        print()
        print(
            "No new candidate news."
        )

        # نحافظ على الأخبار القديمة
        save_news(
            old_news
        )

        print()
        print(
            "==================================="
        )
        print(
            "Bot finished successfully!"
        )
        print(
            "==================================="
        )

        return

    # ========================================================
    # 6. فلترة الأخبار
    # ========================================================

    print()
    print("===================================")
    print("2. FILTERING")
    print("===================================")

    filtered_news = filter_news(
        new_candidate_news
    )

    print()
    print(
        f"Filtered football news: "
        f"{len(filtered_news)}"
    )

    if not filtered_news:

        print()
        print(
            "No football news remained."
        )

        return

    # ========================================================
    # 7. إزالة التكرار
    # ========================================================

    print()
    print("===================================")
    print("3. DEDUPLICATION")
    print("===================================")

    unique_news = deduplicate_news(
        filtered_news
    )

    print()
    print(
        f"Unique news: "
        f"{len(unique_news)}"
    )

    print(
        f"Duplicates removed: "
        f"{len(filtered_news) - len(unique_news)}"
    )

    if not unique_news:

        print()
        print(
            "No unique news remained."
        )

        return

    # ========================================================
    # 8. الحد الأقصى للأخبار الجديدة
    # ========================================================

    unique_news = unique_news[
        :MAX_NEW_NEWS
    ]

    print()
    print(
        f"News selected for processing: "
        f"{len(unique_news)}"
    )

    # ========================================================
    # 9. الترجمة
    # ========================================================

    print()
    print("===================================")
    print("4. TRANSLATION")
    print("===================================")

    translated_news = translate_news(
        unique_news
    )

    print()
    print(
        f"Translated news: "
        f"{len(translated_news)}"
    )

    # ========================================================
    # 10. تنسيق المنشورات
    # ========================================================

    print()
    print("===================================")
    print("5. FORMATTING")
    print("===================================")

    formatted_news = format_news(
        translated_news
    )

    print()
    print(
        f"Formatted news: "
        f"{len(formatted_news)}"
    )

    if not formatted_news:

        print()
        print(
            "❌ No formatted news."
        )

        return

    # ========================================================
    # 11. معالجة كل خبر
    # ========================================================

    new_news = []

    print()
    print("===================================")
    print("6. PROCESSING NEWS")
    print("===================================")

    for index, formatted_news_item in enumerate(
        formatted_news,
        start=1
    ):

        print()
        print()
        print("===================================")
        print(
            f"NEWS #{index}"
        )
        print("===================================")

        news_item = initialize_news_state(
            formatted_news_item
        )

        # ----------------------------------------------------
        # عرض بيانات الخبر
        # ----------------------------------------------------

        print()
        print(
            "Source:",
            news_item.get(
                "source",
                ""
            )
        )

        print(
            "Original title:",
            news_item.get(
                "title",
                ""
            )
        )

        print(
            "Arabic title:",
            news_item.get(
                "arabic_title",
                ""
            )
        )

        print(
            "Category:",
            news_item.get(
                "category",
                ""
            )
        )

        # ----------------------------------------------------
        # معالجة الصورة
        # ----------------------------------------------------

        news_item = prepare_news_image(
            news_item
        )
        # ----------------------------------------------------
        # نشر الخبر على Facebook
        # مع الصورة النهائية إن وُجدت
        # ----------------------------------------------------

        print()
        print("-----------------------------------")
        print(
            "Publishing news to Facebook..."
        )
        print("-----------------------------------")

        facebook_result = publish_post(
            message=news_item.get(
                "post_text",
                ""
            ),
            image_path=news_item.get(
                "image"
            )
        )

        # ====================================================
        # نجاح النشر
        # ====================================================

        if facebook_result.get(
            "success"
        ):

            news_item["processed"] = True

            news_item[
                "published_to_facebook"
            ] = True

            news_item[
                "facebook_post_id"
            ] = facebook_result.get(
                "post_id"
            )

            news_item[
                "facebook_error"
            ] = None

            print()
            print(
                "✅ News published to Facebook."
            )

            print(
                "Facebook Post ID:",
                facebook_result.get(
                    "post_id"
                )
            )

            # ------------------------------------------------
            # إضافة الخبر إلى الحالة
            # ------------------------------------------------

            new_news.append(
                news_item
            )

            # ------------------------------------------------
            # حفظ الحالة بعد كل نشر ناجح
            #
            # هذا يمنع فقدان الأخبار المنشورة إذا توقف
            # البرنامج أثناء معالجة خبر لاحق.
            # ------------------------------------------------

            current_state = (
                new_news +
                old_news
            )

            save_news(
                current_state
            )

            print()
            print(
                "✅ State saved."
            )

        # ====================================================
        # فشل النشر
        # ====================================================

        else:

            news_item["processed"] = False

            news_item[
                "published_to_facebook"
            ] = False

            news_item[
                "facebook_post_id"
            ] = None

            news_item[
                "facebook_error"
            ] = facebook_result.get(
                "error"
            )

            print()
            print(
                "❌ Facebook publishing failed."
            )

            print(
                "Facebook error:",
                facebook_result.get(
                    "error"
                )
            )

            # ------------------------------------------------
            # لا نضيف الخبر إلى الأخبار المنشورة
            # ------------------------------------------------

            continue

    # ========================================================
    # 12. النتائج النهائية
    # ========================================================

    print()
    print("===================================")
    print("FINAL RESULTS")
    print("===================================")

    print()
    print(
        f"Raw news: "
        f"{len(raw_news)}"
    )

    print(
        f"After source limits: "
        f"{len(limited_news)}"
    )

    print(
        f"Candidates: "
        f"{len(new_candidate_news)}"
    )

    print(
        f"Filtered: "
        f"{len(filtered_news)}"
    )

    print(
        f"Unique: "
        f"{len(unique_news)}"
    )

    print(
        f"Translated: "
        f"{len(translated_news)}"
    )

    print(
        f"Formatted: "
        f"{len(formatted_news)}"
    )

    print(
        f"Successfully published: "
        f"{len(new_news)}"
    )

    # ========================================================
    # 13. عرض الأخبار المنشورة
    # ========================================================

    if new_news:

        print()
        print("===================================")
        print("PUBLISHED NEWS")
        print("===================================")

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
                f"{article.get('source', '')}"
            )

            print(
                f"Original title: "
                f"{article.get('title', '')}"
            )

            print(
                f"Arabic title: "
                f"{article.get('arabic_title', '')}"
            )

            print(
                f"Category: "
                f"{article.get('category', '')}"
            )

            print(
                f"Image type: "
                f"{article.get('image_type', '')}"
            )

            print(
                f"Image path: "
                f"{article.get('image', '')}"
            )

            print()
            print(
                "POST PREVIEW:"
            )

            print(
                article.get(
                    "post_text",
                    ""
                )
            )

            print()
            print(
                f"Internal URL: "
                f"{article.get('url', '')}"
            )

            print()
            print(
                f"Facebook Post ID: "
                f"{article.get('facebook_post_id', '')}"
            )

    else:

        print()
        print(
            "No new football news were published."
        )

    # ========================================================
    # 14. الحالة النهائية
    # ========================================================

    combined_news = (
        new_news +
        old_news
    )

    save_news(
        combined_news
    )

    # ========================================================
    # 15. النهاية
    # ========================================================

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

from sources.sources_config import ALL_SOURCES
from sources.source_manager import fetch_all_sources
from sources.news_filter import filter_news
from sources.news_deduplicator import deduplicate_news
from sources.news_translator import translate_news
from sources.news_formatter import format_news

from image_fetcher import fetch_news_image
from image_generator import generate_news_image


# ============================================================
# إعدادات الاختبار
# ============================================================

MAX_IMAGE_TESTS = 2


# ============================================================
# طباعة عنوان مرحلة
# ============================================================

def print_stage(title):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


# ============================================================
# الاختبار الرئيسي
# ============================================================

def main():

    print_stage("1. SOURCES")

    raw_news = fetch_all_sources(ALL_SOURCES)

    print()
    print("Raw news:", len(raw_news))

    if not raw_news:
        print("❌ No news received.")
        return


    # ========================================================
    # Filtering
    # ========================================================

    print_stage("2. FILTERING")

    filtered_news = filter_news(raw_news)

    print()
    print("Filtered news:", len(filtered_news))

    if not filtered_news:
        print("❌ No news remained after filtering.")
        return


    # ========================================================
    # Deduplication
    # ========================================================

    print_stage("3. DEDUPLICATION")

    unique_news = deduplicate_news(filtered_news)

    print()
    print("Unique news:", len(unique_news))
    print("Duplicates removed:", len(filtered_news) - len(unique_news))

    if not unique_news:
        print("❌ No news remained after deduplication.")
        return


    # ========================================================
    # Limit translation test
    # ========================================================

    print_stage("4. TRANSLATION")

    # نختبر عددًا محدودًا حتى لا نرسل طلبات ترجمة كثيرة
    selected_news = unique_news[:5]

    translated_news = translate_news(selected_news)

    print()
    print("Translated items:", len(translated_news))

    for index, news in enumerate(translated_news, start=1):
        print()
        print(f"--- Translation {index} ---")
        print("Original:")
        print(news.get("title", ""))

        print()
        print("Arabic:")
        print(news.get("arabic_title", ""))


    # ========================================================
    # Formatting
    # ========================================================

    print_stage("5. FORMATTING")

    formatted_news = format_news(translated_news)

    print()
    print("Formatted items:", len(formatted_news))

    for index, news in enumerate(formatted_news, start=1):
        print()
        print(f"--- Formatted item {index} ---")
        print(news.get("post_text", ""))


    # ========================================================
    # Images
    # ========================================================

    print_stage("6. IMAGE PIPELINE")

    image_results = []

    for index, news in enumerate(
        formatted_news[:MAX_IMAGE_TESTS],
        start=1
    ):

        title = (
            news.get("arabic_title")
            or news.get("title")
            or "Football News"
        )

        category = news.get(
            "category",
            "football"
        )

        print()
        print("-" * 70)
        print(f"IMAGE TEST {index}")
        print("-" * 70)

        print("Title:", title)
        print("Category:", category)

        # ----------------------------------------------------
        # أولًا: محاولة جلب صورة حقيقية
        # ----------------------------------------------------

        real_image = fetch_news_image(
            title=title
        )

        if real_image:
            print()
            print("✅ Real image found.")

            image_path = real_image.get(
                "image_path"
            )

            # ------------------------------------------------
            # نمرر الصورة الحقيقية إلى مولد الصورة
            # ------------------------------------------------

            generated_path = generate_news_image(
                title=title,
                category=category,
                image_path=image_path,
            )

            if generated_path:
                print()
                print("✅ Final image generated using real image.")
                print("Final image:", generated_path)

                image_results.append({
                    "title": title,
                    "image_type": "real",
                    "image_path": generated_path,
                })

            else:
                print()
                print("⚠️ Generator failed.")
                print("Using real image directly.")

                image_results.append({
                    "title": title,
                    "image_type": "real",
                    "image_path": image_path,
                })

            # -----------------------------------------------
            # وجدنا صورة حقيقية، لا نحتاج اختبار صور أخرى
            # -----------------------------------------------

            break

        # ----------------------------------------------------
        # لا توجد صورة حقيقية
        # ----------------------------------------------------

        print()
        print("⚠️ No real image found.")
        print("Trying generated fallback...")

        generated_path = generate_news_image(
            title=title,
            category=category,
            image_path=None,
        )

        if generated_path:
            print()
            print("✅ Generated fallback image created.")
            print("Image:", generated_path)

            image_results.append({
                "title": title,
                "image_type": "generated",
                "image_path": generated_path,
            })

            # نجح الـ fallback، لا داعي لطلبات إضافية
            break

        else:
            print()
            print("❌ Image generation failed.")

    # ========================================================
    # Final pipeline result
    # ========================================================

    print_stage("7. FINAL PIPELINE RESULT")

    print()
    print("Raw:", len(raw_news))
    print("Filtered:", len(filtered_news))
    print("Unique:", len(unique_news))
    print("Translated:", len(translated_news))
    print("Formatted:", len(formatted_news))
    print("Image results:", len(image_results))

    # ========================================================
    # عرض النتيجة النهائية
    # ========================================================

    if formatted_news:

        final_news = formatted_news[0]

        print()
        print("=" * 70)
        print("FINAL NEWS ITEM")
        print("=" * 70)

        print()
        print("TITLE:")
        print(final_news.get("post_title", ""))

        print()
        print("POST:")
        print(final_news.get("post_text", ""))

        print()
        print("CATEGORY:")
        print(final_news.get("category", ""))

        print()
        print("SOURCE:")
        print(final_news.get("source", ""))

    # ========================================================
    # Image result
    # ========================================================

    if image_results:

        image = image_results[0]

        print()
        print("=" * 70)
        print("FINAL IMAGE")
        print("=" * 70)

        print()
        print("Type:", image.get("image_type"))
        print("Path:", image.get("image_path"))

    # ========================================================
    # Success
    # ========================================================

    print()
    print("=" * 70)
    print("✅ BOT PIPELINE TEST COMPLETED")
    print("=" * 70)


# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":
    main()

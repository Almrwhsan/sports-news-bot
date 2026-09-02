# ============================================================
# اختبار جلب الصور من أخبار حقيقية
# ============================================================

from sources.sources_config import ALL_SOURCES
from sources.source_manager import fetch_all_sources
from image_fetcher import fetch_news_image


# ============================================================
# إعدادات الاختبار
# ============================================================

TEST_NEWS_COUNT = 5


# ============================================================
# البرنامج الرئيسي
# ============================================================

def main():

    print("===================================")
    print("   REAL NEWS IMAGE FETCHER TEST")
    print("===================================")

    print()
    print(
        f"Configured sources: "
        f"{len(ALL_SOURCES)}"
    )

    # --------------------------------------------------------
    # جلب الأخبار الحقيقية
    # --------------------------------------------------------

    print()
    print("Fetching real news from sources...")

    news = fetch_all_sources(
        ALL_SOURCES
    )

    print()
    print("===================================")
    print(
        f"Total real news fetched: "
        f"{len(news)}"
    )
    print("===================================")

    if not news:

        print()
        print(
            "❌ No real news were fetched."
        )

        raise SystemExit(1)

    # --------------------------------------------------------
    # اختيار عدد محدود من الأخبار
    # --------------------------------------------------------

    test_news = news[
        :TEST_NEWS_COUNT
    ]

    print()
    print(
        f"Testing images for "
        f"{len(test_news)} real news items..."
    )

    successful = 0

    # --------------------------------------------------------
    # اختبار كل خبر
    # --------------------------------------------------------

    for index, item in enumerate(
        test_news,
        start=1
    ):

        title = item.get(
            "title",
            ""
        )

        source = item.get(
            "source",
            ""
        )

        category = item.get(
            "category",
            ""
        )

        print()
        print("-----------------------------------")
        print(
            f"REAL NEWS TEST {index}"
        )
        print("-----------------------------------")

        print(
            "Title:",
            title
        )

        print(
            "Source:",
            source
        )

        print(
            "Category:",
            category
        )

        if not title:

            print(
                "⚠️ Empty title. Skipping."
            )

            continue

        # ----------------------------------------------------
        # جلب الصورة
        # ----------------------------------------------------

        try:

            result = fetch_news_image(
                title=title
            )

        except Exception as error:

            print()
            print(
                "❌ Image fetch error:",
                error
            )

            continue

        # ----------------------------------------------------
        # تحليل النتيجة
        # ----------------------------------------------------

        if result:

            successful += 1

            print()
            print(
                "✅ IMAGE FOUND"
            )

            print(
                "Image path:",
                result.get(
                    "image_path",
                    ""
                )
            )

            print(
                "Image title:",
                result.get(
                    "title",
                    ""
                )
            )

            print(
                "License:",
                result.get(
                    "license",
                    ""
                )
            )

            print(
                "Artist:",
                result.get(
                    "artist",
                    ""
                )
            )

            print(
                "Source:",
                result.get(
                    "source_url",
                    ""
                )
            )

        else:

            print()
            print(
                "❌ IMAGE NOT FOUND"
            )

    # --------------------------------------------------------
    # النتيجة النهائية
    # --------------------------------------------------------

    print()
    print("===================================")
    print("       REAL IMAGE TEST SUMMARY")
    print("===================================")

    print()

    print(
        f"Real news tested: "
        f"{len(test_news)}"
    )

    print(
        f"Successful image results: "
        f"{successful}/{len(test_news)}"
    )

    failed = (
        len(test_news)
        - successful
    )

    print(
        f"News without image: "
        f"{failed}/{len(test_news)}"
    )

    print()

    if successful > 0:

        print(
            "✅ REAL NEWS IMAGE FETCHER IS WORKING"
        )

    else:

        print(
            "❌ NO IMAGES FOUND FOR REAL NEWS"
        )

        raise SystemExit(1)

    print()
    print("===================================")
    print("    REAL IMAGE FETCHER TEST END")
    print("===================================")


# ============================================================
# تشغيل الاختبار
# ============================================================

if __name__ == "__main__":

    main()

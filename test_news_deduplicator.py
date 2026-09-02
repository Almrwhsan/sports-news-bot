# ============================================================
# اختبار إزالة الأخبار المتكررة وأولوية المصادر
# ============================================================

from sources.sources_config import ALL_SOURCES
from sources.source_manager import fetch_all_sources
from sources.news_filter import filter_news
from sources.news_deduplicator import deduplicate_news


def main():

    print("===================================")
    print("     NEWS DEDUPLICATOR TEST")
    print("===================================")

    # --------------------------------------------------------
    # جلب الأخبار
    # --------------------------------------------------------

    print()
    print("Fetching all sources...")

    all_news = fetch_all_sources(
        ALL_SOURCES
    )

    print()
    print(
        f"Raw news: {len(all_news)}"
    )

    # --------------------------------------------------------
    # فلترة الأخبار
    # --------------------------------------------------------

    filtered_news = filter_news(
        all_news
    )

    print()
    print(
        f"Filtered football news: "
        f"{len(filtered_news)}"
    )

    # --------------------------------------------------------
    # إزالة التكرار
    # --------------------------------------------------------

    unique_news = deduplicate_news(
        filtered_news
    )

    print()
    print(
        f"Unique news after deduplication: "
        f"{len(unique_news)}"
    )

    # --------------------------------------------------------
    # عدد الأخبار التي تم حذفها
    # --------------------------------------------------------

    duplicates_removed = (
        len(filtered_news)
        - len(unique_news)
    )

    print()
    print(
        f"Duplicates removed: "
        f"{duplicates_removed}"
    )

    # --------------------------------------------------------
    # عرض النتائج
    # --------------------------------------------------------

    print()
    print("===================================")
    print("       SAMPLE UNIQUE RESULTS")
    print("===================================")

    for index, item in enumerate(
        unique_news[:20],
        start=1
    ):

        print()

        print(
            f"{index}. "
            f"{item['title']}"
        )

        print(
            f"Source: "
            f"{item['source']}"
        )

        print(
            f"Category: "
            f"{item['category']}"
        )

        print(
            f"Priority: "
            f"{item['priority']}"
        )

    print()
    print("===================================")
    print("     DEDUPLICATOR TEST END")
    print("===================================")


if __name__ == "__main__":

    main()

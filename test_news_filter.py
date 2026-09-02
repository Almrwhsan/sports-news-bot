# ============================================================
# اختبار فلترة وتصنيف الأخبار
# ============================================================

from sources.sources_config import ALL_SOURCES
from sources.source_manager import fetch_all_sources
from sources.news_filter import filter_news


def main():

    print("===================================")
    print("       NEWS FILTER TEST")
    print("===================================")

    # --------------------------------------------------------
    # جلب جميع الأخبار
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
    # فلترة وتصنيف الأخبار
    # --------------------------------------------------------

    filtered_news = filter_news(
        all_news
    )

    print()
    print(
        f"Filtered football news: "
        f"{len(filtered_news)}"
    )

    print()
    print("===================================")
    print("       SAMPLE RESULTS")
    print("===================================")

    # --------------------------------------------------------
    # عرض أول 20 خبر
    # --------------------------------------------------------

    for index, item in enumerate(
        filtered_news[:20],
        start=1
    ):

        print()
        print(
            f"{index}. {item['title']}"
        )

        print(
            f"Source: {item['source']}"
        )

        print(
            f"Category: {item['category']}"
        )

        print(
            f"Language: {item['language']}"
        )

    print()
    print("===================================")
    print("          FILTER TEST END")
    print("===================================")


if __name__ == "__main__":
    main()

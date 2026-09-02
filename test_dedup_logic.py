# ============================================================
# اختبار منطق إزالة التكرار وأولوية المصادر
# ============================================================

from sources.news_deduplicator import (
    title_similarity,
    choose_best_news,
    deduplicate_news,
)


def main():

    print("===================================")
    print("       DEDUP LOGIC TEST")
    print("===================================")

    # --------------------------------------------------------
    # اختبار 1: تشابه العناوين
    # --------------------------------------------------------

    title_a = (
        "Real Madrid signs a new midfielder"
    )

    title_b = (
        "Real Madrid signs new midfielder"
    )

    similarity = title_similarity(
        title_a,
        title_b
    )

    print()
    print("TEST 1 - Title similarity")
    print(
        f"Similarity: {similarity:.2f}"
    )

    # --------------------------------------------------------
    # اختبار 2: أولوية المصدر
    # --------------------------------------------------------

    news_as = {
        "title": title_a,
        "source": "AS Football",
        "priority": 1,
    }

    news_alyaum = {
        "title": title_b,
        "source": "Al Yaum World Football",
        "priority": 2,
    }

    best = choose_best_news(
        news_as,
        news_alyaum
    )

    print()
    print("TEST 2 - Source priority")
    print(
        f"Selected source: "
        f"{best['source']}"
    )

    # --------------------------------------------------------
    # اختبار 3: خبران مختلفان
    # --------------------------------------------------------

    different_news = [

        {
            "title": (
                "Real Madrid signs a new midfielder"
            ),
            "source": "AS Football",
            "priority": 1,
        },

        {
            "title": (
                "Barcelona announces new coach"
            ),
            "source": "AS Football",
            "priority": 1,
        },

    ]

    unique_different = deduplicate_news(
        different_news
    )

    print()
    print("TEST 3 - Different news")
    print(
        f"News before: "
        f"{len(different_news)}"
    )

    print(
        f"News after: "
        f"{len(unique_different)}"
    )

    # --------------------------------------------------------
    # اختبار 4: خبران متشابهان من مصدرين
    # --------------------------------------------------------

    duplicate_news = [

        {
            "title": (
                "Real Madrid signs a new midfielder"
            ),
            "source": "AS Football",
            "priority": 1,
        },

        {
            "title": (
                "Real Madrid signs new midfielder"
            ),
            "source": "Al Yaum World Football",
            "priority": 2,
        },

    ]

    unique_duplicate = deduplicate_news(
        duplicate_news
    )

    print()
    print("TEST 4 - Duplicate news")

    print(
        f"News before: "
        f"{len(duplicate_news)}"
    )

    print(
        f"News after: "
        f"{len(unique_duplicate)}"
    )

    if unique_duplicate:

        print(
            f"Selected source: "
            f"{unique_duplicate[0]['source']}"
        )

    # --------------------------------------------------------
    # النتيجة
    # --------------------------------------------------------

    print()
    print("===================================")
    print("       DEDUP LOGIC TEST END")
    print("===================================")


if __name__ == "__main__":

    main()

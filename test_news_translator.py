
# ============================================================
# اختبار ترجمة أخبار كرة القدم
# ============================================================

from sources.news_translator import translate_news_item


def main():

    print("===================================")
    print("       NEWS TRANSLATOR TEST")
    print("===================================")

    # --------------------------------------------------------
    # اختبار خبر إسباني
    # --------------------------------------------------------

    spanish_news = {

        "title": (
            "Real Madrid ficha a un nuevo delantero"
        ),

        "summary": (
            "El club blanco ha cerrado el acuerdo "
            "para incorporar al delantero este verano."
        ),

        "language": "es",

        "source": "AS Football",

        "category": "real_madrid",

    }

    print()
    print("TEST 1 - Spanish news")

    translated_spanish = translate_news_item(
        spanish_news
    )

    print()
    print(
        f"Original title: "
        f"{spanish_news['title']}"
    )

    print(
        f"Arabic title: "
        f"{translated_spanish['arabic_title']}"
    )

    print()
    print(
        f"Original summary: "
        f"{spanish_news['summary']}"
    )

    print(
        f"Arabic summary: "
        f"{translated_spanish['arabic_summary']}"
    )

    # --------------------------------------------------------
    # اختبار خبر إنجليزي
    # --------------------------------------------------------

    english_news = {

        "title": (
            "Real Madrid are interested in signing "
            "a young midfielder"
        ),

        "summary": (
            "The Spanish club has been following "
            "the player for several months."
        ),

        "language": "en",

        "source": "BBC Sport",

        "category": "real_madrid",

    }

    print()
    print("TEST 2 - English news")

    translated_english = translate_news_item(
        english_news
    )

    print()
    print(
        f"Original title: "
        f"{english_news['title']}"
    )

    print(
        f"Arabic title: "
        f"{translated_english['arabic_title']}"
    )

    print()
    print(
        f"Original summary: "
        f"{english_news['summary']}"
    )

    print(
        f"Arabic summary: "
        f"{translated_english['arabic_summary']}"
    )

    # --------------------------------------------------------
    # اختبار خبر عربي
    # --------------------------------------------------------

    arabic_news = {

        "title": (
            "ريال مدريد يستعد لمواجهة جديدة"
        ),

        "summary": (
            "الفريق يواصل تحضيراته للمباراة القادمة."
        ),

        "language": "ar",

        "source": "Al Yaum World Football",

        "category": "real_madrid",

    }

    print()
    print("TEST 3 - Arabic news")

    translated_arabic = translate_news_item(
        arabic_news
    )

    print()
    print(
        f"Arabic title: "
        f"{translated_arabic['arabic_title']}"
    )

    print(
        f"Arabic summary: "
        f"{translated_arabic['arabic_summary']}"
    )

    # --------------------------------------------------------
    # التحقق من وجود النتائج
    # --------------------------------------------------------

    print()
    print("===================================")
    print("       TRANSLATION TEST SUMMARY")
    print("===================================")

    tests_passed = 0

    if translated_spanish.get(
        "arabic_title"
    ):

        tests_passed += 1

    if translated_english.get(
        "arabic_title"
    ):

        tests_passed += 1

    if (
        translated_arabic.get(
            "arabic_title"
        )
        == arabic_news["title"]
    ):

        tests_passed += 1

    print()
    print(
        f"Tests passed: "
        f"{tests_passed}/3"
    )

    if tests_passed == 3:

        print()
        print("✅ TRANSLATOR TEST PASSED")

    else:

        print()
        print("❌ TRANSLATOR TEST FAILED")

        raise SystemExit(1)

    print()
    print("===================================")
    print("     TRANSLATOR TEST END")
    print("===================================")


if __name__ == "__main__":

    main()

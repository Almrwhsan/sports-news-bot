# ============================================================
# اختبار تنسيق أخبار كرة القدم
# ============================================================

from sources.news_formatter import format_news_item


def main():

    print("===================================")
    print("       NEWS FORMATTER TEST")
    print("===================================")

    # --------------------------------------------------------
    # خبر مترجم
    # --------------------------------------------------------

    news = {

        "arabic_title": (
            "ريال مدريد مهتم بالتعاقد مع لاعب خط وسط شاب"
        ),

        "arabic_summary": (
            "ويتبع النادي الإسباني اللاعب منذ عدة أشهر."
        ),

        "source": "AS Football",

        "category": "real_madrid",

    }

    formatted = format_news_item(
        news
    )

    # --------------------------------------------------------
    # عرض العنوان
    # --------------------------------------------------------

    print()
    print("POST TITLE:")
    print(
        formatted["post_title"]
    )

    # --------------------------------------------------------
    # عرض المنشور
    # --------------------------------------------------------

    print()
    print("POST TEXT:")
    print("-----------------------------------")

    print(
        formatted["post_text"]
    )

    print("-----------------------------------")

    # --------------------------------------------------------
    # التحقق
    # --------------------------------------------------------

    print()
    print("===================================")
    print("       FORMAT TEST SUMMARY")
    print("===================================")

    tests_passed = 0

    if formatted.get(
        "post_title"
    ):

        tests_passed += 1

    if formatted.get(
        "post_text"
    ):

        tests_passed += 1

    if "🚨" in formatted["post_text"]:

        tests_passed += 1

    if "📰" in formatted["post_text"]:

        tests_passed += 1

    if "🏷️" in formatted["post_text"]:

        tests_passed += 1

    if "🌐 المصدر:" in formatted["post_text"]:

        tests_passed += 1

    if "📍 نبض مدريد" in formatted["post_text"]:

        tests_passed += 1

    print()
    print(
        f"Tests passed: "
        f"{tests_passed}/7"
    )

    if tests_passed == 7:

        print()
        print("✅ FORMATTER TEST PASSED")

    else:

        print()
        print("❌ FORMATTER TEST FAILED")

        raise SystemExit(1)

    print()
    print("===================================")
    print("      FORMATTER TEST END")
    print("===================================")


if __name__ == "__main__":

    main()

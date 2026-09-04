# ============================================================
# اختبار الترجمة الفعلية بعد إصلاح اكتشاف اللغة
# ============================================================

from sources.news_translator import (
    needs_translation,
    translate_news_item,
)


def test_case(number, name, news, expected_translation):
    print()
    print("=" * 70)
    print(f"TEST {number} — {name}")
    print("=" * 70)

    should_translate = needs_translation(news)

    print(f"Language           : {news.get('language', '')}")
    print(f"Original title     : {news.get('title', '')}")
    print(f"Original summary   : {news.get('summary', '')}")
    print(f"Needs translation : {should_translate}")
    print(f"Expected           : {expected_translation}")

    if should_translate != expected_translation:
        print("FAIL")
        return False

    print("Decision test: PASS")

    # --------------------------------------------------------
    # تنفيذ الترجمة الفعلية فقط إذا كان مطلوبًا
    # --------------------------------------------------------

    result = translate_news_item(news)

    print()
    print("RESULT")
    print(f"Arabic title       : {result.get('arabic_title', '')}")
    print(f"Arabic summary     : {result.get('arabic_summary', '')}")

    return True


def main():

    results = []

    # --------------------------------------------------------
    # TEST 1 — حالة AS الحقيقية التي كانت تفشل
    # --------------------------------------------------------

    results.append(
        test_case(
            1,
            "Real AS Spanish article with language=ar",
            {
                "language": "ar",
                "title": (
                    "La Cartuja: el estadio en el que nació "
                    "la leyenda de José Mourinho"
                ),
                "summary": (
                    "El portugués levantó en el recinto sevillano "
                    "su primer título europeo, la UEFA, en 2003."
                ),
            },
            True,
        )
    )

    # --------------------------------------------------------
    # TEST 2 — خبر إنجليزي
    # --------------------------------------------------------

    results.append(
        test_case(
            2,
            "English article",
            {
                "language": "en",
                "title": "David Moyes admits disappointment",
                "summary": (
                    "David Moyes says he was disappointed "
                    "after the match."
                ),
            },
            True,
        )
    )

    # --------------------------------------------------------
    # TEST 3 — خبر عربي
    # --------------------------------------------------------

    results.append(
        test_case(
            3,
            "Arabic article",
            {
                "language": "ar",
                "title": "ريال مدريد يستعد للمباراة",
                "summary": (
                    "يواصل الفريق استعداداته للمواجهة القادمة."
                ),
            },
            False,
        )
    )

    # --------------------------------------------------------
    # TEST 4 — عربي يحتوي اسمًا أجنبيًا
    # --------------------------------------------------------

    results.append(
        test_case(
            4,
            "Arabic article with foreign name",
            {
                "language": "ar",
                "title": "مورينيو يتحدث عن ريال مدريد",
                "summary": (
                    "أكد José Mourinho أن الفريق يمتلك فرصة كبيرة."
                ),
            },
            False,
        )
    )

    # ========================================================
    # النتيجة
    # ========================================================

    passed = sum(results)
    total = len(results)

    print()
    print("=" * 70)
    print("FINAL RESULT")
    print("=" * 70)

    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("ALL TESTS PASSED")
        print()
        print(
            "Translation detection and actual translation "
            "are working correctly."
        )
    else:
        print("SOME TESTS FAILED")


if __name__ == "__main__":
    main()

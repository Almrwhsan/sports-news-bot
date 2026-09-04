# ============================================================
# اختبار قرار الترجمة فقط
# ============================================================

from sources.news_translator import (
    needs_translation,
)


# ============================================================
# تشغيل اختبار واحد
# ============================================================

def run_test(name, news, expected):

    result = needs_translation(news)

    status = "PASS" if result == expected else "FAIL"

    print()
    print("=" * 70)
    print(name)
    print("=" * 70)

    print("Language           :", repr(news.get("language")))
    print("Title              :", news.get("title", ""))
    print("Summary            :", news.get("summary", ""))
    print("Expected           :", expected)
    print("Actual             :", result)
    print("Result             :", status)

    return result == expected


# ============================================================
# الاختبارات
# ============================================================

def main():

    passed = 0
    total = 0

    # ========================================================
    # TEST 1
    # إسباني + language خاطئة = ar
    # ========================================================

    total += 1

    if run_test(
        "TEST 1 — Spanish with language=ar",
        {
            "language": "ar",

            "title": (
                "La Cartuja: el estadio en el que nació "
                "la leyenda de José Mourinho"
            ),

            "summary": (
                "El portugués levantó en el recinto "
                "sevillano su primer título europeo."
            ),
        },
        True
    ):
        passed += 1

    # ========================================================
    # TEST 2
    # إسباني + language خاطئة = arabic
    # ========================================================

    total += 1

    if run_test(
        "TEST 2 — Spanish with language=arabic",
        {
            "language": "arabic",

            "title": (
                "El Real Madrid prepara su próximo partido"
            ),

            "summary": (
                "El equipo trabaja para llegar preparado."
            ),
        },
        True
    ):
        passed += 1

    # ========================================================
    # TEST 3
    # إنجليزي + language=en
    # ========================================================

    total += 1

    if run_test(
        "TEST 3 — English",
        {
            "language": "en",

            "title": (
                "David Moyes admits he wanted to do more "
                "business on deadline day"
            ),

            "summary": (
                "David Moyes says he has to live with "
                "the disappointment."
            ),
        },
        True
    ):
        passed += 1

    # ========================================================
    # TEST 4
    # عربي + language=ar
    # ========================================================

    total += 1

    if run_test(
        "TEST 4 — Arabic",
        {
            "language": "ar",

            "title": (
                "مويز يعيش بخيبة أمل بعد يوم الموعد النهائي"
            ),

            "summary": (
                "اعترف ديفيد مويس بأنه يتعين عليه "
                "التعايش مع خيبات الأمل."
            ),
        },
        False
    ):
        passed += 1

    # ========================================================
    # TEST 5
    # عربي + language=arabic
    # ========================================================

    total += 1

    if run_test(
        "TEST 5 — Arabic with language=arabic",
        {
            "language": "arabic",

            "title": (
                "ريال مدريد يستعد لمباراته القادمة"
            ),

            "summary": (
                "يواصل الفريق استعداداته للمباراة."
            ),
        },
        False
    ):
        passed += 1

    # ========================================================
    # TEST 6
    # إسباني قصير جدًا
    # ========================================================

    total += 1

    if run_test(
        "TEST 6 — Short Spanish text",
        {
            "language": "ar",

            "title": "Real Madrid gana",

            "summary": "El equipo ganó el partido.",
        },
        True
    ):
        passed += 1

    # ========================================================
    # TEST 7
    # اسم أجنبي داخل نص عربي
    #
    # يجب ألا يعتبر الخبر أجنبيًا بسبب اسم واحد.
    # ========================================================

    total += 1

    if run_test(
        "TEST 7 — Arabic text with foreign name",
        {
            "language": "ar",

            "title": (
                "جوزيه مورينيو يتحدث عن ريال مدريد"
            ),

            "summary": (
                "قال José Mourinho إن النادي يملك "
                "تاريخًا كبيرًا في البطولة."
            ),
        },
        False
    ):
        passed += 1

    # ========================================================
    # النتيجة النهائية
    # ========================================================

    print()
    print("=" * 70)
    print("FINAL RESULT")
    print("=" * 70)

    print(
        f"Passed: {passed}/{total}"
    )

    if passed == total:

        print(
            "✅ ALL TESTS PASSED"
        )

    else:

        print(
            "❌ SOME TESTS FAILED"
        )

    print("=" * 70)


# ============================================================
# تشغيل الاختبار
# ============================================================

if __name__ == "__main__":
    main()

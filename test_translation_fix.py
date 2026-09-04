# ============================================================
# اختبار منطق اكتشاف لغة الخبر قبل الترجمة
# لا يعدّل news_translator.py
# ============================================================

import re

from sources.news_translator import clean_text


# ============================================================
# أنماط الحروف
# ============================================================

ARABIC_RE = re.compile(
    r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]"
)

LATIN_RE = re.compile(
    r"[A-Za-zÀ-ÖØ-öø-ÿ]"
)


# ============================================================
# النموذج التجريبي للمنطق الجديد
# ============================================================

def prototype_needs_translation(news):
    """
    نسخة تجريبية فقط لاختبار منطق تحديد الحاجة للترجمة.

    لا نستخدم needs_translation() الحالية من news_translator.py
    لأن الاختبار الحالي هدفه اختبار المنطق الجديد قبل اعتماده.
    """

    title = clean_text(news.get("title", ""))
    summary = clean_text(news.get("summary", ""))

    text = f"{title} {summary}".strip()

    arabic_count = len(ARABIC_RE.findall(text))
    latin_count = len(LATIN_RE.findall(text))

    total_letters = arabic_count + latin_count

    # لا توجد حروف يمكن تحديد اللغة منها
    if total_letters == 0:
        language = str(
            news.get("language", "")
        ).lower().strip()

        return language not in ("", "ar", "arabic")

    arabic_ratio = arabic_count / total_letters
    latin_ratio = latin_count / total_letters

    # ========================================================
    # إذا كان النص عربيًا بشكل واضح
    # ========================================================

    if arabic_count >= 3 and arabic_ratio >= 0.25:
        return False

    # ========================================================
    # إذا كان النص لاتينيًا بشكل واضح
    # مثل الإنجليزية أو الإسبانية
    # ========================================================

    if latin_ratio >= 0.65:
        return True

    # ========================================================
    # حالة مختلطة أو غير واضحة
    # ========================================================

    language = str(
        news.get("language", "")
    ).lower().strip()

    # إذا كان المصدر يقول عربيًا والنص مختلط،
    # نتجنب ترجمة النص العربي بسبب اسم أجنبي مثل Mourinho.
    if language in ("ar", "arabic"):
        return False

    return True


# ============================================================
# تشغيل اختبار واحد
# ============================================================

def run_test(number, name, news, expected):
    print()
    print("=" * 60)
    print(f"TEST {number} — {name}")
    print("=" * 60)

    actual = prototype_needs_translation(news)

    print(f"Language       : {news.get('language', '')}")
    print(f"Title          : {news.get('title', '')}")
    print(f"Summary        : {news.get('summary', '')}")
    print(f"Expected       : {expected}")
    print(f"Actual         : {actual}")

    if actual == expected:
        print("PASS")
        return True

    print("FAIL")
    return False


# ============================================================
# الاختبارات
# ============================================================

def main():

    results = []


    # --------------------------------------------------------
    # TEST 1
    # إسباني لكن المصدر أخطأ وقال ar
    # هذه هي مشكلة AS الأساسية
    # --------------------------------------------------------

    results.append(
        run_test(
            1,
            "Spanish AS article with incorrect language=ar",
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
    # TEST 2
    # إسباني والمصدر يقول arabic
    # --------------------------------------------------------

    results.append(
        run_test(
            2,
            "Spanish article with incorrect language=arabic",
            {
                "language": "arabic",
                "title": "Real Madrid gana el partido",
                "summary": (
                    "El equipo ganó el partido con una gran actuación."
                ),
            },
            True,
        )
    )


    # --------------------------------------------------------
    # TEST 3
    # إنجليزي
    # --------------------------------------------------------

    results.append(
        run_test(
            3,
            "English article",
            {
                "language": "en",
                "title": "David Moyes admits disappointment",
                "summary": (
                    "David Moyes says he was disappointed after the match."
                ),
            },
            True,
        )
    )


    # --------------------------------------------------------
    # TEST 4
    # عربي واضح
    # --------------------------------------------------------

    results.append(
        run_test(
            4,
            "Arabic article",
            {
                "language": "ar",
                "title": "ريال مدريد يحقق الفوز",
                "summary": (
                    "حقق الفريق فوزًا مهمًا في المباراة."
                ),
            },
            False,
        )
    )


    # --------------------------------------------------------
    # TEST 5
    # عربي + language=arabic
    # --------------------------------------------------------

    results.append(
        run_test(
            5,
            "Arabic with language=arabic",
            {
                "language": "arabic",
                "title": "ريال مدريد يستعد للمباراة",
                "summary": (
                    "يواصل الفريق استعداداته للمواجهة القادمة."
                ),
            },
            False,
        )
    )


    # --------------------------------------------------------
    # TEST 6
    # إسباني قصير
    # --------------------------------------------------------

    results.append(
        run_test(
            6,
            "Short Spanish text",
            {
                "language": "ar",
                "title": "Real Madrid gana",
                "summary": "El equipo ganó el partido.",
            },
            True,
        )
    )


    # --------------------------------------------------------
    # TEST 7
    # عربي يحتوي اسمًا أجنبيًا
    # يجب ألا يترجم
    # --------------------------------------------------------

    results.append(
        run_test(
            7,
            "Arabic text with foreign name",
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
    # النتيجة النهائية
    # ========================================================

    passed = sum(results)
    total = len(results)

    print()
    print("=" * 60)
    print("FINAL RESULT")
    print("=" * 60)

    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("ALL TESTS PASSED")
        print()
        print(
            "The prototype language-detection logic is ready "
            "to be considered for news_translator.py."
        )
    else:
        print("SOME TESTS FAILED")
        print()
        print(
            "Do NOT modify news_translator.py yet."
        )


# ============================================================
# تشغيل الملف
# ============================================================

if __name__ == "__main__":
    main()

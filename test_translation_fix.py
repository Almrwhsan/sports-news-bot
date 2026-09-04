from sources.news_translator import (
    needs_translation,
    translate_news_item,
)


def test_translation_case(name, news):

    print("\n" + "=" * 60)
    print(name)
    print("=" * 60)

    print("Language:", news.get("language"))
    print("Original title:", news.get("title"))

    print(
        "Needs translation:",
        needs_translation(news)
    )

    result = translate_news_item(news)

    print(
        "Arabic title:",
        result.get("arabic_title")
    )

    print(
        "Arabic summary:",
        result.get("arabic_summary")
    )


def main():

    # ========================================================
    # TEST 1 — الخبر الإسباني الذي فشل سابقًا
    # ========================================================

    test_translation_case(
        "TEST 1 — Spanish AS",
        {
            "language": "ar",
            "title": (
                "La Cartuja: el estadio en el que nació "
                "la leyenda de José Mourinho"
            ),
            "summary": (
                "El portugués levantó en el recinto "
                "sevillano su primer título europeo, "
                "la UEFA, en 2003."
            ),
        }
    )

    # ========================================================
    # TEST 2 — خبر إنجليزي
    # ========================================================

    test_translation_case(
        "TEST 2 — English BBC",
        {
            "language": "en",
            "title": (
                "David Moyes admits he wanted to do more "
                "business on deadline day"
            ),
            "summary": (
                "David Moyes says he has to live with "
                "the disappointment after wanting to do more."
            ),
        }
    )

    # ========================================================
    # TEST 3 — خبر عربي
    # ========================================================

    test_translation_case(
        "TEST 3 — Arabic",
        {
            "language": "ar",
            "title": (
                "مويز يعيش بخيبة أمل بعد يوم الموعد النهائي"
            ),
            "summary": (
                "اعترف ديفيد مويس بأنه يتعين عليه "
                "التعايش مع خيبات الأمل."
            ),
        }
    )

    # ========================================================
    # TEST 4 — إسباني مع language خاطئة
    # ========================================================

    test_translation_case(
        "TEST 4 — Spanish with wrong language field",
        {
            "language": "arabic",
            "title": (
                "El Real Madrid prepara su próximo partido"
            ),
            "summary": (
                "El equipo trabaja para llegar preparado."
            ),
        }
    )


if __name__ == "__main__":
    main()

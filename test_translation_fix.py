# ============================================================
# تشخيص مشكلة ترجمة الأخبار
# ============================================================

from sources.news_translator import (
    clean_text,
    is_arabic_text,
    needs_translation,
    translate_news_item,
)


# ============================================================
# طباعة نتيجة التشخيص
# ============================================================

def debug_news(name, news):

    print("\n" + "=" * 70)
    print(name)
    print("=" * 70)

    print("Language      :", repr(news.get("language")))
    print("Source        :", repr(news.get("source")))
    print("URL           :", repr(news.get("url")))

    print("Original title:")
    print(news.get("title", ""))

    print("\nOriginal summary:")
    print(news.get("summary", ""))

    print("\n--- LANGUAGE DIAGNOSIS ---")

    title = clean_text(
        news.get("title", "")
    )

    summary = clean_text(
        news.get("summary", "")
    )

    combined = (
        f"{title} {summary}"
    ).strip()

    print(
        "is_arabic_text(title):",
        is_arabic_text(title)
    )

    print(
        "is_arabic_text(summary):",
        is_arabic_text(summary)
    )

    print(
        "is_arabic_text(combined):",
        is_arabic_text(combined)
    )

    print(
        "needs_translation:",
        needs_translation(news)
    )

    # --------------------------------------------------------
    # الترجمة الفعلية
    # --------------------------------------------------------

    print("\n--- TRANSLATION RESULT ---")

    result = translate_news_item(
        news
    )

    print(
        "Arabic title:"
    )

    print(
        result.get(
            "arabic_title",
            ""
        )
    )

    print(
        "\nArabic summary:"
    )

    print(
        result.get(
            "arabic_summary",
            ""
        )
    )


# ============================================================
# الاختبار
# ============================================================

def main():

    # ========================================================
    # TEST 1
    # نفس الخبر الإسباني الذي فشل في البوت
    # ========================================================

    debug_news(
        "TEST 1 — Original Spanish AS failure",
        {
            "language": "ar",

            "source": "AS Real Madrid",

            "url": (
                "https://as.com/futbol/"
                "la-cartuja-el-estadio-en-el-que-nacio-"
                "la-leyenda-de-jose-mourinho-f202609-n/"
            ),

            "title": (
                "La Cartuja: el estadio en el que nació "
                "la leyenda de José Mourinho"
            ),

            "summary": (
                "El portugués levantó en el recinto "
                "sevillano su primer título europeo, "
                "la UEFA, en 2003. El Real Madrid ganó "
                "allí la final de Copa 2023 y luego perdió "
                "la de 2025, ante el Barcelona."
            ),
        }
    )

    # ========================================================
    # TEST 2
    # نفس خبر BBC الذي نجح
    # ========================================================

    debug_news(
        "TEST 2 — Original English BBC success",
        {
            "language": "en",

            "source": "BBC Sport Football",

            "url": (
                "https://www.bbc.co.uk/sport/football/"
                "articles/c3v49617lzko"
            ),

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
    # TEST 3
    # خبر عربي حقيقي
    # ========================================================

    debug_news(
        "TEST 3 — Arabic news",
        {
            "language": "ar",

            "source": "BBC Sport Football",

            "url": "",

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
    # TEST 4
    # إسباني مع language خاطئة
    # ========================================================

    debug_news(
        "TEST 4 — Spanish with incorrect language field",
        {
            "language": "arabic",

            "source": "AS Real Madrid",

            "url": "",

            "title": (
                "El Real Madrid prepara su próximo partido"
            ),

            "summary": (
                "El equipo trabaja para llegar preparado."
            ),
        }
    )


# ============================================================
# تشغيل الاختبار
# ============================================================

if __name__ == "__main__":
    main()

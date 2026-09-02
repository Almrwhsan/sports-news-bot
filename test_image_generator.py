# ============================================================
# اختبار توليد صور الأخبار
# ============================================================

from image_generator import generate_news_image


# ============================================================
# البرنامج الرئيسي
# ============================================================

def main():

    print("===================================")
    print("       IMAGE GENERATOR TEST")
    print("===================================")

    tests = [

        {
            "title": "ريال مدريد يستعد لمواجهة قوية في الدوري الإسباني",
            "category": "football",
            "image_path": None,
        },

        {
            "title": "صفقة جديدة تقترب من ريال مدريد",
            "category": "transfers",
            "image_path": None,
        },

        {
            "title": "اختبار توليد صورة بخلفية خبر",
            "category": "matches",
            "image_path": None,
        },

    ]

    successful = 0

    # --------------------------------------------------------
    # تشغيل الاختبارات
    # --------------------------------------------------------

    for index, test in enumerate(
        tests,
        start=1
    ):

        print()
        print("-----------------------------------")
        print(
            f"GENERATOR TEST {index}"
        )
        print("-----------------------------------")

        print(
            "Title:",
            test["title"]
        )

        print(
            "Category:",
            test["category"]
        )

        try:

            result = generate_news_image(
                title=test["title"],
                category=test["category"],
                image_path=test["image_path"]
            )

            if result:

                successful += 1

                print()
                print(
                    "✅ IMAGE GENERATED"
                )

                print(
                    "Output:",
                    result
                )

            else:

                print()
                print(
                    "❌ IMAGE GENERATION FAILED"
                )

        except Exception as error:

            print()
            print(
                "❌ Generator error:",
                error
            )

    # --------------------------------------------------------
    # الملخص
    # --------------------------------------------------------

    print()
    print("===================================")
    print("      IMAGE GENERATOR SUMMARY")
    print("===================================")

    print()

    print(
        f"Successful generations: "
        f"{successful}/{len(tests)}"
    )

    print()

    if successful > 0:

        print(
            "✅ IMAGE GENERATOR IS WORKING"
        )

    else:

        print(
            "❌ IMAGE GENERATOR FAILED"
        )

        raise SystemExit(1)

    print()
    print("===================================")
    print("     IMAGE GENERATOR TEST END")
    print("===================================")


# ============================================================
# تشغيل الاختبار
# ============================================================

if __name__ == "__main__":

    main()

# ============================================================
# اختبار جلب صور الأخبار
# ============================================================

from image_fetcher import fetch_news_image


def main():

    print("===================================")
    print("       IMAGE FETCHER TEST")
    print("===================================")

    titles = [
        "Real Madrid signs a new midfielder",
        "Barcelona announce new signing",
        "Manchester City complete major transfer",
    ]

    successful = 0

    for index, title in enumerate(
        titles,
        start=1
    ):

        print()
        print(
            f"TEST {index}"
        )

        print(
            f"Title: {title}"
        )

        try:

            image = fetch_news_image(
                title=title
            )

            if image:

                successful += 1

                print(
                    "Image result: FOUND"
                )

                print(
                    f"Image: {image}"
                )

            else:

                print(
                    "Image result: NOT FOUND"
                )

        except Exception as error:

            print(
                f"❌ Error: {error}"
            )

    print()
    print("===================================")
    print("       IMAGE TEST SUMMARY")
    print("===================================")

    print()
    print(
        f"Successful image results: "
        f"{successful}/3"
    )

    if successful > 0:

        print()
        print(
            "✅ IMAGE FETCHER IS WORKING"
        )

    else:

        print()
        print(
            "❌ NO IMAGE RESULTS FOUND"
        )

        raise SystemExit(1)

    print()
    print("===================================")
    print("      IMAGE FETCHER TEST END")
    print("===================================")


if __name__ == "__main__":

    main()

# ============================================================
# اختبار المصادر العربية
# ============================================================

from sources.arabic_sources import ARABIC_SOURCES
from sources.source_manager import fetch_source


def main():

    print("===================================")
    print("     ARABIC SOURCES TEST")
    print("===================================")

    total = 0

    for source in ARABIC_SOURCES:

        print()
        print("-----------------------------------")
        print(f"Source: {source['name']}")
        print(f"Feed: {source['feed']}")

        news = fetch_source(source)

        print(
            f"Entries received: {len(news)}"
        )

        if news:

            total += len(news)

            print("Status: ✅ WORKING")

            print()
            print("Latest title:")

            print(
                news[0]["title"]
            )

        else:

            print("Status: ❌ NO NEWS")

    print()
    print("===================================")
    print(
        f"TOTAL ARABIC NEWS: {total}"
    )
    print("===================================")


if __name__ == "__main__":
    main()

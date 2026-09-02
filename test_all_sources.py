# ============================================================
# اختبار جميع مصادر الأخبار
# ============================================================

from sources.sources_config import ALL_SOURCES
from sources.source_manager import fetch_all_sources


def main():

    print("===================================")
    print("       ALL SOURCES TEST")
    print("===================================")

    print()
    print(
        f"Total configured sources: "
        f"{len(ALL_SOURCES)}"
    )

    print()
    print("Configured sources:")

    for source in ALL_SOURCES:

        print(
            f"- {source['name']} "
            f"| Priority: {source['priority']} "
            f"| Enabled: {source['enabled']}"
        )

    print()
    print("===================================")
    print("       FETCHING ALL SOURCES")
    print("===================================")

    news = fetch_all_sources(
        ALL_SOURCES
    )

    print()
    print("===================================")
    print(
        f"TOTAL NEWS: {len(news)}"
    )
    print("===================================")

    for index, item in enumerate(
        news[:10],
        start=1
    ):

        print()
        print(
            f"{index}. {item['title']}"
        )

        print(
            f"Source: {item['source']}"
        )

        print(
            f"Category: {item['category']}"
        )

        print(
            f"Priority: {item['priority']}"
        )


if __name__ == "__main__":
    main()

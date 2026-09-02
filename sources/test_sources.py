import feedparser

from sources.global_sources import GLOBAL_SOURCES


def main():

    print("===================================")
    print("       GLOBAL SOURCES TEST")
    print("===================================")

    for source in GLOBAL_SOURCES:

        print()
        print(f"Source: {source['name']}")
        print(f"Feed: {source['feed']}")

        try:

            feed = feedparser.parse(
                source["feed"]
            )

            print(
                f"Entries: {len(feed.entries)}"
            )

            if feed.bozo:
                print("⚠️ Feed warning detected.")

            if feed.entries:

                first = feed.entries[0]

                print(
                    f"Latest title: "
                    f"{first.get('title', 'No title')}"
                )

                print("✅ Source works.")

            else:

                print(
                    "❌ No entries found."
                )

        except Exception as error:

            print(
                f"❌ Error: {error}"
            )

    print()
    print("===================================")
    print("          TEST FINISHED")
    print("===================================")


if __name__ == "__main__":
    main()

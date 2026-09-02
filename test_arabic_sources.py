# ============================================================
# تشخيص مصادر FilGoal
# ============================================================

import requests

from sources.arabic_sources import ARABIC_SOURCES


def main():

    print("===================================")
    print("     FILGOAL RSS DIAGNOSTIC")
    print("===================================")

    for source in ARABIC_SOURCES:

        print()
        print("-----------------------------------")
        print(f"Source: {source['name']}")
        print(f"URL: {source['feed']}")

        try:

            response = requests.get(
                source["feed"],
                timeout=30,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 "
                        "(Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 "
                        "(KHTML, like Gecko) "
                        "Chrome/131.0 Safari/537.36"
                    )
                }
            )

            print(
                f"HTTP Status: "
                f"{response.status_code}"
            )

            print(
                f"Content-Type: "
                f"{response.headers.get('content-type')}"
            )

            print(
                f"Content-Length: "
                f"{len(response.content)}"
            )

            print()
            print("Response preview:")

            print(
                response.text[:500]
            )

        except requests.RequestException as error:

            print(
                f"❌ Request failed: {error}"
            )

    print()
    print("===================================")
    print("          DIAGNOSTIC END")
    print("===================================")


if __name__ == "__main__":
    main()

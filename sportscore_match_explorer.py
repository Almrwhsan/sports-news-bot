import json
import requests
from pprint import pprint


SPORTSCORE_MATCH_URL = "https://sportscore.com/api/widget/match/"

MATCH_SLUG = "real-betis-vs-real-madrid"

TIMEOUT = 30


def fetch_match(slug: str):
    params = {
        "sport": "football",
        "slug": slug,
        "src": "nabd-madrid",
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    }

    response = requests.get(
        SPORTSCORE_MATCH_URL,
        params=params,
        headers=headers,
        timeout=TIMEOUT,
    )

    print("=" * 80)
    print("SPORTSCORE DATA EXPLORER")
    print("=" * 80)
    print("HTTP:", response.status_code)
    print("URL :", response.url)
    print()

    response.raise_for_status()

    data = response.json()

    return data


def print_structure(value, prefix=""):
    """
    طباعة بنية JSON بدون إغراق الشاشة بالقيم الكبيرة.
    """
    if isinstance(value, dict):
        for key, child in value.items():
            print(f"{prefix}{key}: {type(child).__name__}")

            if isinstance(child, dict):
                print_structure(child, prefix + "  ")

            elif isinstance(child, list):
                print(f"{prefix}  LIST LENGTH: {len(child)}")

                if child:
                    first = child[0]
                    print(f"{prefix}  FIRST ITEM TYPE: {type(first).__name__}")

                    if isinstance(first, dict):
                        print_structure(first, prefix + "    ")

    elif isinstance(value, list):
        print(f"{prefix}LIST LENGTH: {len(value)}")


def find_keys(value, target_keys, path="root", results=None):
    """
    يبحث بشكل recursive عن مفاتيح معينة داخل JSON.
    """
    if results is None:
        results = []

    if isinstance(value, dict):
        for key, child in value.items():

            key_lower = str(key).lower()

            if key_lower in target_keys:
                results.append(
                    {
                        "path": f"{path}.{key}",
                        "value": child,
                    }
                )

            find_keys(
                child,
                target_keys,
                f"{path}.{key}",
                results,
            )

    elif isinstance(value, list):
        for index, child in enumerate(value):
            find_keys(
                child,
                target_keys,
                f"{path}[{index}]",
                results,
            )

    return results


def print_section(title):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)


def main():
    data = fetch_match(MATCH_SLUG)

    print_section("TOP LEVEL STRUCTURE")

    if isinstance(data, dict):
        for key, value in data.items():
            print(f"{key}: {type(value).__name__}")
    else:
        print("Unexpected root type:", type(data).__name__)

    print_section("FULL JSON STRUCTURE")

    print_structure(data)

    target_keys = {
        "home",
        "away",
        "home_team",
        "away_team",
        "teams",
        "logo",
        "image",
        "image_url",
        "slug",
        "league",
        "competition",
        "tournament",
        "venue",
        "stadium",
        "referee",
        "coach",
        "coaches",
        "lineups",
        "lineup",
        "formation",
        "players",
        "starting_xi",
        "bench",
        "substitutions",
        "incidents",
        "statistics",
        "stats",
        "events",
        "status",
        "status_text",
        "score",
        "home_score",
        "away_score",
        "tracker",
    }

    results = find_keys(data, target_keys)

    print_section("IMPORTANT DATA FOUND")

    for item in results:
        print()
        print("PATH:")
        print(item["path"])

        print("VALUE:")

        try:
            print(
                json.dumps(
                    item["value"],
                    ensure_ascii=False,
                    indent=2,
                )
            )
        except TypeError:
            pprint(item["value"])

    print_section("RAW JSON SAVED")

    output_file = "sportscore_match_raw.json"

    with open(
        output_file,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print(f"Saved to: {output_file}")

    print()
    print("=" * 80)
    print("EXPLORATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()

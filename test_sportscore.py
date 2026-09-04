import json
import requests
from datetime import datetime, timezone


BASE_URL = "https://sportscore.com/api/widget"

HEADERS = {
    "User-Agent": "Nabd-Madrid-Live-Test/1.0",
    "Accept": "application/json",
}


def request_api(endpoint, params):
    url = f"{BASE_URL}/{endpoint}/"

    print("\n" + "=" * 70)
    print(f"REQUEST: {url}")
    print(f"PARAMS : {params}")

    try:
        response = requests.get(
            url,
            params=params,
            headers=HEADERS,
            timeout=20,
        )

        print(f"HTTP   : {response.status_code}")

        response.raise_for_status()

        data = response.json()

        print("JSON   : OK")

        return data

    except requests.RequestException as exc:
        print(f"REQUEST ERROR: {exc}")
        return None

    except ValueError as exc:
        print(f"JSON ERROR: {exc}")
        return None


def print_structure(data, name):
    print("\n" + "-" * 70)
    print(f"{name} RESPONSE STRUCTURE")
    print("-" * 70)

    if data is None:
        print("No data.")
        return

    print(f"Top-level type: {type(data).__name__}")

    if isinstance(data, dict):
        print("Top-level keys:")
        for key in data.keys():
            print(f"  - {key}")

    elif isinstance(data, list):
        print(f"List length: {len(data)}")

    print("\nSample JSON:")
    print(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        )[:12000]
    )


def test_live_matches():
    print("\n\n")
    print("#" * 70)
    print("TEST 1 — LIVE FOOTBALL MATCHES")
    print("#" * 70)

    data = request_api(
        "matches",
        {
            "sport": "football",
            "limit": 50,
            "src": "nabd-madrid",
        },
    )

    print_structure(data, "LIVE MATCHES")

    return data


def test_real_madrid():
    print("\n\n")
    print("#" * 70)
    print("TEST 2 — REAL MADRID")
    print("#" * 70)

    data = request_api(
        "team",
        {
            "sport": "football",
            "slug": "real-madrid",
            "limit": 10,
            "src": "nabd-madrid",
        },
    )

    print_structure(data, "REAL MADRID")

    return data


def test_barcelona():
    print("\n\n")
    print("#" * 70)
    print("TEST 3 — BARCELONA")
    print("#" * 70)

    data = request_api(
        "team",
        {
            "sport": "football",
            "slug": "barcelona",
            "limit": 10,
            "src": "nabd-madrid",
        },
    )

    print_structure(data, "BARCELONA")

    return data


def test_ucl():
    print("\n\n")
    print("#" * 70)
    print("TEST 4 — UEFA CHAMPIONS LEAGUE")
    print("#" * 70)

    data = request_api(
        "bracket",
        {
            "sport": "football",
            "slug": "uefa-champions-league",
            "src": "nabd-madrid",
        },
    )

    print_structure(data, "UEFA CHAMPIONS LEAGUE")

    return data


def test_la_liga():
    print("\n\n")
    print("#" * 70)
    print("TEST 5 — LA LIGA")
    print("#" * 70)

    data = request_api(
        "standings",
        {
            "sport": "football",
            "slug": "spanish-la-liga",
            "src": "nabd-madrid",
        },
    )

    print_structure(data, "LA LIGA")

    return data


def main():
    print("=" * 70)
    print("NABD MADRID — SPORTScore API TEST")
    print("=" * 70)

    print(
        "UTC:",
        datetime.now(timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    print("\nNo API key is required for this test.")

    test_live_matches()
    test_real_madrid()
    test_barcelona()
    test_ucl()
    test_la_liga()

    print("\n\n")
    print("=" * 70)
    print("SPORTSCORE TEST FINISHED")
    print("=" * 70)


if __name__ == "__main__":
    main()

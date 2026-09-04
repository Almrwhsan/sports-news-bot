import json
import requests
from datetime import datetime, timezone


# ============================================================
# SPORTScore API
# ============================================================

BASE_URL = "https://sportscore.com/api/widget"

HEADERS = {
    "User-Agent": "Nabd-Madrid-Live-Test/1.0",
    "Accept": "application/json",
}


# ============================================================
# طلب API
# ============================================================

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


# ============================================================
# طباعة بنية الاستجابة
# ============================================================

def print_structure(data, name, max_chars=12000):

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

    try:

        formatted = json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
        )

        print(formatted[:max_chars])

        if len(formatted) > max_chars:
            print(
                f"\n... OUTPUT TRUNCATED "
                f"(showing first {max_chars} characters)"
            )

    except Exception as exc:

        print(f"Could not format JSON: {exc}")


# ============================================================
# البحث عن مفاتيح الأحداث بشكل مرن
# ============================================================

def find_event_sections(data, path="root"):

    if isinstance(data, dict):

        for key, value in data.items():

            key_lower = str(key).lower()

            if any(
                word in key_lower
                for word in (
                    "event",
                    "timeline",
                    "incident",
                    "commentary",
                )
            ):

                print("\n" + "*" * 70)
                print("POSSIBLE EVENT / TIMELINE DATA")
                print("*" * 70)

                print(f"Path : {path}.{key}")
                print(f"Type : {type(value).__name__}")

                try:

                    print(
                        json.dumps(
                            value,
                            ensure_ascii=False,
                            indent=2,
                        )[:15000]
                    )

                except Exception as exc:

                    print(f"Could not print section: {exc}")

            find_event_sections(
                value,
                f"{path}.{key}",
            )

    elif isinstance(data, list):

        for index, item in enumerate(data[:100]):

            find_event_sections(
                item,
                f"{path}[{index}]",
            )


# ============================================================
# TEST 1
# المباريات المباشرة
# ============================================================

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

    print_structure(
        data,
        "LIVE MATCHES",
    )

    return data


# ============================================================
# TEST 2
# ريال مدريد
# ============================================================

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

    print_structure(
        data,
        "REAL MADRID",
    )

    return data


# ============================================================
# TEST 3
# برشلونة
# ============================================================

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

    print_structure(
        data,
        "BARCELONA",
    )

    return data


# ============================================================
# TEST 4
# دوري أبطال أوروبا
# ============================================================

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

    print_structure(
        data,
        "UEFA CHAMPIONS LEAGUE",
    )

    return data


# ============================================================
# TEST 5
# الدوري الإسباني
# ============================================================

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

    print_structure(
        data,
        "LA LIGA",
    )

    return data


# ============================================================
# TEST 6
# تفاصيل مباراة محددة + الأحداث
# ============================================================

def test_match_detail():

    print("\n\n")
    print("#" * 70)
    print("TEST 6 — MATCH DETAIL + TIMELINE / EVENTS")
    print("#" * 70)

    # مباراة ظهرت فعليًا في اختبار TEST 1
    match_slug = "platense-vs-cd-olimpia"

    print(f"\nMATCH SLUG: {match_slug}")

    data = request_api(
        "match",
        {
            "sport": "football",
            "slug": match_slug,
            "src": "nabd-madrid",
        },
    )

    # طباعة الاستجابة كاملة بشكل منظم
    print_structure(
        data,
        "MATCH DETAIL",
        max_chars=20000,
    )

    # البحث عن timeline/events مهما كان اسم المفتاح
    if data is not None:

        print("\n\n")
        print("#" * 70)
        print("SEARCHING FOR TIMELINE / EVENTS")
        print("#" * 70)

        find_event_sections(data)

    return data


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("NABD MADRID — SPORTScore API TEST")
    print("=" * 70)

    print(
        "UTC:",
        datetime.now(timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
    )

    print("\nNo API key is required for this test.")

    # --------------------------------------------------------
    # الاختبارات الحالية
    # --------------------------------------------------------

    test_live_matches()

    test_real_madrid()

    test_barcelona()

    test_ucl()

    test_la_liga()

    # --------------------------------------------------------
    # الاختبار الجديد
    # --------------------------------------------------------

    test_match_detail()

    # --------------------------------------------------------
    # النهاية
    # --------------------------------------------------------

    print("\n\n")
    print("=" * 70)
    print("SPORTSCORE TEST FINISHED")
    print("=" * 70)


# ============================================================
# تشغيل البرنامج
# ============================================================

if __name__ == "__main__":
    main()

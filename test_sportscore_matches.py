import time
import requests


# ============================================================
# إعدادات SportScore
# ============================================================

URL = "https://sportscore.com/api/widget/matches/"

PARAMS = {
    "sport": "football",
    "limit": 20,
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(compatible; NabdMadridLiveBot/1.0)"
    ),
    "Accept": "application/json",
}

MAX_RETRIES = 5
RETRY_DELAY = 15
TIMEOUT = 30


# ============================================================
# بدء الاختبار
# ============================================================

print("=" * 70)
print("SPORTSCORE MATCHES API TEST")
print("=" * 70)

session = requests.Session()
session.headers.update(HEADERS)


# ============================================================
# تنفيذ الطلب مع إعادة المحاولة
# ============================================================

for attempt in range(1, MAX_RETRIES + 1):

    print()
    print(f"ATTEMPT {attempt}/{MAX_RETRIES}")

    try:

        response = session.get(
            URL,
            params=PARAMS,
            timeout=TIMEOUT,
        )

        print("HTTP STATUS:", response.status_code)
        print("FINAL URL:", response.url)

        # ----------------------------------------------------
        # نجاح الطلب
        # ----------------------------------------------------

        if response.ok:

            data = response.json()

            print()
            print("JSON TYPE:", type(data).__name__)

            # ------------------------------------------------
            # معرفة مكان قائمة المباريات
            # ------------------------------------------------

            matches = []

            if isinstance(data, dict):

                if isinstance(data.get("matches"), list):
                    matches = data["matches"]

                elif isinstance(data.get("data"), list):
                    matches = data["data"]

                elif isinstance(data.get("results"), list):
                    matches = data["results"]

                elif isinstance(data.get("events"), list):
                    matches = data["events"]

            elif isinstance(data, list):

                matches = data

            # ------------------------------------------------
            # عرض ملخص المباريات
            # ------------------------------------------------

            print()
            print("=" * 70)
            print("MATCHES SUMMARY")
            print("=" * 70)

            print("TOTAL MATCHES:", len(matches))

            if not matches:

                print()
                print("WARNING: No matches list detected.")

                print()
                print("=" * 70)
                print("RESPONSE KEYS")
                print("=" * 70)

                if isinstance(data, dict):
                    print(list(data.keys()))

                print()
                print("=" * 70)
                print("RAW RESPONSE")
                print("=" * 70)

                print(data)

            # ------------------------------------------------
            # طباعة كل مباراة
            # ------------------------------------------------

            for index, match in enumerate(matches, start=1):

                if not isinstance(match, dict):
                    print()
                    print(f"#{index}")
                    print("INVALID MATCH OBJECT:", match)
                    continue

                print()
                print("-" * 70)
                print(f"#{index}")
                print("-" * 70)

                print(
                    "HOME:",
                    match.get("home")
                )

                print(
                    "AWAY:",
                    match.get("away")
                )

                print(
                    "SCORE:",
                    match.get("home_score"),
                    "-",
                    match.get("away_score")
                )

                print(
                    "STATUS:",
                    match.get("status")
                )

                print(
                    "STATUS TEXT:",
                    match.get("status_text")
                )

                print(
                    "TIME:",
                    match.get("time")
                )

                print(
                    "COMPETITION:",
                    match.get("competition")
                )

                print(
                    "URL:",
                    match.get("url")
                )

                print(
                    "HOME LOGO:",
                    match.get("home_logo")
                )

                print(
                    "AWAY LOGO:",
                    match.get("away_logo")
                )

                print(
                    "COMPETITION LOGO:",
                    match.get("competition_logo")
                )

            # ------------------------------------------------
            # إنهاء الاختبار
            # ------------------------------------------------

            print()
            print("=" * 70)
            print("TEST PASSED")
            print("=" * 70)

            break

        # ----------------------------------------------------
        # أخطاء مؤقتة
        # ----------------------------------------------------

        if response.status_code in {
            429,
            500,
            502,
            503,
            504,
        }:

            print(
                f"Temporary HTTP error "
                f"{response.status_code}."
            )

            if attempt < MAX_RETRIES:

                print(
                    f"Retrying in "
                    f"{RETRY_DELAY} seconds..."
                )

                time.sleep(RETRY_DELAY)

                continue

        # ----------------------------------------------------
        # خطأ غير مؤقت
        # ----------------------------------------------------

        print()
        print("=" * 70)
        print("API REQUEST FAILED")
        print("=" * 70)

        print(response.text[:2000])

        response.raise_for_status()

    except requests.RequestException as error:

        print()
        print(
            "REQUEST ERROR:",
            type(error).__name__,
        )

        print(error)

        if attempt < MAX_RETRIES:

            print(
                f"Retrying in "
                f"{RETRY_DELAY} seconds..."
            )

            time.sleep(RETRY_DELAY)

            continue

        raise

    except ValueError as error:

        print()
        print("INVALID JSON:", error)

        print()
        print("SERVER RESPONSE:")

        print(response.text[:2000])

        raise

else:

    print()
    print("=" * 70)
    print("ALL RETRIES FAILED")
    print("=" * 70)

    raise SystemExit(1)

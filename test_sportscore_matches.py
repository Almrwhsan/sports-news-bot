import time
import requests


# ============================================================
# إعدادات SportScore
# ============================================================

URL = "https://sportscore.com/api/widget/matches/"

PARAMS = {
    "sport": "football",
    "limit": 100,
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
print("SPORTSCORE MATCHES API — LARGE LIMIT TEST")
print("=" * 70)

session = requests.Session()
session.headers.update(HEADERS)


# ============================================================
# تنفيذ الطلب
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
        # نجاح
        # ----------------------------------------------------

        if response.ok:

            data = response.json()

            print()
            print("JSON TYPE:", type(data).__name__)

            # ------------------------------------------------
            # استخراج المباريات
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
            # الملخص
            # ------------------------------------------------

            print()
            print("=" * 70)
            print("MATCHES SUMMARY")
            print("=" * 70)

            print("REQUESTED LIMIT:", PARAMS["limit"])
            print("TOTAL MATCHES:", len(matches))

            # ------------------------------------------------
            # إحصائيات البطولات
            # ------------------------------------------------

            competitions = {}

            for match in matches:

                if not isinstance(match, dict):
                    continue

                competition = match.get(
                    "competition",
                    "Unknown"
                )

                competitions[competition] = (
                    competitions.get(competition, 0) + 1
                )

            print()
            print("=" * 70)
            print("COMPETITIONS FOUND")
            print("=" * 70)

            for competition, count in sorted(
                competitions.items(),
                key=lambda item: (-item[1], item[0])
            ):

                print(
                    f"{count:3} | {competition}"
                )

            # ------------------------------------------------
            # عرض جميع المباريات
            # ------------------------------------------------

            print()
            print("=" * 70)
            print("ALL MATCHES")
            print("=" * 70)

            for index, match in enumerate(
                matches,
                start=1
            ):

                if not isinstance(match, dict):
                    continue

                print()
                print(
                    f"#{index} "
                    f"{match.get('home')} "
                    f"vs "
                    f"{match.get('away')}"
                )

                print(
                    "  STATUS:",
                    match.get("status"),
                    "|",
                    match.get("status_text")
                )

                print(
                    "  TIME:",
                    match.get("time")
                )

                print(
                    "  COMPETITION:",
                    match.get("competition")
                )

                print(
                    "  URL:",
                    match.get("url")
                )

            # ------------------------------------------------
            # النجاح
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
        # خطأ نهائي
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

import time
import json
import requests


# ============================================================
# إعدادات الاختبار
# ============================================================

URL = "https://sportscore.com/api/widget/team/"

PARAMS = {
    "sport": "football",
    "slug": "real-madrid",
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
print("SPORTSCORE TEAM API TEST")
print("=" * 70)

print()
print("TEAM: Real Madrid")
print("SLUG:", PARAMS["slug"])


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

        print(
            "HTTP STATUS:",
            response.status_code
        )

        print(
            "FINAL URL:",
            response.url
        )

        # ----------------------------------------------------
        # نجاح
        # ----------------------------------------------------

        if response.ok:

            data = response.json()

            print()
            print(
                "JSON TYPE:",
                type(data).__name__
            )

            # ------------------------------------------------
            # عرض مفاتيح الاستجابة
            # ------------------------------------------------

            if isinstance(data, dict):

                print()
                print("=" * 70)
                print("RESPONSE KEYS")
                print("=" * 70)

                print(
                    list(data.keys())
                )

            # ------------------------------------------------
            # عرض الاستجابة كاملة
            # ------------------------------------------------

            print()
            print("=" * 70)
            print("FULL RESPONSE")
            print("=" * 70)

            print(
                json.dumps(
                    data,
                    ensure_ascii=False,
                    indent=2,
                )
            )

            # ------------------------------------------------
            # نجاح الاختبار
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

        print(
            response.text[:3000]
        )

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
        print(
            "INVALID JSON:",
            error
        )

        print()
        print(
            "SERVER RESPONSE:"
        )

        print(
            response.text[:3000]
        )

        raise

else:

    print()
    print("=" * 70)
    print("ALL RETRIES FAILED")
    print("=" * 70)

    raise SystemExit(1)

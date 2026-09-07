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
# الفرق المهمة عالميًا
# ============================================================

IMPORTANT_TEAMS = [
    "real madrid",
    "barcelona",
    "atletico madrid",
    "atlético madrid",
    "manchester city",
    "manchester united",
    "liverpool",
    "arsenal",
    "chelsea",
    "tottenham",
    "newcastle",
    "aston villa",
    "bayern",
    "borussia dortmund",
    "dortmund",
    "bayer leverkusen",
    "inter",
    "internazionale",
    "inter milan",
    "juventus",
    "milan",
    "ac milan",
    "napoli",
    "roma",
    "paris saint-germain",
    "psg",
    "lyon",
    "marseille",
    "ajax",
    "psv",
    "benfica",
    "porto",
    "sporting",
]


# ============================================================
# البطولات المهمة
# ============================================================

IMPORTANT_COMPETITIONS = [
    "uefa champions league",
    "champions league",

    "uefa europa league",
    "europa league",

    "uefa conference league",
    "conference league",

    "la liga",
    "laliga",
    "spanish la liga",

    "premier league",
    "english premier league",

    "serie a",
    "italian serie a",

    "bundesliga",
    "german bundesliga",

    "ligue 1",
    "french ligue 1",

    "copa del rey",
    "fa cup",
    "carabao cup",

    "coppa italia",
    "dfb pokal",

    "club world cup",
    "fifa club world cup",

    "world cup",
    "fifa world cup",

    "euro",
    "uefa european championship",

    "copa america",

    "afcon",
    "africa cup of nations",
]


# ============================================================
# بطولات/أنواع يجب استبعادها
# ============================================================

EXCLUDED_KEYWORDS = [
    "women",
    "(w)",
    "female",

    "u17",
    "u18",
    "u19",
    "u20",
    "u21",
    "u23",

    "youth",
    "junior",

    "reserve",
    "reserves",

    "b team",
    "b-team",

    "ii",
    "academy",

    "division 4",
    "division 5",

    "amateur",
]


# ============================================================
# دالة التطبيع
# ============================================================

def normalize_text(value):
    if value is None:
        return ""

    return (
        str(value)
        .strip()
        .lower()
    )


# ============================================================
# استخراج قائمة المباريات
# ============================================================

def extract_matches(data):

    if isinstance(data, list):
        return data

    if not isinstance(data, dict):
        return []

    possible_keys = [
        "matches",
        "data",
        "results",
        "events",
    ]

    for key in possible_keys:

        value = data.get(key)

        if isinstance(value, list):
            return value

    return []


# ============================================================
# بدء الاختبار
# ============================================================

print("=" * 70)
print("SPORTSCORE MATCHES API — IMPORTANT MATCH DISCOVERY TEST")
print("=" * 70)


session = requests.Session()

session.headers.update(HEADERS)


# ============================================================
# الاتصال مع إعادة المحاولة
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

            matches = extract_matches(data)

            print()
            print("=" * 70)
            print("GENERAL RESULT")
            print("=" * 70)

            print(
                "REQUESTED LIMIT:",
                PARAMS["limit"]
            )

            print(
                "TOTAL MATCHES:",
                len(matches)
            )

            # ------------------------------------------------
            # تحليل المباريات المهمة
            # ------------------------------------------------

            important_matches = []

            excluded_matches = []

            for index, match in enumerate(
                matches,
                start=1
            ):

                if not isinstance(match, dict):
                    continue

                home = normalize_text(
                    match.get("home")
                )

                away = normalize_text(
                    match.get("away")
                )

                competition = normalize_text(
                    match.get("competition")
                )

                combined_text = (
                    f"{home} "
                    f"{away} "
                    f"{competition}"
                )

                # --------------------------------------------
                # استبعاد
                # --------------------------------------------

                excluded_reason = None

                for keyword in EXCLUDED_KEYWORDS:

                    if keyword in combined_text:

                        excluded_reason = keyword
                        break

                if excluded_reason:

                    excluded_matches.append(
                        {
                            "index": index,
                            "home": match.get("home"),
                            "away": match.get("away"),
                            "competition": match.get(
                                "competition"
                            ),
                            "reason": excluded_reason,
                        }
                    )

                    continue

                # --------------------------------------------
                # البحث عن فريق مهم
                # --------------------------------------------

                matched_teams = []

                for team in IMPORTANT_TEAMS:

                    if (
                        team in home
                        or team in away
                    ):

                        matched_teams.append(team)

                # --------------------------------------------
                # البحث عن بطولة مهمة
                # --------------------------------------------

                matched_competitions = []

                for competition_name in (
                    IMPORTANT_COMPETITIONS
                ):

                    if (
                        competition_name
                        in competition
                    ):

                        matched_competitions.append(
                            competition_name
                        )

                # --------------------------------------------
                # اعتبار المباراة مهمة
                # --------------------------------------------

                if (
                    matched_teams
                    or matched_competitions
                ):

                    important_matches.append(
                        {
                            "index": index,
                            "home": match.get("home"),
                            "away": match.get("away"),
                            "home_score": match.get(
                                "home_score"
                            ),
                            "away_score": match.get(
                                "away_score"
                            ),
                            "status": match.get(
                                "status"
                            ),
                            "status_text": match.get(
                                "status_text"
                            ),
                            "time": match.get(
                                "time"
                            ),
                            "competition": match.get(
                                "competition"
                            ),
                            "url": match.get(
                                "url"
                            ),
                            "matched_teams": matched_teams,
                            "matched_competitions": (
                                matched_competitions
                            ),
                        }
                    )

            # ------------------------------------------------
            # عرض المباريات المهمة
            # ------------------------------------------------

            print()
            print("=" * 70)
            print("IMPORTANT MATCH CANDIDATES")
            print("=" * 70)

            print(
                "IMPORTANT MATCHES FOUND:",
                len(important_matches)
            )

            for match in important_matches:

                print()
                print("-" * 70)

                print(
                    f"#{match['index']}"
                )

                print(
                    "MATCH:",
                    match["home"],
                    "vs",
                    match["away"]
                )

                print(
                    "SCORE:",
                    match["home_score"],
                    "-",
                    match["away_score"]
                )

                print(
                    "STATUS:",
                    match["status"],
                    "|",
                    match["status_text"]
                )

                print(
                    "TIME:",
                    match["time"]
                )

                print(
                    "COMPETITION:",
                    match["competition"]
                )

                print(
                    "URL:",
                    match["url"]
                )

                if match["matched_teams"]:

                    print(
                        "MATCHED TEAMS:",
                        ", ".join(
                            match["matched_teams"]
                        )
                    )

                if match[
                    "matched_competitions"
                ]:

                    print(
                        "MATCHED COMPETITIONS:",
                        ", ".join(
                            match[
                                "matched_competitions"
                            ]
                        )
                    )

            # ------------------------------------------------
            # إحصائية الاستبعاد
            # ------------------------------------------------

            print()
            print("=" * 70)
            print("FILTER STATISTICS")
            print("=" * 70)

            print(
                "TOTAL MATCHES:",
                len(matches)
            )

            print(
                "IMPORTANT MATCHES:",
                len(important_matches)
            )

            print(
                "EXCLUDED MATCHES:",
                len(excluded_matches)
            )

            # ------------------------------------------------
            # عرض المباريات المستبعدة
            # ------------------------------------------------

            print()
            print("=" * 70)
            print("EXCLUDED MATCH SAMPLE")
            print("=" * 70)

            sample_count = min(
                15,
                len(excluded_matches)
            )

            for item in excluded_matches[
                :sample_count
            ]:

                print(
                    f"#{item['index']} "
                    f"{item['home']} "
                    f"vs "
                    f"{item['away']}"
                )

                print(
                    "  COMPETITION:",
                    item["competition"]
                )

                print(
                    "  REASON:",
                    item["reason"]
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

        print(
            response.text[:2000]
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
            response.text[:2000]
        )

        raise

else:

    print()
    print("=" * 70)
    print("ALL RETRIES FAILED")
    print("=" * 70)

    raise SystemExit(1)

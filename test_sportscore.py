import json
import requests
from datetime import datetime, timezone
from collections import Counter


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
# أدوات تحليل الأحداث
# ============================================================

def normalize_event_type(event):

    if not isinstance(event, dict):
        return "UNKNOWN"

    event_type = event.get("type")

    if event_type is None:
        return "UNKNOWN"

    return str(event_type).strip() or "UNKNOWN"


def print_event_sample(event_type, event):

    print("\n" + "-" * 70)
    print(f"EVENT TYPE: {event_type}")
    print("-" * 70)

    if not isinstance(event, dict):

        print(event)

        return

    print("Fields:")

    for key in event.keys():
        print(f"  - {key}")

    print("\nSample:")

    try:

        print(
            json.dumps(
                event,
                ensure_ascii=False,
                indent=2,
            )
        )

    except Exception as exc:

        print(f"Could not format event: {exc}")


# ============================================================
# تحليل incidents
# ============================================================

def analyze_incidents(match):

    print("\n\n")
    print("#" * 70)
    print("INCIDENTS ANALYSIS")
    print("#" * 70)

    if not isinstance(match, dict):

        print("Match data is not a dictionary.")

        return

    incidents = match.get("incidents")

    if incidents is None:

        print("No 'incidents' field found.")

        print("\nAvailable match fields:")

        for key in match.keys():
            print(f"  - {key}")

        return

    if not isinstance(incidents, list):

        print(
            "The 'incidents' field exists but is not a list."
        )

        print(
            f"Type: {type(incidents).__name__}"
        )

        return

    # --------------------------------------------------------
    # العدد الإجمالي
    # --------------------------------------------------------

    print(
        f"\nTotal incidents: {len(incidents)}"
    )

    if not incidents:

        print("No incidents found.")

        return

    # --------------------------------------------------------
    # عد الأحداث حسب النوع
    # --------------------------------------------------------

    event_counter = Counter()

    for incident in incidents:

        event_type = normalize_event_type(
            incident
        )

        event_counter[event_type] += 1

    print("\nEVENT TYPES:")
    print("-" * 70)

    for event_type, count in event_counter.most_common():

        print(
            f"- {event_type}: {count}"
        )

    # --------------------------------------------------------
    # جميع الحقول الموجودة في incidents
    # --------------------------------------------------------

    all_fields = set()

    for incident in incidents:

        if isinstance(incident, dict):

            all_fields.update(
                incident.keys()
            )

    print("\nINCIDENT FIELDS:")
    print("-" * 70)

    for field in sorted(all_fields):

        print(f"- {field}")

    # --------------------------------------------------------
    # أول عينة من كل نوع
    # --------------------------------------------------------

    print("\n\n")
    print("#" * 70)
    print("ONE SAMPLE FROM EACH EVENT TYPE")
    print("#" * 70)

    samples = {}

    for incident in incidents:

        event_type = normalize_event_type(
            incident
        )

        if event_type not in samples:

            samples[event_type] = incident

    for event_type in sorted(samples):

        print_event_sample(
            event_type,
            samples[event_type],
        )

    # --------------------------------------------------------
    # الأحداث المرتبطة بالأهداف
    # --------------------------------------------------------

    goals = []

    for incident in incidents:

        if not isinstance(incident, dict):
            continue

        if incident.get("is_goal") is True:

            goals.append(incident)

        elif str(
            incident.get("type", "")
        ).lower() == "goal":

            goals.append(incident)

    print("\n\n")
    print("#" * 70)
    print("GOALS SUMMARY")
    print("#" * 70)

    print(
        f"Detected goals: {len(goals)}"
    )

    for goal in goals:

        if not isinstance(goal, dict):
            continue

        print(
            f"- Minute: {goal.get('time')}"
        )

        print(
            f"  Player: {goal.get('player')}"
        )

        print(
            f"  Side: {goal.get('side')}"
        )

        print(
            f"  Score: "
            f"{goal.get('home_score')} - "
            f"{goal.get('away_score')}"
        )

    # --------------------------------------------------------
    # الملخص النهائي
    # --------------------------------------------------------

    print("\n\n")
    print("#" * 70)
    print("INCIDENTS TEST SUMMARY")
    print("#" * 70)

    print(
        f"Total incidents : {len(incidents)}"
    )

    print(
        f"Event types     : {len(event_counter)}"
    )

    print(
        f"Goals detected  : {len(goals)}"
    )

    print(
        "Status          : INCIDENT DATA AVAILABLE"
    )


# ============================================================
# TEST 6
# تفاصيل مباراة + الأحداث
# ============================================================

def test_match_detail():

    print("\n\n")
    print("#" * 70)
    print("TEST 6 — MATCH DETAIL + TIMELINE / EVENTS")
    print("#" * 70)

    # هذه المباراة ظهرت فعليًا في TEST 1
    match_slug = "platense-vs-cd-olimpia"

    print(
        f"\nMATCH SLUG: {match_slug}"
    )

    data = request_api(
        "match",
        {
            "sport": "football",
            "slug": match_slug,
            "src": "nabd-madrid",
        },
    )

    # --------------------------------------------------------
    # التحقق من الاستجابة الأساسية
    # --------------------------------------------------------

    if data is None:

        print(
            "\nTEST 6 FAILED — No response."
        )

        return None

    print("\n")
    print("-" * 70)
    print("MATCH RESPONSE")
    print("-" * 70)

    print(
        f"Top-level type: "
        f"{type(data).__name__}"
    )

    if isinstance(data, dict):

        print("Top-level keys:")

        for key in data.keys():

            print(f"  - {key}")

    # --------------------------------------------------------
    # استخراج match
    # --------------------------------------------------------

    match = data.get("match")

    if not isinstance(match, dict):

        print(
            "\nTEST 6 FAILED — "
            "'match' object not found."
        )

        return data

    # --------------------------------------------------------
    # معلومات المباراة الأساسية
    # --------------------------------------------------------

    print("\n")
    print("#" * 70)
    print("MATCH BASIC INFORMATION")
    print("#" * 70)

    print(
        f"Home       : {match.get('home')}"
    )

    print(
        f"Away       : {match.get('away')}"
    )

    print(
        f"Score      : "
        f"{match.get('home_score')} - "
        f"{match.get('away_score')}"
    )

    print(
        f"Status     : {match.get('status')}"
    )

    print(
        f"Status text: {match.get('status_text')}"
    )

    print(
        f"Time       : {match.get('time')}"
    )

    print(
        f"Live minute: {match.get('live_minute')}"
    )

    print(
        f"Competition: {match.get('competition')}"
    )

    # --------------------------------------------------------
    # الحقول الموجودة في match
    # --------------------------------------------------------

    print("\n")
    print("#" * 70)
    print("MATCH FIELDS")
    print("#" * 70)

    for key in match.keys():

        print(f"- {key}")

    # --------------------------------------------------------
    # تحليل الأحداث
    # --------------------------------------------------------

    analyze_incidents(match)

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

    print(
        "\nNo API key is required for this test."
    )

    # ========================================================
    # الاختبارات الحالية
    # ========================================================

    test_live_matches()

    test_real_madrid()

    test_barcelona()

    test_ucl()

    test_la_liga()

    # ========================================================
    # الاختبار الجديد
    # ========================================================

    test_match_detail()

    # ========================================================
    # النهاية
    # ========================================================

    print("\n\n")
    print("=" * 70)
    print("SPORTSCORE TEST FINISHED")
    print("=" * 70)


# ============================================================
# تشغيل البرنامج
# ============================================================

if __name__ == "__main__":
    main()

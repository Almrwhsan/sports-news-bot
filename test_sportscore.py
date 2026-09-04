import json
import requests
import re
import time
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
# أدوات TEST 7
# ============================================================

def normalize_name(value):

    if value is None:
        return ""

    value = str(value).lower().strip()

    value = re.sub(
        r"[^a-z0-9\u00C0-\u024F\u0600-\u06FF]+",
        "",
        value,
    )

    return value


def is_real_madrid_betis_match(match):

    if not isinstance(match, dict):
        return False

    home = normalize_name(
        match.get("home")
    )

    away = normalize_name(
        match.get("away")
    )

    teams = f"{home} {away}"

    madrid_found = (
        "realmadrid" in teams
        or "realmadrid" in home
        or "realmadrid" in away
    )

    betis_found = (
        "realbetis" in teams
        or "betisseville" in teams
        or "realbetisseville" in teams
        or "betis" in home
        or "betis" in away
    )

    return madrid_found and betis_found


def extract_match_candidates(data):

    """
    يحاول استخراج عناصر المباريات من أكثر من شكل
    محتمل للاستجابة دون افتراض بنية واحدة.
    """

    candidates = []

    def walk(value):

        if isinstance(value, dict):

            # إذا كان الكائن يبدو كمباراة
            if (
                "home" in value
                and "away" in value
            ):

                candidates.append(value)

            for child in value.values():

                walk(child)

        elif isinstance(value, list):

            for child in value:

                walk(child)

    walk(data)

    return candidates


def extract_slug_from_match(match):

    if not isinstance(match, dict):
        return None

    # --------------------------------------------------------
    # الأفضل: استخراج slug من url
    # --------------------------------------------------------

    url = match.get("url")

    if url:

        url = str(url).strip()

        parts = [
            part
            for part in url.rstrip("/").split("/")
            if part
        ]

        if parts:

            return parts[-1]

    # --------------------------------------------------------
    # إذا كان API يعيد slug مباشرة
    # --------------------------------------------------------

    slug = match.get("slug")

    if slug:

        return str(slug).strip()

    return None


def extract_match_object(data):

    if not isinstance(data, dict):
        return None

    match = data.get("match")

    if isinstance(match, dict):
        return match

    # إذا كانت الاستجابة نفسها تمثل المباراة
    if (
        "home" in data
        and "away" in data
    ):

        return data

    return None


def summarize_live_match(match):

    if not isinstance(match, dict):

        return {
            "status": None,
            "status_text": None,
            "minute": None,
            "home_score": None,
            "away_score": None,
            "incidents": [],
        }

    incidents = match.get(
        "incidents",
        []
    )

    if not isinstance(incidents, list):

        incidents = []

    return {
        "status": match.get("status"),
        "status_text": match.get("status_text"),
        "minute": match.get("live_minute"),
        "home_score": match.get("home_score"),
        "away_score": match.get("away_score"),
        "incidents": incidents,
    }


def incident_signature(incident):

    if not isinstance(incident, dict):

        return str(incident)

    return (
        str(incident.get("type", "")),
        str(incident.get("type_id", "")),
        str(incident.get("time", "")),
        str(incident.get("side", "")),
        str(incident.get("player", "")),
        str(incident.get("player_in", "")),
        str(incident.get("player_out", "")),
        str(incident.get("home_score", "")),
        str(incident.get("away_score", "")),
    )


def compare_live_snapshots(first, second):

    print("\n")
    print("-" * 70)
    print("LIVE SNAPSHOT COMPARISON")
    print("-" * 70)

    print(
        f"First score : "
        f"{first.get('home_score')} - "
        f"{first.get('away_score')}"
    )

    print(
        f"Second score: "
        f"{second.get('home_score')} - "
        f"{second.get('away_score')}"
    )

    print(
        f"First minute : {first.get('minute')}"
    )

    print(
        f"Second minute: {second.get('minute')}"
    )

    first_incidents = {
        incident_signature(item)
        for item in first.get("incidents", [])
    }

    second_incidents = {
        incident_signature(item)
        for item in second.get("incidents", [])
    }

    new_incidents = (
        second_incidents
        - first_incidents
    )

    print(
        f"First incidents : "
        f"{len(first_incidents)}"
    )

    print(
        f"Second incidents: "
        f"{len(second_incidents)}"
    )

    print(
        f"New incidents   : "
        f"{len(new_incidents)}"
    )

    if (
        first.get("home_score")
        != second.get("home_score")
        or
        first.get("away_score")
        != second.get("away_score")
    ):

        print(
            "CHANGE DETECTED: SCORE CHANGED"
        )

    elif (
        first.get("minute")
        != second.get("minute")
    ):

        print(
            "CHANGE DETECTED: LIVE MINUTE CHANGED"
        )

    elif new_incidents:

        print(
            "CHANGE DETECTED: NEW INCIDENTS"
        )

    else:

        print(
            "NO DATA CHANGE DETECTED"
        )

        print(
            "This does NOT necessarily mean "
            "the source is not live."
        )

        print(
            "SportScore responses may be cached."
        )


# ============================================================
# TEST 7
# مباراة ريال بيتيس × ريال مدريد
# ============================================================

def test_real_madrid_betis_live():

    print("\n\n")
    print("#" * 70)
    print(
        "TEST 7 — REAL BETIS vs REAL MADRID "
        "LIVE MONITOR"
    )
    print("#" * 70)

    print(
        "\nTarget:"
    )

    print(
        "Real Betis Seville vs Real Madrid"
    )

    print(
        "Date: 2026-09-04"
    )

    # --------------------------------------------------------
    # الخطوة 1
    # استخدام endpoint الخاص بريال مدريد
    # --------------------------------------------------------

    data = request_api(
        "team",
        {
            "sport": "football",
            "slug": "real-madrid",
            "limit": 20,
            "src": "nabd-madrid",
        },
    )

    if data is None:

        print(
            "\nTEST 7 FAILED — "
            "Could not retrieve Real Madrid team data."
        )

        return False

    # --------------------------------------------------------
    # البحث عن المباريات داخل استجابة الفريق
    # --------------------------------------------------------

    candidates = extract_match_candidates(
        data
    )

    print(
        f"\nMatch objects detected: "
        f"{len(candidates)}"
    )

    target_match = None

    for candidate in candidates:

        if is_real_madrid_betis_match(
            candidate
        ):

            target_match = candidate

            break

    # --------------------------------------------------------
    # لم يتم العثور على المباراة
    # --------------------------------------------------------

    if target_match is None:

        print("\n")
        print("-" * 70)
        print(
            "TARGET MATCH NOT FOUND "
            "IN REAL MADRID TEAM DATA"
        )
        print("-" * 70)

        print(
            "\nThis is not treated as an API failure."
        )

        print(
            "The team endpoint responded successfully, "
            "but the target fixture was not found "
            "in the returned data."
        )

        print(
            "\nTEST 7 STATUS: NOT AVAILABLE YET"
        )

        return True

    # --------------------------------------------------------
    # معلومات المباراة المكتشفة
    # --------------------------------------------------------

    print("\n")
    print("#" * 70)
    print("TARGET MATCH FOUND")
    print("#" * 70)

    print(
        f"Home       : "
        f"{target_match.get('home')}"
    )

    print(
        f"Away       : "
        f"{target_match.get('away')}"
    )

    print(
        f"Score      : "
        f"{target_match.get('home_score')} - "
        f"{target_match.get('away_score')}"
    )

    print(
        f"Status     : "
        f"{target_match.get('status')}"
    )

    print(
        f"Status text: "
        f"{target_match.get('status_text')}"
    )

    print(
        f"Time       : "
        f"{target_match.get('time')}"
    )

    print(
        f"Live minute: "
        f"{target_match.get('live_minute')}"
    )

    print(
        f"URL        : "
        f"{target_match.get('url')}"
    )

    # --------------------------------------------------------
    # استخراج slug
    # --------------------------------------------------------

    match_slug = extract_slug_from_match(
        target_match
    )

    print(
        f"\nMATCH SLUG: {match_slug}"
    )

    if not match_slug:

        print(
            "\nTEST 7 FAILED — "
            "Could not extract match slug."
        )

        return False

    # --------------------------------------------------------
    # الخطوة 2
    # جلب تفاصيل المباراة
    # --------------------------------------------------------

    detail_data = request_api(
        "match",
        {
            "sport": "football",
            "slug": match_slug,
            "src": "nabd-madrid",
        },
    )

    if detail_data is None:

        print(
            "\nTEST 7 FAILED — "
            "Could not retrieve match details."
        )

        return False

    match = extract_match_object(
        detail_data
    )

    if match is None:

        print(
            "\nTEST 7 FAILED — "
            "Match object not found."
        )

        return False

    # --------------------------------------------------------
    # المعلومات الحالية
    # --------------------------------------------------------

    print("\n")
    print("#" * 70)
    print("CURRENT MATCH STATUS")
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

    incidents = match.get(
        "incidents",
        []
    )

    if isinstance(incidents, list):

        print(
            f"Incidents  : {len(incidents)}"
        )

    else:

        print(
            "Incidents  : unavailable"
        )

    # --------------------------------------------------------
    # تحديد حالة المباراة
    # --------------------------------------------------------

    status = str(
        match.get(
            "status",
            ""
        )
    ).lower().strip()

    status_text = str(
        match.get(
            "status_text",
            ""
        )
    ).lower().strip()

    combined_status = (
        f"{status} {status_text}"
    )

    live_keywords = (
        "live",
        "inprogress",
        "in progress",
        "playing",
        "started",
    )

    finished_keywords = (
        "finished",
        "ended",
        "complete",
        "completed",
        "cancelled",
        "postponed",
    )

    is_live = any(
        keyword in combined_status
        for keyword in live_keywords
    )

    is_finished = any(
        keyword in combined_status
        for keyword in finished_keywords
    )

    # --------------------------------------------------------
    # المباراة لم تبدأ
    # --------------------------------------------------------

    if not is_live and not is_finished:

        print("\n")
        print("-" * 70)
        print(
            "MATCH HAS NOT STARTED YET"
        )
        print("-" * 70)

        print(
            "This is expected before kickoff."
        )

        print(
            "\nTEST 7 STATUS: READY"
        )

        print(
            "SportScore can locate the target "
            "match and retrieve its details."
        )

        return True

    # --------------------------------------------------------
    # المباراة انتهت
    # --------------------------------------------------------

    if is_finished:

        print("\n")
        print("-" * 70)
        print(
            "MATCH IS FINISHED"
        )
        print("-" * 70)

        print(
            "Final score:"
        )

        print(
            f"{match.get('home')} "
            f"{match.get('home_score')} - "
            f"{match.get('away_score')} "
            f"{match.get('away')}"
        )

        print(
            "\nTEST 7 STATUS: MATCH DATA AVAILABLE"
        )

        analyze_incidents(
            match
        )

        return True

    # --------------------------------------------------------
    # المباراة حية
    # --------------------------------------------------------

    print("\n")
    print("#" * 70)
    print(
        "LIVE MATCH DETECTED"
    )
    print("#" * 70)

    print(
        f"Live minute: "
        f"{match.get('live_minute')}"
    )

    print(
        f"Score: "
        f"{match.get('home_score')} - "
        f"{match.get('away_score')}"
    )

    print(
        f"Incidents: "
        f"{len(incidents) if isinstance(incidents, list) else 0}"
    )

    # --------------------------------------------------------
    # تحليل الأحداث الحالية
    # --------------------------------------------------------

    analyze_incidents(
        match
    )

    # --------------------------------------------------------
    # Snapshot 1
    # --------------------------------------------------------

    first_snapshot = summarize_live_match(
        match
    )

    # --------------------------------------------------------
    # الانتظار أكثر من مدة الكاش
    # --------------------------------------------------------

    wait_seconds = 65

    print("\n")
    print("#" * 70)
    print(
        f"WAITING {wait_seconds} SECONDS "
        "BEFORE SECOND LIVE CHECK"
    )
    print("#" * 70)

    print(
        "\nReason:"
    )

    print(
        "SportScore responses may be cached "
        "for approximately 60 seconds."
    )

    print(
        "Waiting longer gives the second request "
        "a better chance of receiving refreshed data."
    )

    for remaining in range(
        wait_seconds,
        0,
        -5
    ):

        print(
            f"Remaining: {remaining}s"
        )

        time.sleep(
            min(
                5,
                remaining
            )
        )

    # --------------------------------------------------------
    # Snapshot 2
    # --------------------------------------------------------

    print("\n")
    print("#" * 70)
    print(
        "SECOND LIVE CHECK"
    )
    print("#" * 70)

    second_data = request_api(
        "match",
        {
            "sport": "football",
            "slug": match_slug,
            "src": "nabd-madrid",
        },
    )

    if second_data is None:

        print(
            "\nTEST 7 FAILED — "
            "Second live request failed."
        )

        return False

    second_match = extract_match_object(
        second_data
    )

    if second_match is None:

        print(
            "\nTEST 7 FAILED — "
            "Second match object not found."
        )

        return False

    second_snapshot = summarize_live_match(
        second_match
    )

    # --------------------------------------------------------
    # المقارنة
    # --------------------------------------------------------

    compare_live_snapshots(
        first_snapshot,
        second_snapshot
    )

    # --------------------------------------------------------
    # نتيجة الاختبار
    # --------------------------------------------------------

    print("\n")
    print("#" * 70)
    print("TEST 7 FINAL STATUS")
    print("#" * 70)

    print(
        "STATUS: SPORTScore LIVE DATA AVAILABLE"
    )

    print(
        "The target match can be located and "
        "its live match details can be retrieved."
    )

    return True


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
    # TEST 6
    # ========================================================

    test_match_detail()

    # ========================================================
    # TEST 7
    # ========================================================

    test_real_madrid_betis_live()

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

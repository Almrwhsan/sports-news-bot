import json
import requests
import re
import time
from datetime import datetime, timezone
from collections import Counter


# ============================================================
# SportScore API
# ============================================================

BASE_URL = "https://sportscore.com/api/widget"


# ============================================================
# Helpers
# ============================================================

def request_api(endpoint, params=None):
    """
    إرسال طلب إلى SportScore API
    """
    url = f"{BASE_URL}/{endpoint}/"

    try:
        print()
        print("REQUEST:", url)
        print("PARAMS :", params)

        response = requests.get(
            url,
            params=params or {},
            timeout=30,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/140 Safari/537.36"
                ),
                "Accept": "application/json",
            },
        )

        print("HTTP   :", response.status_code)

        response.raise_for_status()

        data = response.json()

        print("JSON   : OK")

        return data

    except requests.RequestException as exc:
        print("REQUEST ERROR:", exc)
        return None

    except ValueError as exc:
        print("JSON ERROR:", exc)
        return None


def print_structure(obj, path="root", depth=0, max_depth=5):
    """
    طباعة بنية JSON بشكل مختصر.
    """

    if depth > max_depth:
        return

    indent = "  " * depth

    if isinstance(obj, dict):

        print(
            f"{indent}{path}: DICT "
            f"({len(obj)} keys)"
        )

        for key, value in obj.items():

            if isinstance(value, dict):

                print_structure(
                    value,
                    f"{path}.{key}",
                    depth + 1,
                    max_depth,
                )

            elif isinstance(value, list):

                print(
                    f"{indent}  {key}: "
                    f"LIST ({len(value)} items)"
                )

                if value:
                    print_structure(
                        value[0],
                        f"{path}.{key}[0]",
                        depth + 2,
                        max_depth,
                    )

            else:

                print(
                    f"{indent}  {key}: "
                    f"{repr(value)}"
                )

    elif isinstance(obj, list):

        print(
            f"{indent}{path}: LIST "
            f"({len(obj)} items)"
        )

        if obj:

            print_structure(
                obj[0],
                f"{path}[0]",
                depth + 1,
                max_depth,
            )

    else:

        print(
            f"{indent}{path}: "
            f"{repr(obj)}"
        )


# ============================================================
# TEST 1
# Matches
# ============================================================

print()
print("=" * 70)
print("TEST 1 — MATCHES")
print("=" * 70)

matches_data = request_api(
    "matches",
    {
        "sport": "football",
        "limit": 10,
        "src": "nabd-madrid",
    },
)

if matches_data is not None:

    print()
    print("MATCHES STRUCTURE")
    print("-" * 70)

    print_structure(
        matches_data,
        max_depth=4,
    )


# ============================================================
# TEST 2
# Real Madrid
# ============================================================

print()
print("=" * 70)
print("TEST 2 — REAL MADRID")
print("=" * 70)

real_madrid_data = request_api(
    "team",
    {
        "sport": "football",
        "slug": "real-madrid",
        "limit": 20,
        "src": "nabd-madrid",
    },
)

if real_madrid_data is not None:

    print()
    print("REAL MADRID STRUCTURE")
    print("-" * 70)

    print_structure(
        real_madrid_data,
        max_depth=4,
    )


# ============================================================
# TEST 3
# Barcelona
# ============================================================

print()
print("=" * 70)
print("TEST 3 — BARCELONA")
print("=" * 70)

barcelona_data = request_api(
    "team",
    {
        "sport": "football",
        "slug": "barcelona",
        "limit": 20,
        "src": "nabd-madrid",
    },
)

if barcelona_data is not None:

    print()
    print("BARCELONA STRUCTURE")
    print("-" * 70)

    print_structure(
        barcelona_data,
        max_depth=4,
    )


# ============================================================
# TEST 4
# UEFA Champions League
# ============================================================

print()
print("=" * 70)
print("TEST 4 — UEFA CHAMPIONS LEAGUE BRACKET")
print("=" * 70)

ucl_data = request_api(
    "bracket",
    {
        "sport": "football",
        "slug": "uefa-champions-league",
        "src": "nabd-madrid",
    },
)

if ucl_data is not None:

    print()
    print("UCL STRUCTURE")
    print("-" * 70)

    print_structure(
        ucl_data,
        max_depth=5,
    )


# ============================================================
# TEST 5
# La Liga standings
# ============================================================

print()
print("=" * 70)
print("TEST 5 — LA LIGA STANDINGS")
print("=" * 70)

laliga_data = request_api(
    "standings",
    {
        "sport": "football",
        "slug": "laliga",
        "src": "nabd-madrid",
    },
)

if laliga_data is not None:

    print()
    print("LA LIGA STRUCTURE")
    print("-" * 70)

    print_structure(
        laliga_data,
        max_depth=5,
    )


# ============================================================
# TEST 6
# Match detail test
# ============================================================

print()
print("=" * 70)
print("TEST 6 — MATCH DETAIL")
print("=" * 70)

detail_data = request_api(
    "match",
    {
        "sport": "football",
        "slug": "platense-vs-cd-olimpia",
        "src": "nabd-madrid",
    },
)

if detail_data is not None:

    print()
    print("MATCH DETAIL STRUCTURE")
    print("-" * 70)

    print_structure(
        detail_data,
        max_depth=6,
    )


# ============================================================
# TEST 7 HELPERS
# ============================================================

TARGET_DATE = "2026-09-04"
TARGET_HOME = "Real Betis"
TARGET_AWAY = "Real Madrid"


def normalize_name(value):
    """
    توحيد أسماء الفرق للمقارنة.
    """

    if value is None:
        return ""

    value = str(value).strip().lower()

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    replacements = {
        "real betis seville": "real betis",
        "real betis sevilla": "real betis",
        "real betis": "real betis",
        "real madrid": "real madrid",
    }

    return replacements.get(
        value,
        value,
    )


def get_team_name(match, side):
    """
    محاولة استخراج اسم الفريق من عدة صيغ محتملة.
    """

    if not isinstance(match, dict):
        return ""

    if side == "home":

        keys = [
            "home",
            "home_team",
            "homeTeam",
            "home_name",
            "homeName",
            "homeTeamName",
        ]

    else:

        keys = [
            "away",
            "away_team",
            "awayTeam",
            "away_name",
            "awayName",
            "awayTeamName",
        ]

    for key in keys:

        value = match.get(key)

        if isinstance(value, str) and value.strip():
            return value.strip()

        if isinstance(value, dict):

            for nested_key in [
                "name",
                "title",
                "team_name",
                "shortName",
            ]:

                nested_value = value.get(
                    nested_key
                )

                if (
                    isinstance(
                        nested_value,
                        str,
                    )
                    and nested_value.strip()
                ):
                    return nested_value.strip()

    return ""


def get_match_time(match):
    """
    استخراج وقت المباراة.
    """

    if not isinstance(match, dict):
        return None

    keys = [
        "time",
        "start_time",
        "startTime",
        "date",
        "datetime",
        "timestamp",
    ]

    for key in keys:

        value = match.get(key)

        if value is not None:

            if isinstance(
                value,
                (str, int, float),
            ):
                return value

    return None


def is_target_match(match):
    """
    التحقق من أن الكائن يمثل مباراة بيتيس وريال مدريد.
    """

    if not isinstance(match, dict):
        return False

    home = normalize_name(
        get_team_name(
            match,
            "home",
        )
    )

    away = normalize_name(
        get_team_name(
            match,
            "away",
        )
    )

    target_home = normalize_name(
        TARGET_HOME
    )

    target_away = normalize_name(
        TARGET_AWAY
    )

    return (
        home == target_home
        and away == target_away
    ) or (
        home == target_away
        and away == target_home
    )


def extract_match_candidates(obj):
    """
    البحث recursively عن جميع كائنات المباراة.
    """

    candidates = []

    def walk(value):

        if isinstance(value, dict):

            if is_target_match(value):
                candidates.append(value)

            for child in value.values():
                walk(child)

        elif isinstance(value, list):

            for item in value:
                walk(item)

    walk(obj)

    return candidates


def extract_slug_from_match(match):
    """
    استخراج slug المباراة.
    """

    if not isinstance(match, dict):
        return None

    possible_urls = [
        match.get("url"),
        match.get("match_url"),
        match.get("matchUrl"),
        match.get("link"),
        match.get("href"),
    ]

    for url in possible_urls:

        if not url:
            continue

        url = (
            str(url)
            .strip()
            .rstrip("/")
        )

        if "/football/match/" in url:

            slug = (
                url
                .split("/football/match/")[-1]
                .split("?")[0]
                .strip("/")
            )

            if slug:
                return slug

    possible_slugs = [
        match.get("slug"),
        match.get("match_slug"),
        match.get("matchSlug"),
    ]

    for slug in possible_slugs:

        if slug:

            return (
                str(slug)
                .strip()
                .strip("/")
            )

    return None


def extract_match_object(data):
    """
    محاولة استخراج الكائن الرئيسي للمباراة.
    """

    if isinstance(data, dict):

        possible_keys = [
            "match",
            "data",
            "fixture",
            "game",
        ]

        for key in possible_keys:

            value = data.get(key)

            if isinstance(value, dict):

                if (
                    is_target_match(value)
                    or key in [
                        "match",
                        "fixture",
                        "game",
                    ]
                ):
                    return value

        if is_target_match(data):
            return data

    return None


def summarize_live_match(data):
    """
    استخراج ملخص المباراة من البيانات.
    """

    match = extract_match_object(
        data
    )

    if match is None:
        match = data

    if not isinstance(match, dict):
        return {}

    home = get_team_name(
        match,
        "home",
    )

    away = get_team_name(
        match,
        "away",
    )

    score_home = None
    score_away = None

    score_objects = [
        match.get("score"),
        match.get("scores"),
    ]

    for score in score_objects:

        if isinstance(score, dict):

            for key in [
                "home",
                "home_score",
                "homeScore",
            ]:

                if key in score:
                    score_home = score.get(key)
                    break

            for key in [
                "away",
                "away_score",
                "awayScore",
            ]:

                if key in score:
                    score_away = score.get(key)
                    break

    if score_home is None:

        for key in [
            "home_score",
            "homeScore",
            "score_home",
        ]:

            if key in match:
                score_home = match.get(key)
                break

    if score_away is None:

        for key in [
            "away_score",
            "awayScore",
            "score_away",
        ]:

            if key in match:
                score_away = match.get(key)
                break

    status = (
        match.get("status")
        or match.get("state")
        or match.get("match_status")
    )

    status_text = (
        match.get("status_text")
        or match.get("statusText")
        or match.get("state_text")
        or match.get("stateText")
    )

    minute = (
        match.get("minute")
        or match.get("match_minute")
        or match.get("matchMinute")
        or match.get("elapsed")
    )

    match_time = get_match_time(
        match
    )

    incidents = []

    for key in [
        "incidents",
        "events",
        "timeline",
        "commentary",
    ]:

        value = match.get(key)

        if isinstance(value, list):

            incidents = value
            break

    return {
        "home": home,
        "away": away,
        "score_home": score_home,
        "score_away": score_away,
        "status": status,
        "status_text": status_text,
        "time": match_time,
        "minute": minute,
        "incidents": incidents,
    }


def find_event_containers(obj):
    """
    البحث عن جميع القوائم التي قد تحتوي
    على أحداث المباراة.
    """

    found = []

    def walk(value, path="root"):

        if isinstance(value, dict):

            for key, child in value.items():

                key_lower = str(
                    key
                ).lower()

                if any(
                    word in key_lower
                    for word in [
                        "events",
                        "event",
                        "incidents",
                        "incident",
                        "timeline",
                        "commentary",
                    ]
                ):

                    if isinstance(
                        child,
                        list,
                    ):

                        found.append(
                            {
                                "path": (
                                    f"{path}.{key}"
                                ),
                                "key": key,
                                "items": child,
                            }
                        )

                if isinstance(
                    child,
                    (dict, list),
                ):

                    walk(
                        child,
                        f"{path}.{key}",
                    )

        elif isinstance(value, list):

            for index, item in enumerate(
                value
            ):

                if isinstance(
                    item,
                    (dict, list),
                ):

                    walk(
                        item,
                        f"{path}[{index}]",
                    )

    walk(obj)

    return found


def print_event_structure(
    obj,
    path="root",
    depth=0,
    max_depth=8,
):
    """
    طباعة بنية البيانات المتعلقة بالأحداث.
    """

    if depth > max_depth:
        return

    indent = "  " * depth

    if isinstance(obj, dict):

        print(
            f"{indent}{path} -> "
            f"DICT ({len(obj)} keys)"
        )

        for key, value in obj.items():

            key_lower = str(
                key
            ).lower()

            interesting = any(
                word in key_lower
                for word in [
                    "event",
                    "incident",
                    "timeline",
                    "goal",
                    "card",
                    "yellow",
                    "red",
                    "substitution",
                    "score",
                    "status",
                    "minute",
                    "time",
                    "player",
                    "team",
                    "assist",
                ]
            )

            if interesting:

                if isinstance(
                    value,
                    (dict, list),
                ):

                    print(
                        f"{indent}  KEY: "
                        f"{key} -> "
                        f"{type(value).__name__}"
                    )

                else:

                    print(
                        f"{indent}  KEY: "
                        f"{key} -> "
                        f"{repr(value)}"
                    )

            if isinstance(
                value,
                (dict, list),
            ):

                print_event_structure(
                    value,
                    f"{path}.{key}",
                    depth + 1,
                    max_depth,
                )

    elif isinstance(obj, list):

        print(
            f"{indent}{path} -> "
            f"LIST ({len(obj)} items)"
        )

        for index, item in enumerate(
            obj[:10]
        ):

            if isinstance(
                item,
                (dict, list),
            ):

                print_event_structure(
                    item,
                    f"{path}[{index}]",
                    depth + 1,
                    max_depth,
                )

            else:

                print(
                    f"{indent}  "
                    f"[{index}] "
                    f"{repr(item)}"
                )


def incident_signature(event):
    """
    إنشاء توقيع ثابت للحدث.
    هذا سيكون مهمًا لاحقًا لمنع التكرار.
    """

    if not isinstance(event, dict):
        return str(event)

    important_keys = [
        "id",
        "event_id",
        "eventId",
        "incident_id",
        "incidentId",
        "type",
        "event_type",
        "eventType",
        "incident_type",
        "incidentType",
        "minute",
        "time",
        "player",
        "player_id",
        "playerId",
        "team",
        "team_id",
        "teamId",
    ]

    parts = []

    for key in important_keys:

        if key in event:

            value = event.get(key)

            if isinstance(
                value,
                (dict, list),
            ):

                value = json.dumps(
                    value,
                    ensure_ascii=False,
                    sort_keys=True,
                )

            parts.append(
                f"{key}={value}"
            )

    if parts:
        return "|".join(parts)

    return json.dumps(
        event,
        ensure_ascii=False,
        sort_keys=True,
    )


def compare_live_snapshots(
    first,
    second,
):
    """
    مقارنة لقطتين من المباراة.
    """

    first_summary = summarize_live_match(
        first
    )

    second_summary = summarize_live_match(
        second
    )

    first_incidents = (
        first_summary.get(
            "incidents",
            [],
        )
    )

    second_incidents = (
        second_summary.get(
            "incidents",
            [],
        )
    )

    first_signatures = {
        incident_signature(event)
        for event in first_incidents
    }

    second_signatures = {
        incident_signature(event)
        for event in second_incidents
    }

    new_events = (
        second_signatures
        - first_signatures
    )

    return {
        "score_changed": (
            first_summary.get(
                "score_home"
            )
            != second_summary.get(
                "score_home"
            )
            or
            first_summary.get(
                "score_away"
            )
            != second_summary.get(
                "score_away"
            )
        ),
        "minute_changed": (
            first_summary.get(
                "minute"
            )
            != second_summary.get(
                "minute"
            )
        ),
        "status_changed": (
            first_summary.get(
                "status"
            )
            != second_summary.get(
                "status"
            )
        ),
        "new_events": new_events,
    }


# ============================================================
# TEST 7
# Real Betis vs Real Madrid
# FULL LIVE MATCH / EVENTS INSPECTION
# ============================================================

print()
print("=" * 70)
print("TEST 7 — REAL BETIS vs REAL MADRID")
print("FULL LIVE MATCH / EVENTS INSPECTION")
print("=" * 70)

print()
print("TARGET:")
print(f"Home : {TARGET_HOME}")
print(f"Away : {TARGET_AWAY}")
print(f"Date : {TARGET_DATE}")


# ============================================================
# STEP 1
# Find target match
# ============================================================

print()
print("-" * 70)
print("STEP 1 — FIND TARGET MATCH")
print("-" * 70)

data = request_api(
    "team",
    {
        "sport": "football",
        "slug": "real-madrid",
        "limit": 30,
        "src": "nabd-madrid",
    },
)

if data is None:

    print()
    print(
        "ERROR: Could not retrieve "
        "Real Madrid team data."
    )

else:

    candidates = extract_match_candidates(
        data
    )

    print()
    print(
        "Target match candidates found:",
        len(candidates),
    )

    if not candidates:

        print()
        print(
            "TARGET MATCH NOT FOUND"
        )

    else:

        # ----------------------------------------------------
        # Display candidates
        # ----------------------------------------------------

        for index, candidate in enumerate(
            candidates,
            start=1,
        ):

            print()
            print(
                f"CANDIDATE #{index}"
            )

            print(
                "Home:",
                get_team_name(
                    candidate,
                    "home",
                ),
            )

            print(
                "Away:",
                get_team_name(
                    candidate,
                    "away",
                ),
            )

            print(
                "Time:",
                get_match_time(
                    candidate
                ),
            )

            print(
                "Status:",
                candidate.get(
                    "status"
                ),
            )

            print(
                "URL:",
                candidate.get(
                    "url"
                ),
            )

        # ----------------------------------------------------
        # Prefer exact target date
        # ----------------------------------------------------

        selected_candidate = None

        for candidate in candidates:

            candidate_time = get_match_time(
                candidate
            )

            if candidate_time:

                candidate_time_text = str(
                    candidate_time
                )

                if TARGET_DATE in candidate_time_text:

                    selected_candidate = candidate
                    break

        # ----------------------------------------------------
        # Fallback
        # ----------------------------------------------------

        if selected_candidate is None:

            selected_candidate = candidates[0]

            print()
            print(
                "WARNING:"
            )
            print(
                "No candidate contained "
                "the exact target date."
            )

            print(
                "Using first matching candidate "
                "to obtain slug."
            )

        else:

            print()
            print(
                "Exact target-date candidate selected."
            )

        # ----------------------------------------------------
        # Extract slug
        # ----------------------------------------------------

        slug = extract_slug_from_match(
            selected_candidate
        )

        print()
        print(
            "MATCH SLUG:"
        )
        print(slug)

        if not slug:

            print()
            print(
                "ERROR: Could not extract "
                "match slug."
            )

        else:

            # =================================================
            # STEP 2
            # Full match detail
            # =================================================

            print()
            print("-" * 70)
            print(
                "STEP 2 — GET FULL MATCH DETAIL"
            )
            print("-" * 70)

            match_data = request_api(
                "match",
                {
                    "sport": "football",
                    "slug": slug,
                    "src": "nabd-madrid",
                },
            )

            if match_data is None:

                print()
                print(
                    "ERROR: Could not retrieve "
                    "full match data."
                )

            else:

                # =================================================
                # STEP 3
                # Match summary
                # =================================================

                print()
                print("-" * 70)
                print(
                    "STEP 3 — CURRENT MATCH SUMMARY"
                )
                print("-" * 70)

                summary = summarize_live_match(
                    match_data
                )

                print()
                print(
                    "Home       :",
                    summary.get(
                        "home"
                    ),
                )

                print(
                    "Away       :",
                    summary.get(
                        "away"
                    ),
                )

                print(
                    "Score      :",
                    summary.get(
                        "score_home"
                    ),
                    "-",
                    summary.get(
                        "score_away"
                    ),
                )

                print(
                    "Status     :",
                    summary.get(
                        "status"
                    ),
                )

                print(
                    "Status text:",
                    summary.get(
                        "status_text"
                    ),
                )

                print(
                    "Time       :",
                    summary.get(
                        "time"
                    ),
                )

                print(
                    "Live minute:",
                    summary.get(
                        "minute"
                    ),
                )

                print(
                    "Incidents  :",
                    len(
                        summary.get(
                            "incidents",
                            [],
                        )
                    ),
                )

                # =================================================
                # STEP 4
                # Status analysis
                # =================================================

                print()
                print("-" * 70)
                print(
                    "STEP 4 — STATUS ANALYSIS"
                )
                print("-" * 70)

                raw_status = str(
                    summary.get(
                        "status"
                    )
                    or ""
                ).strip().lower()

                raw_status_text = str(
                    summary.get(
                        "status_text"
                    )
                    or ""
                ).strip().lower()

                combined_status = (
                    f"{raw_status} "
                    f"{raw_status_text}"
                )

                is_not_started = (
                    "not started"
                    in combined_status
                    or
                    "upcoming"
                    in combined_status
                    or
                    "scheduled"
                    in combined_status
                )

                live_keywords = (
                    "live",
                    "inprogress",
                    "in progress",
                    "playing",
                    "ongoing",
                )

                is_live = (
                    not is_not_started
                    and any(
                        keyword
                        in combined_status
                        for keyword
                        in live_keywords
                    )
                )

                finished_keywords = (
                    "finished",
                    "full time",
                    "completed",
                    "complete",
                    "ended",
                )

                is_finished = any(
                    keyword
                    in combined_status
                    for keyword in finished_keywords
                )

                print()
                print(
                    "Normalized status:",
                    combined_status,
                )

                print(
                    "Not started:",
                    is_not_started,
                )

                print(
                    "Live:",
                    is_live,
                )

                print(
                    "Finished:",
                    is_finished,
                )

                # =================================================
                # STEP 5
                # Event containers
                # =================================================

                print()
                print("-" * 70)
                print(
                    "STEP 5 — EVENT CONTAINERS"
                )
                print("-" * 70)

                containers = find_event_containers(
                    match_data
                )

                print(
                    "Event containers found:",
                    len(containers),
                )

                for index, container in enumerate(
                    containers,
                    start=1,
                ):

                    print()
                    print(
                        f"EVENT CONTAINER #{index}"
                    )

                    print(
                        "Path:",
                        container[
                            "path"
                        ],
                    )

                    print(
                        "Key:",
                        container[
                            "key"
                        ],
                    )

                    print(
                        "Items:",
                        len(
                            container[
                                "items"
                            ]
                        ),
                    )

                    for event_index, event in enumerate(
                        container[
                            "items"
                        ][:20],
                        start=1,
                    ):

                        print()
                        print(
                            f"EVENT #{event_index}"
                        )

                        if isinstance(
                            event,
                            dict,
                        ):

                            print(
                                json.dumps(
                                    event,
                                    ensure_ascii=False,
                                    indent=2,
                                )[:5000]
                            )

                        else:

                            print(
                                repr(event)
                            )

                # =================================================
                # STEP 6
                # Event structure
                # =================================================

                print()
                print("-" * 70)
                print(
                    "STEP 6 — EVENT DATA STRUCTURE"
                )
                print("-" * 70)

                print_event_structure(
                    match_data,
                    max_depth=7,
                )

                # =================================================
                # STEP 7
                # Raw JSON
                # =================================================

                print()
                print("-" * 70)
                print(
                    "STEP 7 — RAW MATCH JSON"
                )
                print("-" * 70)

                raw_json = json.dumps(
                    match_data,
                    ensure_ascii=False,
                    indent=2,
                )

                print(
                    raw_json[:40000]
                )

                if len(raw_json) > 40000:

                    print()
                    print(
                        "... RAW JSON TRUNCATED ..."
                    )

                # =================================================
                # STEP 8
                # Initial live monitoring
                # =================================================

                print()
                print("-" * 70)
                print(
                    "STEP 8 — LIVE MONITOR PRECHECK"
                )
                print("-" * 70)

                if is_not_started:

                    print()
                    print(
                        "MATCH STATUS:"
                    )

                    print(
                        "NOT STARTED"
                    )

                    print()
                    print(
                        "The monitor is READY."
                    )

                    print(
                        "It will wait for the "
                        "match to become live."
                    )

                    print()
                    print(
                        "IMPORTANT:"
                    )

                    print(
                        "'Not started' is NOT "
                        "treated as live."
                    )

                elif is_live:

                    print()
                    print(
                        "LIVE MATCH DETECTED"
                    )

                    print(
                        "Live minute:",
                        summary.get(
                            "minute"
                        ),
                    )

                    print(
                        "Score:",
                        summary.get(
                            "score_home"
                        ),
                        "-",
                        summary.get(
                            "score_away"
                        ),
                    )

                    print(
                        "Incidents:",
                        len(
                            summary.get(
                                "incidents",
                                [],
                            )
                        ),
                    )

                    print()
                    print(
                        "The match can be "
                        "monitored immediately."
                    )

                elif is_finished:

                    print()
                    print(
                        "MATCH FINISHED"
                    )

                    print(
                        "Final score:",
                        summary.get(
                            "score_home"
                        ),
                        "-",
                        summary.get(
                            "score_away"
                        ),
                    )

                else:

                    print()
                    print(
                        "UNKNOWN MATCH STATUS"
                    )

                    print(
                        "The raw status values "
                        "were printed above."
                    )

                # =================================================
                # STEP 9
                # Optional second snapshot
                # =================================================

                if is_live:

                    print()
                    print("-" * 70)
                    print(
                        "STEP 9 — SECOND LIVE SNAPSHOT"
                    )
                    print("-" * 70)

                    print()
                    print(
                        "WAITING 65 SECONDS..."
                    )

                    time.sleep(65)

                    second_data = request_api(
                        "match",
                        {
                            "sport": "football",
                            "slug": slug,
                            "src": "nabd-madrid",
                        },
                    )

                    if second_data is not None:

                        comparison = compare_live_snapshots(
                            match_data,
                            second_data,
                        )

                        second_summary = summarize_live_match(
                            second_data
                        )

                        print()
                        print(
                            "FIRST SNAPSHOT"
                        )

                        print(
                            "Score:",
                            summary.get(
                                "score_home"
                            ),
                            "-",
                            summary.get(
                                "score_away"
                            ),
                        )

                        print(
                            "Minute:",
                            summary.get(
                                "minute"
                            ),
                        )

                        print(
                            "Incidents:",
                            len(
                                summary.get(
                                    "incidents",
                                    [],
                                )
                            ),
                        )

                        print()
                        print(
                            "SECOND SNAPSHOT"
                        )

                        print(
                            "Score:",
                            second_summary.get(
                                "score_home"
                            ),
                            "-",
                            second_summary.get(
                                "score_away"
                            ),
                        )

                        print(
                            "Minute:",
                            second_summary.get(
                                "minute"
                            ),
                        )

                        print(
                            "Incidents:",
                            len(
                                second_summary.get(
                                    "incidents",
                                    [],
                                )
                            ),
                        )

                        print()
                        print(
                            "COMPARISON"
                        )

                        print(
                            "Score changed:",
                            comparison[
                                "score_changed"
                            ],
                        )

                        print(
                            "Minute changed:",
                            comparison[
                                "minute_changed"
                            ],
                        )

                        print(
                            "Status changed:",
                            comparison[
                                "status_changed"
                            ],
                        )

                        print(
                            "New events:",
                            len(
                                comparison[
                                    "new_events"
                                ]
                            ),
                        )

                        if comparison[
                            "new_events"
                        ]:

                            print()
                            print(
                                "NEW EVENT SIGNATURES:"
                            )

                            for event in comparison[
                                "new_events"
                            ]:

                                print(
                                    event
                                )

                    else:

                        print(
                            "SECOND SNAPSHOT "
                            "COULD NOT BE RETRIEVED"
                        )

                # =================================================
                # FINAL STATUS
                # =================================================

                print()
                print("=" * 70)
                print(
                    "TEST 7 FINAL STATUS"
                )
                print("=" * 70)

                print()
                print(
                    "STATUS: FULL MATCH DATA RETRIEVED"
                )

                print(
                    "Match:",
                    summary.get(
                        "home"
                    ),
                    "vs",
                    summary.get(
                        "away"
                    ),
                )

                print(
                    "Time:",
                    summary.get(
                        "time"
                    ),
                )

                print(
                    "Status:",
                    summary.get(
                        "status"
                    ),
                )

                print(
                    "Events:",
                    len(
                        summary.get(
                            "incidents",
                            [],
                        )
                    ),
                )

                print()
                print(
                    "NEXT STEP:"
                )

                print(
                    "Build live_event_manager.py "
                    "from the actual SportScore "
                    "event structure above."
                )

                print("=" * 70)

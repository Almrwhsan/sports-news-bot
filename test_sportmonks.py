import os
import requests
from datetime import datetime, timezone


BASE_URL = "https://api.sportmonks.com/v3/football"


# ============================================================
# TOKEN
# ============================================================

def get_token():
    token = os.getenv("SPORTMONKS_TOKEN")

    if not token:
        print("ERROR: SPORTMONKS_TOKEN is not set.")
        return None

    return token


# ============================================================
# API REQUEST
# ============================================================

def api_get(endpoint, params=None):
    token = get_token()

    if not token:
        return None

    url = f"{BASE_URL}/{endpoint}"

    headers = {
        "Authorization": token,
        "Accept": "application/json",
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params or {},
            timeout=30,
        )

        print(f"\nHTTP {response.status_code}: {endpoint}")

        if response.status_code != 200:
            print(response.text[:2000])
            return None

        return response.json()

    except requests.RequestException as e:
        print(f"REQUEST ERROR: {e}")
        return None


# ============================================================
# TEST 1 — EVENT TYPES
# ============================================================

def test_event_types():
    print("\n" + "=" * 70)
    print("TEST 1 — EVENT TYPES")
    print("=" * 70)

    data = api_get("types")

    if not data:
        print("Could not retrieve event types.")
        return {}

    items = data.get("data", [])

    print(f"Event types received: {len(items)}")

    event_types = {}

    for item in items:
        type_id = item.get("id")
        name = item.get("name")
        code = item.get("code")

        event_types[type_id] = {
            "name": name,
            "code": code,
        }

        print(
            f"TYPE {type_id}: "
            f"name={name!r}, "
            f"code={code!r}"
        )

    return event_types


# ============================================================
# TEST 2 — TODAY'S FIXTURES
# ============================================================

def test_recent_fixtures():
    print("\n" + "=" * 70)
    print("TEST 2 — RECENT FIXTURES")
    print("=" * 70)

    now = datetime.now(timezone.utc)

    today = now.strftime("%Y-%m-%d")

    data = api_get(
        f"fixtures/date/{today}",
        params={
            "include": "participants,state,scores,events",
            "per_page": 50,
        },
    )

    if not data:
        print("Could not retrieve today's fixtures.")
        return []

    fixtures = data.get("data", [])

    print(f"Fixtures today: {len(fixtures)}")

    for fixture in fixtures[:20]:

        fixture_id = fixture.get("id")
        name = fixture.get("name")
        starting_at = fixture.get("starting_at")
        state = fixture.get("state")

        state_name = None

        if isinstance(state, dict):
            state_name = (
                state.get("name")
                or state.get("short_name")
                or state.get("developer_name")
            )

        print("\n----------------------------------------")
        print(f"Fixture ID: {fixture_id}")
        print(f"Name: {name}")
        print(f"Starting: {starting_at}")
        print(f"State: {state_name}")

    return fixtures


# ============================================================
# TEST 3 — LATEST UPDATED FIXTURES
# ============================================================

def test_latest_updated():
    print("\n" + "=" * 70)
    print("TEST 3 — LATEST UPDATED FIXTURES")
    print("=" * 70)

    data = api_get(
        "fixtures/latest",
        params={
            "include": "participants,state,scores,events",
        },
    )

    if not data:
        print("Could not retrieve latest updated fixtures.")
        return []

    fixtures = data.get("data", [])

    print(
        "Fixtures updated within latest-update window: "
        f"{len(fixtures)}"
    )

    for fixture in fixtures[:20]:

        fixture_id = fixture.get("id")
        name = fixture.get("name")
        starting_at = fixture.get("starting_at")

        state = fixture.get("state")
        scores = fixture.get("scores")
        events = fixture.get("events")

        print("\n----------------------------------------")
        print(f"Fixture ID: {fixture_id}")
        print(f"Name: {name}")
        print(f"Starting: {starting_at}")

        if isinstance(state, dict):
            print(
                "State:",
                state.get("name")
                or state.get("short_name")
                or state.get("developer_name")
            )
        else:
            print("State:", state)

        print(
            "Scores:",
            len(scores) if isinstance(scores, list) else 0
        )

        print(
            "Events:",
            len(events) if isinstance(events, list) else 0
        )

    return fixtures


# ============================================================
# TEST 4 — DETAILED FIXTURE
# ============================================================

def test_detailed_fixture(fixtures, event_types):
    print("\n" + "=" * 70)
    print("TEST 4 — DETAILED FIXTURE")
    print("=" * 70)

    if not fixtures:
        print("No fixture available for detailed testing.")
        return

    fixture = fixtures[0]

    fixture_id = fixture.get("id")

    if not fixture_id:
        print("Fixture has no ID.")
        return

    print(f"Testing fixture ID: {fixture_id}")

    data = api_get(
        f"fixtures/{fixture_id}",
        params={
            "include": "participants,state,scores,events",
        },
    )

    if not data:
        print("Could not retrieve fixture details.")
        return

    fixture = data.get("data")

    if not fixture:
        print("No fixture data returned.")
        return

    # --------------------------------------------------------
    # MATCH INFORMATION
    # --------------------------------------------------------

    print("\nMATCH INFORMATION")
    print("----------------------------------------")

    print("ID:", fixture.get("id"))
    print("Name:", fixture.get("name"))
    print("Starting:", fixture.get("starting_at"))
    print("Result:", fixture.get("result_info"))

    # --------------------------------------------------------
    # STATE
    # --------------------------------------------------------

    state = fixture.get("state")

    print("\nSTATE")
    print("----------------------------------------")

    if isinstance(state, dict):
        print("ID:", state.get("id"))
        print("Name:", state.get("name"))
        print("Short:", state.get("short_name"))
        print("Developer:", state.get("developer_name"))
    else:
        print(state)

    # --------------------------------------------------------
    # PARTICIPANTS
    # --------------------------------------------------------

    participants = fixture.get("participants")

    print("\nPARTICIPANTS")
    print("----------------------------------------")

    if isinstance(participants, list):

        for participant in participants:

            print(
                "Team:",
                participant.get("name"),
                "| ID:",
                participant.get("id"),
                "| Meta:",
                participant.get("meta"),
            )

    else:
        print("No participants.")

    # --------------------------------------------------------
    # SCORES
    # --------------------------------------------------------

    scores = fixture.get("scores")

    print("\nSCORES")
    print("----------------------------------------")

    if isinstance(scores, list):

        for score in scores:
            print("Score:", score)

    else:
        print("No scores.")

    # --------------------------------------------------------
    # EVENTS
    # --------------------------------------------------------

    events = fixture.get("events")

    print("\nEVENTS")
    print("----------------------------------------")

    if not isinstance(events, list) or not events:
        print("No events.")
        return

    print(f"Total events: {len(events)}")

    for event in events:

        event_id = event.get("id")
        type_id = event.get("type_id")
        minute = event.get("minute")
        extra_minute = event.get("extra_minute")
        player_name = event.get("player_name")
        related_player_name = event.get("related_player_name")
        result = event.get("result")

        event_info = event_types.get(type_id, {})

        type_name = event_info.get("name")
        type_code = event_info.get("code")

        print("\nEVENT")
        print("----------------------------------------")
        print("ID:", event_id)
        print("Type ID:", type_id)
        print("Type name:", type_name)
        print("Type code:", type_code)
        print("Minute:", minute)
        print("Extra minute:", extra_minute)
        print("Player:", player_name)
        print("Related player:", related_player_name)
        print("Result:", result)


# ============================================================
# TEST 5 — LIVE SCORES
# ============================================================

def test_live_scores():
    print("\n" + "=" * 70)
    print("TEST 5 — LIVE SCORES")
    print("=" * 70)

    data = api_get(
        "livescores",
        params={
            "include": "participants,state,scores,events",
        },
    )

    if not data:
        print("Could not retrieve livescores.")
        return []

    fixtures = data.get("data", [])

    print(
        f"Live matches currently available: {len(fixtures)}"
    )

    if not fixtures:
        print("No live matches currently available.")
        return []

    for fixture in fixtures[:20]:

        print("\n----------------------------------------")

        print("Fixture ID:", fixture.get("id"))
        print("Name:", fixture.get("name"))
        print("Starting:", fixture.get("starting_at"))

        state = fixture.get("state")

        if isinstance(state, dict):
            print(
                "State:",
                state.get("name")
                or state.get("short_name")
                or state.get("developer_name")
            )

        scores = fixture.get("scores")

        print(
            "Scores:",
            scores if scores else "None"
        )

        events = fixture.get("events")

        print(
            "Events:",
            len(events) if isinstance(events, list) else 0
        )

    return fixtures


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("SPORTMONKS DEEP TEST")
    print("=" * 70)

    now = datetime.now(timezone.utc)

    print(
        "Current UTC:",
        now.strftime("%Y-%m-%d %H:%M:%S")
    )

    # --------------------------------------------------------
    # TEST 1
    # --------------------------------------------------------

    event_types = test_event_types()

    # --------------------------------------------------------
    # TEST 2
    # --------------------------------------------------------

    fixtures = test_recent_fixtures()

    # --------------------------------------------------------
    # TEST 3
    # --------------------------------------------------------

    latest = test_latest_updated()

    # --------------------------------------------------------
    # TEST 4
    # --------------------------------------------------------

    detailed_source = latest if latest else fixtures

    test_detailed_fixture(
        detailed_source,
        event_types,
    )

    # --------------------------------------------------------
    # TEST 5
    # --------------------------------------------------------

    test_live_scores()

    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("SPORTMONKS DEEP TEST FINISHED")
    print("=" * 70)


if __name__ == "__main__":
    main()

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
            print(response.text[:3000])
            return None

        return response.json()

    except requests.RequestException as e:
        print(f"REQUEST ERROR: {e}")
        return None


# ============================================================
# TEST 1 — TODAY'S FIXTURES
# ============================================================

def test_recent_fixtures():
    print("\n" + "=" * 70)
    print("TEST 1 — TODAY'S FIXTURES")
    print("=" * 70)

    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")

    data = api_get(
        f"fixtures/date/{today}",
        params={
            "include": "participants;state;scores;events",
            "per_page": 50,
        },
    )

    if not data:
        print("Could not retrieve today's fixtures.")
        return []

    fixtures = data.get("data", [])

    print(f"Fixtures today: {len(fixtures)}")

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
        else:
            print("State:", state)

        scores = fixture.get("scores")

        print(
            "Scores:",
            len(scores) if isinstance(scores, list) else 0
        )

        events = fixture.get("events")

        print(
            "Events:",
            len(events) if isinstance(events, list) else 0
        )

    return fixtures


# ============================================================
# TEST 2 — ALL LIVESCORES
# ============================================================

def test_livescores():
    print("\n" + "=" * 70)
    print("TEST 2 — ALL LIVESCORES")
    print("=" * 70)

    data = api_get(
        "livescores",
        params={
            "include": "participants;state;scores;events",
        },
    )

    if not data:
        print("Could not retrieve livescores.")
        return []

    fixtures = data.get("data", [])

    print(
        f"Livescores currently available: {len(fixtures)}"
    )

    if not fixtures:
        print("No livescores currently available.")
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

        print("Scores:")
        if isinstance(scores, list):
            for score in scores:
                print(" ", score)

        events = fixture.get("events")

        print(
            "Events:",
            len(events) if isinstance(events, list) else 0
        )

    return fixtures


# ============================================================
# TEST 3 — LATEST UPDATED LIVESCORES
# ============================================================

def test_latest_livescores():
    print("\n" + "=" * 70)
    print("TEST 3 — LATEST UPDATED LIVESCORES")
    print("=" * 70)

    data = api_get(
        "livescores/latest",
        params={
            "include": "participants;state;scores;events",
        },
    )

    if not data:
        print("Could not retrieve latest updated livescores.")
        return []

    fixtures = data.get("data", [])

    print(
        "Recently updated live fixtures: "
        f"{len(fixtures)}"
    )

    if not fixtures:
        print(
            "No recently updated live fixtures "
            "were returned."
        )
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
        events = fixture.get("events")

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

def test_detailed_fixture(fixtures):

    print("\n" + "=" * 70)
    print("TEST 4 — DETAILED FIXTURE")
    print("=" * 70)

    if not fixtures:
        print("No fixture available for detailed testing.")
        return

    fixture_id = fixtures[0].get("id")

    if not fixture_id:
        print("Fixture has no ID.")
        return

    print("Testing fixture ID:", fixture_id)

    data = api_get(
        f"fixtures/{fixture_id}",
        params={
            "include": "participants;state;scores;events",
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
    # MATCH
    # --------------------------------------------------------

    print("\nMATCH")
    print("----------------------------------------")

    print("ID:", fixture.get("id"))
    print("Name:", fixture.get("name"))
    print("Starting:", fixture.get("starting_at"))
    print("Result info:", fixture.get("result_info"))

    # --------------------------------------------------------
    # STATE
    # --------------------------------------------------------

    print("\nSTATE")
    print("----------------------------------------")

    state = fixture.get("state")

    if isinstance(state, dict):

        print("ID:", state.get("id"))
        print("Name:", state.get("name"))
        print("Short:", state.get("short_name"))
        print(
            "Developer:",
            state.get("developer_name")
        )

    else:
        print(state)

    # --------------------------------------------------------
    # PARTICIPANTS
    # --------------------------------------------------------

    print("\nPARTICIPANTS")
    print("----------------------------------------")

    participants = fixture.get("participants")

    if isinstance(participants, list):

        for participant in participants:

            print(
                "Team:",
                participant.get("name")
            )

            print(
                "ID:",
                participant.get("id")
            )

            print(
                "Meta:",
                participant.get("meta")
            )

            print()

    else:
        print("No participants.")

    # --------------------------------------------------------
    # SCORES
    # --------------------------------------------------------

    print("\nSCORES")
    print("----------------------------------------")

    scores = fixture.get("scores")

    if isinstance(scores, list):

        for score in scores:

            print(score)

    else:
        print("No scores.")

    # --------------------------------------------------------
    # EVENTS
    # --------------------------------------------------------

    print("\nEVENTS")
    print("----------------------------------------")

    events = fixture.get("events")

    if not isinstance(events, list) or not events:

        print("No events.")
        return

    print("Total events:", len(events))

    for event in events:

        print("\nEVENT")
        print("----------------------------------------")

        print("ID:", event.get("id"))
        print("Type ID:", event.get("type_id"))
        print("Minute:", event.get("minute"))
        print(
            "Extra minute:",
            event.get("extra_minute")
        )
        print(
            "Player:",
            event.get("player_name")
        )
        print(
            "Related player:",
            event.get("related_player_name")
        )
        print(
            "Result:",
            event.get("result")
        )


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

    fixtures = test_recent_fixtures()

    # --------------------------------------------------------
    # TEST 2
    # --------------------------------------------------------

    live = test_livescores()

    # --------------------------------------------------------
    # TEST 3
    # --------------------------------------------------------

    latest = test_latest_livescores()

    # --------------------------------------------------------
    # TEST 4
    # --------------------------------------------------------

    detailed_source = (
        latest
        if latest
        else live
        if live
        else fixtures
    )

    test_detailed_fixture(
        detailed_source
    )

    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("SPORTMONKS DEEP TEST FINISHED")
    print("=" * 70)


if __name__ == "__main__":
    main()

import os
import requests
from datetime import datetime, timezone


BASE_URL = "https://api.sportmonks.com/v3/football"


def api_get(endpoint, params=None):
    token = os.getenv("SPORTMONKS_TOKEN")

    if not token:
        print("ERROR: SPORTMONKS_TOKEN is not configured.")
        return None

    try:
        response = requests.get(
            f"{BASE_URL}/{endpoint}",
            params=params or {},
            headers={
                "Authorization": token,
                "Accept": "application/json",
            },
            timeout=20,
        )

    except requests.RequestException as exc:
        print(f"REQUEST ERROR: {exc}")
        return None

    print(f"HTTP {response.status_code}: {endpoint}")

    if response.status_code != 200:
        print(response.text[:3000])
        return None

    try:
        return response.json()

    except ValueError:
        print("ERROR: Invalid JSON response.")
        print(response.text[:3000])
        return None


def test_leagues():
    print()
    print("=" * 70)
    print("TEST 1 — AVAILABLE LEAGUES")
    print("=" * 70)

    payload = api_get("leagues")

    if payload is None:
        return []

    leagues = payload.get("data", [])

    print(f"Leagues returned: {len(leagues)}")
    print()

    for league in leagues:
        print(
            f"League ID: {league.get('id')} | "
            f"Name: {league.get('name')} | "
            f"Country ID: {league.get('country_id')}"
        )

    return leagues


def test_upcoming_fixtures():
    print()
    print("=" * 70)
    print("TEST 2 — UPCOMING FIXTURES")
    print("=" * 70)

    today = datetime.now(timezone.utc).date().isoformat()

    payload = api_get(
        f"fixtures/date/{today}",
        params={
            "include": (
                "participants;"
                "scores;"
                "events;"
                "state;"
                "league"
            )
        },
    )

    if payload is None:
        return

    fixtures = payload.get("data", [])

    print(f"Fixtures today: {len(fixtures)}")
    print()

    if not fixtures:
        print("No fixtures returned for today.")
        return

    for fixture in fixtures[:20]:

        print("-" * 70)

        print(f"Fixture ID: {fixture.get('id')}")
        print(f"Name: {fixture.get('name')}")
        print(f"Starting At: {fixture.get('starting_at')}")
        print(f"State ID: {fixture.get('state_id')}")

        league = fixture.get("league") or {}

        print(
            f"League: "
            f"{league.get('name')} "
            f"(ID: {league.get('id')})"
        )

        participants = fixture.get("participants") or []

        print()
        print("Participants:")

        for team in participants:
            print(
                f"  - {team.get('name')} "
                f"(ID: {team.get('id')})"
            )

        scores = fixture.get("scores") or []

        print()
        print(f"Scores: {len(scores)}")

        for score in scores:
            print(
                f"  - "
                f"Participant ID: {score.get('participant_id')} | "
                f"Goals: {score.get('goals')} | "
                f"Description: {score.get('description')}"
            )

        events = fixture.get("events") or []

        print()
        print(f"Events: {len(events)}")

        for event in events:
            print(
                "  EVENT:",
                {
                    "id": event.get("id"),
                    "type_id": event.get("type_id"),
                    "minute": event.get("minute"),
                    "extra_minute": event.get(
                        "extra_minute"
                    ),
                    "player_name": event.get(
                        "player_name"
                    ),
                    "related_player_name": event.get(
                        "related_player_name"
                    ),
                    "result": event.get("result"),
                }
            )


def test_live():
    print()
    print("=" * 70)
    print("TEST 3 — LIVE MATCHES")
    print("=" * 70)

    payload = api_get(
        "livescores",
        params={
            "include": (
                "participants;"
                "scores;"
                "events;"
                "state;"
                "league"
            )
        },
    )

    if payload is None:
        return

    matches = payload.get("data", [])

    print(f"Live matches: {len(matches)}")
    print()

    if not matches:
        print("No live matches are currently available.")
        return

    for match in matches:

        print("-" * 70)

        print(f"Fixture ID: {match.get('id')}")
        print(f"Name: {match.get('name')}")
        print(f"Starting At: {match.get('starting_at')}")
        print(f"State ID: {match.get('state_id')}")

        league = match.get("league") or {}

        print(
            f"League: "
            f"{league.get('name')} "
            f"(ID: {league.get('id')})"
        )

        participants = match.get("participants") or []

        print()
        print("Participants:")

        for team in participants:
            print(
                f"  - {team.get('name')} "
                f"(ID: {team.get('id')})"
            )

        scores = match.get("scores") or []

        print()
        print(f"Scores: {len(scores)}")

        for score in scores:
            print(
                f"  - "
                f"Participant ID: {score.get('participant_id')} | "
                f"Goals: {score.get('goals')} | "
                f"Description: {score.get('description')}"
            )

        events = match.get("events") or []

        print()
        print(f"Events: {len(events)}")

        for event in events:

            print(
                "  EVENT:",
                {
                    "id": event.get("id"),
                    "type_id": event.get("type_id"),
                    "minute": event.get("minute"),
                    "extra_minute": event.get(
                        "extra_minute"
                    ),
                    "player_name": event.get(
                        "player_name"
                    ),
                    "related_player_name": event.get(
                        "related_player_name"
                    ),
                    "result": event.get("result"),
                }
            )


def main():

    print("=" * 70)
    print("SPORTMONKS FREE PLAN DEEP TEST")
    print("=" * 70)

    print(
        "UTC:",
        datetime.now(timezone.utc).isoformat()
    )

    leagues = test_leagues()

    if not leagues:
        print()
        print("WARNING: No leagues returned.")

    test_upcoming_fixtures()

    test_live()

    print()
    print("=" * 70)
    print("SPORTMONKS TEST FINISHED")
    print("=" * 70)


if __name__ == "__main__":
    raise SystemExit(main())

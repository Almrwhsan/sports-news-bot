import os
import requests
from datetime import datetime


API_URL = "https://api.sportmonks.com/v3/football/livescores"


def main():
    token = os.getenv("SPORTMONKS_TOKEN")

    if not token:
        print("ERROR: SPORTMONKS_TOKEN is not configured.")
        return 1

    print("=" * 60)
    print("SPORTMONKS LIVE API TEST")
    print("=" * 60)

    print(f"Time: {datetime.utcnow().isoformat()}Z")
    print("Requesting live matches...")

    try:
        response = requests.get(
            API_URL,
            params={
                "include": "participants;events"
            },
            headers={
                "Authorization": token
            },
            timeout=15,
        )
    except requests.RequestException as exc:
        print(f"REQUEST ERROR: {exc}")
        return 1

    print(f"HTTP Status: {response.status_code}")

    if response.status_code != 200:
        print("API request failed.")
        print(response.text[:2000])
        return 1

    try:
        payload = response.json()
    except ValueError:
        print("ERROR: API did not return valid JSON.")
        print(response.text[:2000])
        return 1

    matches = payload.get("data", [])

    print(f"Live matches returned: {len(matches)}")
    print()

    if not matches:
        print("No live matches are currently available.")
        print("This does NOT mean the API is broken.")
        print("It may simply mean there are no live matches in the")
        print("free-plan competitions at this moment.")
        return 0

    for index, match in enumerate(matches, start=1):

        print("-" * 60)
        print(f"MATCH #{index}")

        print(f"Fixture ID: {match.get('id')}")
        print(f"Name: {match.get('name')}")
        print(f"State ID: {match.get('state_id')}")
        print(f"Starting At: {match.get('starting_at')}")

        participants = match.get("participants") or []

        print()
        print("PARTICIPANTS:")

        for team in participants:
            print(
                f"  - {team.get('name')} "
                f"(ID: {team.get('id')})"
            )

        events = match.get("events") or []

        print()
        print(f"EVENTS: {len(events)}")

        for event in events:

            print(
                "  EVENT:",
                {
                    "id": event.get("id"),
                    "type_id": event.get("type_id"),
                    "minute": event.get("minute"),
                    "extra_minute": event.get("extra_minute"),
                    "player_name": event.get("player_name"),
                    "related_player_name": event.get(
                        "related_player_name"
                    ),
                    "result": event.get("result"),
                }
            )

    print()
    print("=" * 60)
    print("SPORTMONKS TEST FINISHED")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

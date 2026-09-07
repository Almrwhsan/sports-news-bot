from datetime import datetime, timezone
import requests


URL = "https://sportscore.com/api/widget/team/"

TEAMS = [
    ("Real Madrid", "real-madrid"),
    ("Barcelona", "barcelona"),
    ("Manchester City", "manchester-city"),
    ("Liverpool", "liverpool"),
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(compatible; NabdMadridLiveBot/1.0)"
    ),
    "Accept": "application/json",
}

TIMEOUT = 15


def parse_time(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(
            str(value).replace("Z", "+00:00")
        )
    except (TypeError, ValueError):
        return None


def normalize(value):
    if value is None:
        return ""

    return str(value).strip().lower()


def is_live(match):
    status = normalize(match.get("status"))
    text = normalize(match.get("status_text"))

    live_values = {
        "live",
        "inplay",
        "in-play",
        "playing",
        "started",
        "halftime",
        "half-time",
    }

    if status in live_values:
        return True

    return any(
        word in text
        for word in (
            "live",
            "in play",
            "in-play",
            "playing",
            "half time",
            "halftime",
        )
    )


def is_upcoming(match):
    status = normalize(match.get("status"))
    text = normalize(match.get("status_text"))

    upcoming_values = {
        "upcoming",
        "scheduled",
        "not_started",
        "not-started",
        "pre",
    }

    if status in upcoming_values:
        return True

    return any(
        word in text
        for word in (
            "not started",
            "scheduled",
            "upcoming",
        )
    )


def get_matches(data):
    if not isinstance(data, dict):
        return []

    matches = data.get("matches")

    if isinstance(matches, list):
        return matches

    return []


def fetch_team(session, team_name, slug):
    print()
    print("=" * 70)
    print(f"TEAM: {team_name}")
    print(f"SLUG: {slug}")
    print("=" * 70)

    params = {
        "sport": "football",
        "slug": slug,
        "src": "nabd-madrid",
    }

    try:
        response = session.get(
            URL,
            params=params,
            timeout=TIMEOUT,
        )

        print("HTTP STATUS:", response.status_code)

        response.raise_for_status()

        data = response.json()

        if not isinstance(data, dict):
            print("Unexpected response format.")
            return None

        return data

    except requests.RequestException as error:
        print(
            "REQUEST ERROR:",
            type(error).__name__,
            str(error),
        )
        return None

    except ValueError as error:
        print("INVALID JSON:", error)
        return None


def print_match(match, index):
    home = match.get("home")
    away = match.get("away")

    print()
    print(f"MATCH #{index}")
    print(f"{home} vs {away}")
    print(f"Competition : {match.get('competition')}")
    print(f"Status      : {match.get('status')}")
    print(f"Status text : {match.get('status_text')}")
    print(f"Time        : {match.get('time')}")
    print(f"URL         : {match.get('url')}")

    print(
        "Home logo   :",
        bool(match.get("home_logo")),
    )

    print(
        "Away logo   :",
        bool(match.get("away_logo")),
    )

    print(
        "Competition logo:",
        bool(match.get("competition_logo")),
    )


def main():
    print("=" * 70)
    print("SPORTSCORE TEAM DISCOVERY TEST")
    print("=" * 70)

    now = datetime.now(timezone.utc)

    print()
    print("CURRENT UTC:", now.isoformat())

    session = requests.Session()
    session.headers.update(HEADERS)

    total_success = 0
    total_failed = 0

    all_results = {}

    for team_name, slug in TEAMS:

        data = fetch_team(
            session,
            team_name,
            slug,
        )

        if data is None:
            total_failed += 1
            all_results[team_name] = []
            continue

        total_success += 1

        matches = get_matches(data)

        print()
        print("MATCH COUNT:", len(matches))

        live_matches = [
            match
            for match in matches
            if is_live(match)
        ]

        upcoming_matches = [
            match
            for match in matches
            if is_upcoming(match)
        ]

        dated_upcoming = []

        for match in upcoming_matches:
            match_time = parse_time(
                match.get("time")
            )

            if match_time is None:
                continue

            dated_upcoming.append(
                (match_time, match)
            )

        dated_upcoming.sort(
            key=lambda item: item[0]
        )

        print(
            "LIVE COUNT:",
            len(live_matches),
        )

        print(
            "UPCOMING COUNT:",
            len(upcoming_matches),
        )

        all_results[team_name] = matches

        print()
        print("-" * 70)
        print("LIVE MATCHES")
        print("-" * 70)

        if not live_matches:
            print("None")

        for index, match in enumerate(
            live_matches,
            start=1,
        ):
            print_match(
                match,
                index,
            )

        print()
        print("-" * 70)
        print("NEAREST UPCOMING MATCHES")
        print("-" * 70)

        if not dated_upcoming:
            print("None")

        for index, (_, match) in enumerate(
            dated_upcoming[:3],
            start=1,
        ):
            print_match(
                match,
                index,
            )

    print()
    print("=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)

    print(
        "Successful teams:",
        total_success,
    )

    print(
        "Failed teams    :",
        total_failed,
    )

    for team_name, matches in all_results.items():

        live_count = sum(
            1
            for match in matches
            if is_live(match)
        )

        upcoming_count = sum(
            1
            for match in matches
            if is_upcoming(match)
        )

        print(
            f"{team_name}: "
            f"total={len(matches)}, "
            f"live={live_count}, "
            f"upcoming={upcoming_count}"
        )

    print()
    print("=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()

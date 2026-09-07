import requests
import time
from datetime import datetime, timezone


TEAM_URL = "https://sportscore.com/api/widget/team/"

TIMEOUT = 20

TEAMS = [
    ("Real Madrid", "real-madrid"),
    ("Barcelona", "barcelona"),
    ("Manchester City", "manchester-city"),
    ("Liverpool", "liverpool"),
    ("Bayern Munich", "bayern-munich"),
    ("Paris Saint-Germain", "paris-saint-germain"),
    ("Inter Milan", "inter-milan"),
    ("Arsenal", "arsenal"),
    ("Chelsea", "chelsea"),
    ("Atletico Madrid", "atletico-madrid"),
]


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(compatible; NabdMadridLiveBot/1.0)"
    ),
    "Accept": "application/json",
}


def normalize(value):
    if value is None:
        return ""

    return str(value).strip().lower()


def is_live(match):
    if not isinstance(match, dict):
        return False

    status = normalize(match.get("status"))
    status_text = normalize(match.get("status_text"))

    live_statuses = {
        "live",
        "inplay",
        "in-play",
        "playing",
        "started",
        "halftime",
        "half-time",
    }

    if status in live_statuses:
        return True

    live_words = (
        "live",
        "in play",
        "in-play",
        "playing",
        "half time",
        "halftime",
    )

    if any(word in status_text for word in live_words):
        return True

    minute = (
        match.get("live_minute")
        if match.get("live_minute") is not None
        else match.get("minute")
    )

    if minute is not None:
        try:
            return int(minute) > 0
        except (TypeError, ValueError):
            pass

    return False


def get_matches(data):
    if not isinstance(data, dict):
        return []

    matches = data.get("matches")

    if isinstance(matches, list):
        return matches

    return []


def print_match(match):
    print()
    print("  HOME:", match.get("home"))
    print("  AWAY:", match.get("away"))

    print(
        "  SCORE:",
        match.get("home_score"),
        "-",
        match.get("away_score"),
    )

    print("  STATUS:", match.get("status"))
    print("  STATUS TEXT:", match.get("status_text"))
    print("  MINUTE:", match.get("minute"))
    print("  LIVE MINUTE:", match.get("live_minute"))
    print("  TIME:", match.get("time"))
    print("  COMPETITION:", match.get("competition"))
    print("  URL:", match.get("url"))

    print(
        "  HOME LOGO:",
        bool(match.get("home_logo")),
    )

    print(
        "  AWAY LOGO:",
        bool(match.get("away_logo")),
    )

    print(
        "  COMPETITION LOGO:",
        bool(match.get("competition_logo")),
    )

    incidents = match.get("incidents")

    if isinstance(incidents, list):
        print(
            "  INCIDENTS:",
            len(incidents),
        )


def fetch_team(session, name, slug):
    params = {
        "sport": "football",
        "slug": slug,
        "src": "nabd-madrid",
    }

    for attempt in range(1, 4):

        try:
            response = session.get(
                TEAM_URL,
                params=params,
                timeout=TIMEOUT,
            )

            print(
                f"HTTP STATUS: {response.status_code}"
            )

            if response.status_code == 503:
                print(
                    f"503 received. Retry {attempt}/3..."
                )

                if attempt < 3:
                    time.sleep(5)

                continue

            response.raise_for_status()

            return response.json()

        except requests.RequestException as error:

            print(
                f"REQUEST ERROR: {error}"
            )

            if attempt < 3:
                time.sleep(5)

    return None


def main():

    print()
    print("=" * 70)
    print("SPORTSCORE LIVE TEAM DISCOVERY TEST")
    print("=" * 70)

    print()
    print(
        "CURRENT UTC:",
        datetime.now(timezone.utc).isoformat(),
    )

    session = requests.Session()
    session.headers.update(HEADERS)

    total_success = 0
    total_live = 0

    live_results = []

    for name, slug in TEAMS:

        print()
        print("=" * 70)
        print("TEAM:", name)
        print("SLUG:", slug)
        print("=" * 70)

        data = fetch_team(
            session,
            name,
            slug,
        )

        if data is None:
            print("RESULT: FAILED")
            continue

        matches = get_matches(data)

        total_success += 1

        print(
            "MATCH COUNT:",
            len(matches),
        )

        live_matches = [
            match
            for match in matches
            if is_live(match)
        ]

        print(
            "LIVE MATCHES:",
            len(live_matches),
        )

        if not live_matches:
            print(
                "No live match found for this team."
            )
            continue

        total_live += len(live_matches)

        for match in live_matches:

            live_results.append(
                (name, match)
            )

            print()
            print(
                "🔥 LIVE MATCH FOUND!"
            )

            print_match(match)

    print()
    print("=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)

    print(
        "Successful team requests:",
        total_success,
        "/",
        len(TEAMS),
    )

    print(
        "Total live matches found:",
        total_live,
    )

    if live_results:

        print()
        print("=" * 70)
        print("LIVE MATCHES DISCOVERED")
        print("=" * 70)

        for team_name, match in live_results:

            print()
            print(
                "DISCOVERED THROUGH:",
                team_name,
            )

            print_match(match)

        print()
        print(
            "SUCCESS: /team/ exposes live-match data."
        )

    else:

        print()
        print(
            "NO LIVE MATCH FOUND "
            "THROUGH ANY TESTED TEAM."
        )

        print()
        print(
            "This does NOT prove that /team/ "
            "cannot expose live matches."
        )

        print(
            "It only means no tested team had "
            "a live match in its returned data "
            "at this moment."
        )

    print()
    print("=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()

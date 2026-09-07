import json
import requests
from datetime import datetime, timezone


URL = "https://sportscore.com/api/widget/matches/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(compatible; NabdMadridLiveBot/1.0)"
    ),
    "Accept": "application/json",
}

TIMEOUT = 20


def fetch_matches():
    params = {
        "sport": "football",
        "limit": 100,
        "src": "nabd-madrid",
    }

    session = requests.Session()
    session.headers.update(HEADERS)

    print("=" * 70)
    print("SPORTSCORE MATCHES FILTER TEST")
    print("=" * 70)
    print("Requesting matches...")
    print()

    response = session.get(
        URL,
        params=params,
        timeout=TIMEOUT,
    )

    print("HTTP STATUS:", response.status_code)
    print("FINAL URL:", response.url)

    response.raise_for_status()

    data = response.json()

    if not isinstance(data, dict):
        raise ValueError("Unexpected response format.")

    return data


def get_matches(data):
    matches = data.get("matches")

    if isinstance(matches, list):
        return matches

    # بعض الاستجابات قد تستخدم data
    nested = data.get("data")

    if isinstance(nested, dict):
        matches = nested.get("matches")

        if isinstance(matches, list):
            return matches

    return []


def normalize(value):
    if value is None:
        return ""

    return str(value).strip().lower()


def is_live(match):
    status = normalize(match.get("status"))
    status_text = normalize(match.get("status_text"))

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

    live_words = (
        "live",
        "in play",
        "in-play",
        "playing",
        "half time",
        "halftime",
    )

    return any(word in status_text for word in live_words)


def is_upcoming(match):
    status = normalize(match.get("status"))
    status_text = normalize(match.get("status_text"))

    upcoming_values = {
        "upcoming",
        "scheduled",
        "not_started",
        "not-started",
        "pre",
    }

    if status in upcoming_values:
        return True

    upcoming_words = (
        "not started",
        "scheduled",
        "upcoming",
    )

    return any(word in status_text for word in upcoming_words)


def is_finished(match):
    status = normalize(match.get("status"))
    status_text = normalize(match.get("status_text"))

    finished_values = {
        "finished",
        "complete",
        "completed",
        "ended",
        "ft",
        "after",
    }

    if status in finished_values:
        return True

    finished_words = (
        "finished",
        "completed",
        "ended",
        "full time",
        "match ended",
    )

    return any(word in status_text for word in finished_words)


def match_text(match):
    values = [
        match.get("home"),
        match.get("away"),
        match.get("competition"),
    ]

    return " ".join(
        normalize(value)
        for value in values
        if value
    )


def contains_any(text, values):
    return any(value in text for value in values)


# البطولات التي سنهتم بها
IMPORTANT_COMPETITIONS = [
    "champions league",
    "uefa champions league",
    "la liga",
    "spanish la liga",
    "premier league",
    "english premier league",
    "serie a",
    "italian serie a",
    "bundesliga",
    "ligue 1",
    "fifa world cup",
    "world cup",
    "europa league",
    "conference league",
]


# فرق عالمية نريد مراقبتها
IMPORTANT_TEAMS = [
    "real madrid",
    "barcelona",
    "atletico madrid",
    "manchester city",
    "manchester united",
    "liverpool",
    "arsenal",
    "chelsea",
    "tottenham",
    "newcastle",
    "bayern munich",
    "borussia dortmund",
    "bayer leverkusen",
    "paris saint-germain",
    "inter milan",
    "ac milan",
    "juventus",
    "napoli",
    "roma",
]


def is_important_competition(match):
    competition = normalize(
        match.get("competition")
    )

    return contains_any(
        competition,
        IMPORTANT_COMPETITIONS,
    )


def is_important_team(match):
    home = normalize(match.get("home"))
    away = normalize(match.get("away"))

    return (
        home in IMPORTANT_TEAMS
        or away in IMPORTANT_TEAMS
    )


def print_match(prefix, match):
    home = match.get("home")
    away = match.get("away")

    print(
        f"{prefix} "
        f"{home} vs {away}"
    )

    print(
        f"    Competition: "
        f"{match.get('competition')}"
    )

    print(
        f"    Status     : "
        f"{match.get('status')} "
        f"({match.get('status_text')})"
    )

    print(
        f"    Time       : "
        f"{match.get('time')}"
    )

    print(
        f"    URL        : "
        f"{match.get('url')}"
    )

    print()


def main():
    data = fetch_matches()

    print()
    print("=" * 70)
    print("RESPONSE KEYS")
    print("=" * 70)

    print(list(data.keys()))

    matches = get_matches(data)

    print()
    print("=" * 70)
    print("TOTAL MATCHES")
    print("=" * 70)

    print(len(matches))

    if not matches:
        print()
        print("No matches found.")
        return

    live_matches = []
    important_competition = []
    important_team = []
    important_both = []

    for match in matches:

        live = is_live(match)
        important_comp = is_important_competition(match)
        important_team_flag = is_important_team(match)

        if live:
            live_matches.append(match)

        if important_comp:
            important_competition.append(match)

        if important_team_flag:
            important_team.append(match)

        if important_comp and important_team_flag:
            important_both.append(match)

    print()
    print("=" * 70)
    print("LIVE MATCHES")
    print("=" * 70)

    print("COUNT:", len(live_matches))

    for index, match in enumerate(
        live_matches,
        start=1,
    ):
        print_match(
            f"#{index}",
            match,
        )

    print()
    print("=" * 70)
    print("IMPORTANT COMPETITIONS")
    print("=" * 70)

    print(
        "COUNT:",
        len(important_competition),
    )

    for index, match in enumerate(
        important_competition[:30],
        start=1,
    ):
        print_match(
            f"#{index}",
            match,
        )

    print()
    print("=" * 70)
    print("IMPORTANT TEAMS")
    print("=" * 70)

    print(
        "COUNT:",
        len(important_team),
    )

    for index, match in enumerate(
        important_team[:30],
        start=1,
    ):
        print_match(
            f"#{index}",
            match,
        )

    print()
    print("=" * 70)
    print("IMPORTANT TEAM + IMPORTANT COMPETITION")
    print("=" * 70)

    print(
        "COUNT:",
        len(important_both),
    )

    for index, match in enumerate(
        important_both[:30],
        start=1,
    ):
        print_match(
            f"#{index}",
            match,
        )

    print()
    print("=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()

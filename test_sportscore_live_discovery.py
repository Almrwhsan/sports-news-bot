import requests
from datetime import datetime, timezone


MATCHES_URL = "https://sportscore.com/api/widget/matches/"
TEAM_URL = "https://sportscore.com/api/widget/team/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(compatible; NabdMadridLiveBot/1.0)"
    ),
    "Accept": "application/json",
}

TIMEOUT = 20


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

    live_words = (
        "live",
        "in play",
        "in-play",
        "playing",
        "half time",
        "halftime",
    )

    return any(
        word in text
        for word in live_words
    )


def get_matches(data):
    if not isinstance(data, dict):
        return []

    matches = data.get("matches")

    if isinstance(matches, list):
        return matches

    return []


def get_slug_from_url(url):
    if not url:
        return None

    url = str(url).strip().strip("/")

    parts = url.split("/")

    if len(parts) < 3:
        return None

    if parts[-2] != "match":
        return None

    slug = parts[-1]

    if not slug:
        return None

    return slug


def get_team_slug(team_name):
    """
    محاولة آمنة فقط لاختبار endpoint.
    لا نستخدم هذا لاحقًا كمولد slug نهائي.
    """

    if not team_name:
        return None

    return (
        normalize(team_name)
        .replace(" ", "-")
        .replace(".", "")
    )


def print_match(match, prefix=""):
    print()
    print(prefix + "HOME:", match.get("home"))
    print(prefix + "AWAY:", match.get("away"))
    print(prefix + "SCORE:", match.get("home_score"),
          "-", match.get("away_score"))
    print(prefix + "STATUS:", match.get("status"))
    print(prefix + "STATUS TEXT:", match.get("status_text"))
    print(prefix + "TIME:", match.get("time"))
    print(prefix + "COMPETITION:", match.get("competition"))
    print(prefix + "URL:", match.get("url"))
    print(prefix + "HOME LOGO:", bool(match.get("home_logo")))
    print(prefix + "AWAY LOGO:", bool(match.get("away_logo")))
    print(prefix + "COMPETITION LOGO:",
          bool(match.get("competition_logo")))


def fetch_matches(session):
    params = {
        "sport": "football",
        "limit": 100,
        "src": "nabd-madrid",
    }

    print("=" * 70)
    print("STEP 1 — FIND LIVE MATCHES")
    print("=" * 70)

    response = session.get(
        MATCHES_URL,
        params=params,
        timeout=TIMEOUT,
    )

    print("HTTP STATUS:", response.status_code)

    response.raise_for_status()

    data = response.json()

    matches = get_matches(data)

    print("TOTAL MATCHES:", len(matches))

    return matches


def fetch_team(session, team_name, slug):
    print()
    print("=" * 70)
    print("STEP 2 — QUERY TEAM ENDPOINT")
    print("=" * 70)

    print("TEAM:", team_name)
    print("SLUG:", slug)

    params = {
        "sport": "football",
        "slug": slug,
        "src": "nabd-madrid",
    }

    response = session.get(
        TEAM_URL,
        params=params,
        timeout=TIMEOUT,
    )

    print("HTTP STATUS:", response.status_code)

    response.raise_for_status()

    data = response.json()

    matches = get_matches(data)

    print("TEAM MATCH COUNT:", len(matches))

    return matches


def same_team(a, b):
    return normalize(a) == normalize(b)


def main():
    print()
    print("=" * 70)
    print("SPORTSCORE LIVE DISCOVERY TEST")
    print("=" * 70)

    now = datetime.now(timezone.utc)

    print()
    print("CURRENT UTC:", now.isoformat())

    session = requests.Session()
    session.headers.update(HEADERS)

    try:
        matches = fetch_matches(session)

    except Exception as error:
        print()
        print("=" * 70)
        print("FAILED TO READ /matches/")
        print("=" * 70)
        print(type(error).__name__, error)
        raise SystemExit(1)

    live_matches = [
        match
        for match in matches
        if is_live(match)
    ]

    print()
    print("=" * 70)
    print("LIVE MATCH COUNT")
    print("=" * 70)

    print(len(live_matches))

    if not live_matches:
        print()
        print("NO LIVE MATCH FOUND.")
        print()
        print(
            "This is not necessarily an API failure."
        )
        print(
            "It may simply mean SportScore currently "
            "has no live match in this endpoint snapshot."
        )
        print()
        print("=" * 70)
        print("TEST COMPLETE")
        print("=" * 70)
        return

    # نأخذ أول مباراة Live فقط
    live_match = live_matches[0]

    print()
    print("=" * 70)
    print("SELECTED LIVE MATCH")
    print("=" * 70)

    print_match(
        live_match,
        prefix="  ",
    )

    home = live_match.get("home")
    away = live_match.get("away")

    # نختبر الفريق المضيف أولًا
    selected_team = home

    if not selected_team:
        selected_team = away

    if not selected_team:
        print("Could not determine team.")
        raise SystemExit(1)

    team_slug = get_team_slug(selected_team)

    if not team_slug:
        print("Could not create test slug.")
        raise SystemExit(1)

    print()
    print("=" * 70)
    print("SELECTED TEAM")
    print("=" * 70)

    print("Team:", selected_team)
    print("Generated slug:", team_slug)

    try:
        team_matches = fetch_team(
            session,
            selected_team,
            team_slug,
        )

    except Exception as error:
        print()
        print("=" * 70)
        print("TEAM ENDPOINT FAILED")
        print("=" * 70)
        print(type(error).__name__, error)
        raise SystemExit(1)

    print()
    print("=" * 70)
    print("SEARCHING TEAM RESULTS FOR SAME MATCH")
    print("=" * 70)

    found = False

    for index, match in enumerate(
        team_matches,
        start=1,
    ):

        home2 = match.get("home")
        away2 = match.get("away")

        same_home = (
            same_team(home, home2)
            and same_team(away, away2)
        )

        same_away = (
            same_team(home, away2)
            and same_team(away, home2)
        )

        if same_home or same_away:
            found = True

            print()
            print(
                "MATCH FOUND IN /team/ RESULT"
            )

            print_match(
                match,
                prefix="  ",
            )

            print()
            print(
                "IS LIVE:",
                is_live(match),
            )

            print(
                "SAME MATCH:",
                True,
            )

    print()
    print("=" * 70)
    print("FINAL RESULT")
    print("=" * 70)

    print("Live match found in /matches/:", True)
    print(
        "Same match found in /team/:",
        found,
    )

    if found:
        print()
        print(
            "SUCCESS: /matches/ and /team/ "
            "can be correlated."
        )
    else:
        print()
        print(
            "WARNING: Live match was found in "
            "/matches/, but not in /team/."
        )

    print()
    print("=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()

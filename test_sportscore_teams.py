import time
import json
import requests


URL = "https://sportscore.com/api/widget/team/"

TEAMS = [
    ("Real Madrid", "real-madrid"),
    ("Barcelona", "barcelona"),
    ("Manchester City", "manchester-city"),
    ("Liverpool", "liverpool"),
    ("Bayern Munich", "bayern-munich"),
    ("Paris Saint-Germain", "paris-saint-germain"),
    ("Inter Milan", "inter-milan"),
    ("Arsenal", "arsenal"),
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(compatible; NabdMadridLiveBot/1.0)"
    ),
    "Accept": "application/json",
}

MAX_RETRIES = 4
RETRY_DELAY = 15
TIMEOUT = 30


def request_team(session, team_name, slug):
    params = {
        "sport": "football",
        "slug": slug,
    }

    for attempt in range(1, MAX_RETRIES + 1):
        print()
        print("-" * 70)
        print(f"TEAM: {team_name}")
        print(f"SLUG: {slug}")
        print(f"ATTEMPT: {attempt}/{MAX_RETRIES}")

        try:
            response = session.get(
                URL,
                params=params,
                timeout=TIMEOUT,
            )

            print("HTTP STATUS:", response.status_code)

            if response.ok:
                data = response.json()
                return data

            if response.status_code in {429, 500, 502, 503, 504}:
                print(
                    f"Temporary HTTP error {response.status_code}."
                )

                if attempt < MAX_RETRIES:
                    print(
                        f"Retrying in {RETRY_DELAY} seconds..."
                    )
                    time.sleep(RETRY_DELAY)
                    continue

            print("REQUEST FAILED:")
            print(response.text[:2000])
            return None

        except requests.RequestException as error:
            print(
                "REQUEST ERROR:",
                type(error).__name__,
                str(error),
            )

            if attempt < MAX_RETRIES:
                print(
                    f"Retrying in {RETRY_DELAY} seconds..."
                )
                time.sleep(RETRY_DELAY)
                continue

            return None

        except ValueError as error:
            print("INVALID JSON:", error)
            print("SERVER RESPONSE:")
            print(response.text[:2000])
            return None

    return None


def extract_matches(data):
    if not isinstance(data, dict):
        return []

    matches = data.get("matches")

    if isinstance(matches, list):
        return matches

    return []


def print_match(index, match):
    if not isinstance(match, dict):
        return

    home = match.get("home")
    away = match.get("away")

    home_score = match.get("home_score")
    away_score = match.get("away_score")

    status = match.get("status")
    status_text = match.get("status_text")

    match_time = match.get("time")
    competition = match.get("competition")

    url = match.get("url")

    print()
    print(f"  MATCH #{index}")
    print(f"  {home} vs {away}")
    print(f"  Score       : {home_score} - {away_score}")
    print(f"  Status      : {status}")
    print(f"  Status text : {status_text}")
    print(f"  Time        : {match_time}")
    print(f"  Competition : {competition}")
    print(f"  URL         : {url}")


def main():
    print("=" * 70)
    print("SPORTSCORE MULTI-TEAM API TEST")
    print("=" * 70)

    session = requests.Session()
    session.headers.update(HEADERS)

    successful = 0
    failed = 0

    results = {}

    for team_name, slug in TEAMS:
        data = request_team(
            session=session,
            team_name=team_name,
            slug=slug,
        )

        if data is None:
            failed += 1
            results[team_name] = {
                "success": False,
                "matches": [],
            }
            continue

        matches = extract_matches(data)

        successful += 1

        results[team_name] = {
            "success": True,
            "matches_count": len(matches),
        }

        print()
        print("=" * 70)
        print(f"{team_name} RESULT")
        print("=" * 70)

        print("JSON TYPE:", type(data).__name__)

        if isinstance(data, dict):
            print("RESPONSE KEYS:", list(data.keys()))

        print("MATCHES:", len(matches))

        # نعرض أول 5 مباريات فقط حتى لا يصبح سجل GitHub ضخمًا
        for index, match in enumerate(matches[:5], start=1):
            print_match(index, match)

        if len(matches) > 5:
            print()
            print(
                f"  ... and {len(matches) - 5} more matches."
            )

    print()
    print("=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)

    print("Successful teams:", successful)
    print("Failed teams    :", failed)

    print()

    for team_name, result in results.items():
        if result["success"]:
            print(
                f"✅ {team_name}: "
                f"{result['matches_count']} matches"
            )
        else:
            print(f"❌ {team_name}: FAILED")

    print()
    print("=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)

    if failed > 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

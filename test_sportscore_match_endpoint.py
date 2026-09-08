import requests
import time


URL = "https://sportscore.com/api/widget/match/"

PARAMS = {
    "sport": "football",
    "slug": "inter-milan-vs-real-madrid",
    "src": "nabd-madrid",
}


def main():

    print("=" * 70)
    print("SPORTSCORE MATCH ENDPOINT TEST")
    print("=" * 70)

    headers_list = [
        {
            "User-Agent": "Mozilla/5.0"
        },
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json,text/plain,*/*",
            "Referer": "https://sportscore.com/football/match/inter-milan-vs-real-madrid/",
        },
    ]

    for i, headers in enumerate(headers_list, 1):

        print(f"\n🔎 TEST {i}")
        print("-" * 70)

        try:
            response = requests.get(
                URL,
                params=PARAMS,
                headers=headers,
                timeout=30,
            )

            print("HTTP:", response.status_code)
            print("URL:", response.url)

            print("\nResponse headers:")
            print("Content-Type:", response.headers.get("content-type"))
            print("Server:", response.headers.get("server"))
            print("CF-Ray:", response.headers.get("cf-ray"))

            print("\nResponse preview:")
            print(response.text[:1000])

            if response.ok:

                try:
                    data = response.json()

                    print("\n✅ JSON SUCCESS")

                    print("Keys:", data.keys())

                    match = data.get("match", data)

                    print("\nHome:", match.get("home"))
                    print("Away:", match.get("away"))
                    print("Score:",
                          match.get("home_score"),
                          "-",
                          match.get("away_score"))
                    print("Status:", match.get("status"))
                    print("Status text:", match.get("status_text"))

                    return

                except Exception as error:
                    print("⚠️ JSON parsing error:", error)

        except requests.RequestException as error:
            print("❌ Request error:", error)

        if i < len(headers_list):
            print("\n⏳ Waiting 5 seconds...")
            time.sleep(5)

    print("\n❌ All endpoint tests failed.")


if __name__ == "__main__":
    main()

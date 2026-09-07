import requests
import json

URL = "https://sportscore.com/api/widget/matches/"

params = {
    "sport": "football",
    "limit": 20,
}

headers = {
    "User-Agent": "Mozilla/5.0 (compatible; NabdMadridLiveBot/1.0)",
    "Accept": "application/json",
}

print("=" * 70)
print("SPORTSCORE MATCHES API TEST")
print("=" * 70)

try:
    response = requests.get(
        URL,
        params=params,
        headers=headers,
        timeout=30,
    )

    print()
    print("HTTP STATUS:", response.status_code)
    print("FINAL URL:", response.url)

    response.raise_for_status()

    data = response.json()

    print()
    print("JSON TYPE:", type(data).__name__)

    print()
    print("FULL RESPONSE")
    print("=" * 70)

    print(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
        )
    )

except Exception as error:

    print()
    print("=" * 70)
    print("ERROR")
    print("=" * 70)

    print(type(error).__name__)
    print(error)

    raise

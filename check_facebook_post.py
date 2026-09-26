import os
import json
import requests

GRAPH_VERSION = "v26.0"
OBJECT_ID = "1061075956557715"

PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
ACCESS_TOKEN = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")


def graph_get(object_id, fields=None):
    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{object_id}"

    params = {
        "access_token": ACCESS_TOKEN,
    }

    if fields:
        params["fields"] = fields

    response = requests.get(
        url,
        params=params,
        timeout=30,
    )

    try:
        data = response.json()
    except ValueError:
        data = {"raw_response": response.text}

    return response.status_code, data


def print_test(title, status, data):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)
    print(f"HTTP Status: {status}")
    print(json.dumps(data, ensure_ascii=False, indent=2))


print("=" * 70)
print("FACEBOOK POST / PHOTO OBJECT INVESTIGATION")
print("=" * 70)

print(f"Page ID: {PAGE_ID}")
print(f"Object ID: {OBJECT_ID}")


if not ACCESS_TOKEN:
    print("❌ FACEBOOK_PAGE_ACCESS_TOKEN is missing.")
    raise SystemExit(1)


# ---------------------------------------------------------
# TEST 1
# Raw object
# ---------------------------------------------------------

status, data = graph_get(OBJECT_ID)

print_test(
    "TEST 1 — RAW OBJECT",
    status,
    data
)


# ---------------------------------------------------------
# TEST 2
# Try common object identification fields
# ---------------------------------------------------------

status, data = graph_get(
    OBJECT_ID,
    "id,created_time,name"
)

print_test(
    "TEST 2 — OBJECT IDENTITY",
    status,
    data
)


# ---------------------------------------------------------
# TEST 3
# Try the object type through metadata
# ---------------------------------------------------------

url = f"https://graph.facebook.com/{GRAPH_VERSION}/{OBJECT_ID}"

response = requests.get(
    url,
    params={
        "metadata": "1",
        "access_token": ACCESS_TOKEN,
    },
    timeout=30,
)

try:
    data = response.json()
except ValueError:
    data = {"raw_response": response.text}

print_test(
    "TEST 3 — FACEBOOK OBJECT METADATA",
    response.status_code,
    data
)


# ---------------------------------------------------------
# TEST 4
# Try Page ownership / author fields
# ---------------------------------------------------------

status, data = graph_get(
    OBJECT_ID,
    "id,from"
)

print_test(
    "TEST 4 — OBJECT OWNER / FROM",
    status,
    data
)


# ---------------------------------------------------------
# TEST 5
# Try link fields
# ---------------------------------------------------------

status, data = graph_get(
    OBJECT_ID,
    "id,link"
)

print_test(
    "TEST 5 — OBJECT LINK",
    status,
    data
)


# ---------------------------------------------------------
# TEST 6
# Query the exact object through Page photos
# ---------------------------------------------------------

photos_url = (
    f"https://graph.facebook.com/"
    f"{GRAPH_VERSION}/{PAGE_ID}/photos"
)

response = requests.get(
    photos_url,
    params={
        "fields": "id,created_time,name",
        "limit": 100,
        "access_token": ACCESS_TOKEN,
    },
    timeout=30,
)

try:
    photos_data = response.json()
except ValueError:
    photos_data = {"raw_response": response.text}

print_test(
    "TEST 6 — PAGE PHOTOS",
    response.status_code,
    photos_data
)


if isinstance(photos_data, dict):
    photos = photos_data.get("data", [])

    found = False

    for photo in photos:
        if str(photo.get("id")) == OBJECT_ID:
            found = True
            print()
            print("✅ OBJECT FOUND IN PAGE PHOTOS")
            print(json.dumps(photo, ensure_ascii=False, indent=2))
            break

    if not found:
        print()
        print("⚠️ OBJECT NOT FOUND IN THE FIRST 100 PAGE PHOTOS.")


print()
print("=" * 70)
print("INVESTIGATION FINISHED")
print("=" * 70)

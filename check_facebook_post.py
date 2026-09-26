import os
import json
import requests

GRAPH_VERSION = "v26.0"
PHOTO_ID = "1061075956557715"

ACCESS_TOKEN = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")


def request_graph(path, params):
    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{path}"

    params = dict(params)
    params["access_token"] = ACCESS_TOKEN

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


def show(title, status, data):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)
    print(f"HTTP Status: {status}")
    print(json.dumps(data, ensure_ascii=False, indent=2))


print("=" * 70)
print("FACEBOOK PHOTO -> POST RELATIONSHIP TEST")
print("=" * 70)

print(f"Photo ID: {PHOTO_ID}")

if not ACCESS_TOKEN:
    print("❌ FACEBOOK_PAGE_ACCESS_TOKEN is missing.")
    raise SystemExit(1)


# =========================================================
# TEST 1
# Photo basic information
# =========================================================

status, data = request_graph(
    PHOTO_ID,
    {
        "fields": "id,created_time,name,from,link"
    }
)

show(
    "TEST 1 — PHOTO BASIC INFORMATION",
    status,
    data
)


# =========================================================
# TEST 2
# Try photo object fields that may expose the related post
# =========================================================

status, data = request_graph(
    PHOTO_ID,
    {
        "fields": "id,album"
    }
)

show(
    "TEST 2 — PHOTO ALBUM",
    status,
    data
)


# =========================================================
# TEST 3
# Ask for reactions/comments counts
# =========================================================

status, data = request_graph(
    PHOTO_ID,
    {
        "fields": "id,reactions.summary(true),comments.summary(true)"
    }
)

show(
    "TEST 3 — ENGAGEMENT",
    status,
    data
)


# =========================================================
# TEST 4
# Try sharedposts connection
# =========================================================

status, data = request_graph(
    f"{PHOTO_ID}/sharedposts",
    {
        "limit": "25"
    }
)

show(
    "TEST 4 — SHARED POSTS",
    status,
    data
)


# =========================================================
# TEST 5
# Try feed connection from the photo
# =========================================================

status, data = request_graph(
    f"{PHOTO_ID}/feed",
    {
        "limit": "25"
    }
)

show(
    "TEST 5 — PHOTO FEED CONNECTION",
    status,
    data
)


# =========================================================
# TEST 6
# Try Page published posts using the known Page ID
# =========================================================

PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")

if PAGE_ID:

    status, data = request_graph(
        f"{PAGE_ID}/published_posts",
        {
            "fields": "id,created_time",
            "limit": "25"
        }
    )

    show(
        "TEST 6 — PAGE PUBLISHED POSTS",
        status,
        data
    )


print()
print("=" * 70)
print("RELATIONSHIP TEST FINISHED")
print("=" * 70)

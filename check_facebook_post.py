import os
import json
import requests
from datetime import datetime, timezone

GRAPH_VERSION = "v26.0"

# الـPhoto ID الذي ظهر في سجل النشر
PHOTO_ID = "1061075956557715"

PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
ACCESS_TOKEN = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")


def graph_get(path, params=None):
    """
    GET request to Facebook Graph API.
    """
    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{path}"

    request_params = {
        "access_token": ACCESS_TOKEN
    }

    if params:
        request_params.update(params)

    response = requests.get(
        url,
        params=request_params,
        timeout=30
    )

    try:
        data = response.json()
    except ValueError:
        data = {
            "raw_response": response.text
        }

    return response.status_code, data


def print_result(title, status, data):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)
    print(f"HTTP Status: {status}")
    print(json.dumps(data, ensure_ascii=False, indent=2))


def parse_time(value):
    """
    Convert Facebook timestamp to datetime.
    """
    if not value:
        return None

    try:
        return datetime.strptime(
            value,
            "%Y-%m-%dT%H:%M:%S%z"
        )
    except ValueError:
        return None


print("=" * 70)
print("FACEBOOK PHOTO -> PUBLISHED POST DIAGNOSTIC")
print("=" * 70)

print(f"Page ID configured: {'YES' if PAGE_ID else 'NO'}")
print(f"Access Token configured: {'YES' if ACCESS_TOKEN else 'NO'}")
print(f"Photo ID: {PHOTO_ID}")


# =========================================================
# CONFIGURATION CHECK
# =========================================================

if not PAGE_ID:
    print()
    print("❌ FACEBOOK_PAGE_ID is missing.")
    raise SystemExit(1)

if not ACCESS_TOKEN:
    print()
    print("❌ FACEBOOK_PAGE_ACCESS_TOKEN is missing.")
    raise SystemExit(1)


# =========================================================
# TEST 1 — PHOTO OBJECT
# =========================================================

status, photo = graph_get(
    PHOTO_ID,
    {
        "fields": "id,created_time,name,from,album,link"
    }
)

print_result(
    "TEST 1 — PHOTO OBJECT",
    status,
    photo
)

if status != 200:
    print()
    print("❌ Could not read the Photo Object.")
    raise SystemExit(1)

photo_created_time = photo.get("created_time")

print()
print(f"Photo created_time: {photo_created_time}")


# =========================================================
# TEST 2 — FIND THE CORRESPONDING PUBLISHED PAGE POST
# =========================================================

print()
print("=" * 70)
print("TEST 2 — SEARCH PUBLISHED POSTS")
print("=" * 70)

status, published = graph_get(
    f"{PAGE_ID}/published_posts",
    {
        "fields": "id,created_time",
        "limit": "100"
    }
)

print(f"HTTP Status: {status}")

if status != 200:
    print(json.dumps(published, ensure_ascii=False, indent=2))

    print()
    print("❌ Could not read Page Published Posts.")
    raise SystemExit(1)

posts = published.get("data", [])

print(f"Published posts returned: {len(posts)}")

photo_time = parse_time(photo_created_time)

matched_post = None
closest_post = None
closest_difference = None


for post in posts:

    post_id = post.get("id")
    post_time_text = post.get("created_time")

    post_time = parse_time(post_time_text)

    if not post_time:
        continue

    # Exact timestamp match
    if photo_time and post_time == photo_time:
        matched_post = post
        break

    # Keep closest post as backup
    if photo_time:
        difference = abs(
            (post_time - photo_time).total_seconds()
        )

        if closest_difference is None or difference < closest_difference:
            closest_difference = difference
            closest_post = post


if matched_post:
    print()
    print("✅ MATCH FOUND")
    print()
    print(f"Photo ID : {PHOTO_ID}")
    print(f"Post ID  : {matched_post.get('id')}")
    print(f"Created  : {matched_post.get('created_time')}")

    POST_ID = matched_post.get("id")

else:
    print()
    print("⚠️ No exact timestamp match found.")

    if closest_post:
        print()
        print("Closest published post:")
        print(json.dumps(
            closest_post,
            ensure_ascii=False,
            indent=2
        ))

        print()
        print(
            f"Time difference: {closest_difference} seconds"
        )

    POST_ID = None


# =========================================================
# TEST 3 — INSPECT THE ACTUAL POST
# =========================================================

if POST_ID:

    status, post_data = graph_get(
        POST_ID,
        {
            "fields": "id,created_time,from,name"
        }
    )

    print_result(
        "TEST 3 — ACTUAL PUBLISHED POST",
        status,
        post_data
    )

else:

    print()
    print("=" * 70)
    print("TEST 3 — ACTUAL PUBLISHED POST")
    print("=" * 70)
    print("⚠️ Skipped because no matching Page Post was found.")


# =========================================================
# TEST 4 — TRY POST LINK
# =========================================================

if POST_ID:

    status, link_data = graph_get(
        POST_ID,
        {
            "fields": "id,link"
        }
    )

    print_result(
        "TEST 4 — ACTUAL POST LINK",
        status,
        link_data
    )


# =========================================================
# TEST 5 — TRY POST NAME / CONTENT
# =========================================================

if POST_ID:

    status, content_data = graph_get(
        POST_ID,
        {
            "fields": "id,name"
        }
    )

    print_result(
        "TEST 5 — ACTUAL POST CONTENT",
        status,
        content_data
    )


# =========================================================
# TEST 6 — VERIFY PHOTO IS ASSOCIATED WITH PAGE
# =========================================================

status, page_photos = graph_get(
    f"{PAGE_ID}/photos",
    {
        "fields": "id,created_time,name",
        "limit": "100"
    }
)

print_result(
    "TEST 6 — PAGE PHOTOS",
    status,
    page_photos
)

if status == 200:

    photo_found = False

    for item in page_photos.get("data", []):

        if str(item.get("id")) == PHOTO_ID:
            photo_found = True

            print()
            print("✅ TARGET PHOTO FOUND IN PAGE PHOTOS")
            print(
                json.dumps(
                    item,
                    ensure_ascii=False,
                    indent=2
                )
            )

            break

    if not photo_found:

        print()
        print(
            "⚠️ Target Photo ID was not found "
            "in the first 100 Page photos."
        )


# =========================================================
# FINAL SUMMARY
# =========================================================

print()
print("=" * 70)
print("FINAL DIAGNOSTIC SUMMARY")
print("=" * 70)

print(f"Photo ID: {PHOTO_ID}")

if POST_ID:
    print(f"Published Post ID: {POST_ID}")
    print("✅ Facebook created a published Page post for this photo.")
else:
    print("⚠️ No corresponding Published Post ID was detected.")

print()
print("No publishing operation was performed.")
print("No Facebook post was created by this diagnostic.")
print("The diagnostic only performed GET requests.")

print()
print("=" * 70)
print("DIAGNOSTIC FINISHED")
print("=" * 70)

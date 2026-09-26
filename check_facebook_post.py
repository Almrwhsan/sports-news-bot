import os
import json
import requests

GRAPH_VERSION = "v26.0"
POST_ID = "1061075956557715"

PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
ACCESS_TOKEN = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")


def graph_get(object_id, fields):
    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{object_id}"

    response = requests.get(
        url,
        params={
            "fields": fields,
            "access_token": ACCESS_TOKEN,
        },
        timeout=30,
    )

    try:
        data = response.json()
    except ValueError:
        data = {
            "raw_response": response.text,
            "http_status": response.status_code,
        }

    return response.status_code, data


print("=" * 70)
print("FACEBOOK POST DIAGNOSTIC TEST")
print("=" * 70)

print(f"Page ID: {PAGE_ID}")
print(f"Object/Post ID being tested: {POST_ID}")
print()

if not PAGE_ID:
    print("❌ FACEBOOK_PAGE_ID is missing.")
    raise SystemExit(1)

if not ACCESS_TOKEN:
    print("❌ FACEBOOK_PAGE_ACCESS_TOKEN is missing.")
    raise SystemExit(1)


# ---------------------------------------------------------
# TEST 1 — Basic object information
# ---------------------------------------------------------

print("TEST 1 — BASIC OBJECT INFORMATION")
print("-" * 70)

status, data = graph_get(
    POST_ID,
    "id,created_time,permalink_url,message"
)

print(f"HTTP Status: {status}")
print(json.dumps(data, ensure_ascii=False, indent=2))

print()


# ---------------------------------------------------------
# TEST 2 — Check whether this object has a post_id
# ---------------------------------------------------------

print("TEST 2 — CHECK FOR POST ID")
print("-" * 70)

status, data = graph_get(
    POST_ID,
    "id,post_id,created_time,permalink_url"
)

print(f"HTTP Status: {status}")
print(json.dumps(data, ensure_ascii=False, indent=2))

actual_post_id = data.get("post_id") if isinstance(data, dict) else None

if actual_post_id:
    print()
    print(f"✅ Facebook returned a separate post_id:")
    print(actual_post_id)
else:
    print()
    print("ℹ️ No separate post_id was returned.")


# ---------------------------------------------------------
# TEST 3 — Check publication state
# ---------------------------------------------------------

print()
print("TEST 3 — PUBLICATION STATE")
print("-" * 70)

status, data = graph_get(
    POST_ID,
    "id,is_published,created_time,permalink_url"
)

print(f"HTTP Status: {status}")
print(json.dumps(data, ensure_ascii=False, indent=2))


# ---------------------------------------------------------
# TEST 4 — If a separate post_id exists, inspect it
# ---------------------------------------------------------

if actual_post_id and actual_post_id != POST_ID:

    print()
    print("TEST 4 — INSPECT ACTUAL POST ID")
    print("-" * 70)

    status, data = graph_get(
        actual_post_id,
        "id,created_time,permalink_url,message,is_published"
    )

    print(f"Actual Post ID: {actual_post_id}")
    print(f"HTTP Status: {status}")
    print(json.dumps(data, ensure_ascii=False, indent=2))


# ---------------------------------------------------------
# TEST 5 — Try finding the object in the Page feed
# ---------------------------------------------------------

print()
print("TEST 5 — PAGE FEED CHECK")
print("-" * 70)

feed_url = f"https://graph.facebook.com/{GRAPH_VERSION}/{PAGE_ID}/feed"

try:
    response = requests.get(
        feed_url,
        params={
            "fields": "id,created_time,permalink_url,message",
            "limit": 25,
            "access_token": ACCESS_TOKEN,
        },
        timeout=30,
    )

    print(f"HTTP Status: {response.status_code}")

    try:
        feed_data = response.json()
    except ValueError:
        feed_data = {"raw_response": response.text}

    print(json.dumps(feed_data, ensure_ascii=False, indent=2))

    if isinstance(feed_data, dict):
        posts = feed_data.get("data", [])

        found = False

        for post in posts:
            post_id = str(post.get("id", ""))

            if (
                post_id == POST_ID
                or post_id == str(actual_post_id or "")
            ):
                found = True
                print()
                print("✅ TEST POST FOUND IN PAGE FEED")

        if not found:
            print()
            print("⚠️ TEST POST WAS NOT FOUND IN THE FIRST 25 FEED ITEMS.")

except requests.RequestException as error:
    print(f"❌ Feed request failed: {error}")


print()
print("=" * 70)
print("DIAGNOSTIC TEST FINISHED")
print("=" * 70)

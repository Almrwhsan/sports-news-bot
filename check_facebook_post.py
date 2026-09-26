import os
import json
import requests

GRAPH_VERSION = "v26.0"
OBJECT_ID = "1061075956557715"

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
        data = {
            "raw_response": response.text
        }

    return response.status_code, data


print("=" * 70)
print("FACEBOOK OBJECT TYPE DIAGNOSTIC")
print("=" * 70)

print(f"Object ID: {OBJECT_ID}")
print()

if not ACCESS_TOKEN:
    print("❌ FACEBOOK_PAGE_ACCESS_TOKEN is missing.")
    raise SystemExit(1)


# ---------------------------------------------------------
# TEST 1
# Ask Facebook for the object without fields
# ---------------------------------------------------------

print("TEST 1 — RAW OBJECT")
print("-" * 70)

status, data = graph_get(OBJECT_ID)

print(f"HTTP Status: {status}")
print(json.dumps(data, ensure_ascii=False, indent=2))

print()


# ---------------------------------------------------------
# TEST 2
# Only universally basic fields
# ---------------------------------------------------------

print("TEST 2 — BASIC FIELDS")
print("-" * 70)

status, data = graph_get(
    OBJECT_ID,
    "id,created_time"
)

print(f"HTTP Status: {status}")
print(json.dumps(data, ensure_ascii=False, indent=2))

print()


# ---------------------------------------------------------
# TEST 3
# Try message only
# ---------------------------------------------------------

print("TEST 3 — MESSAGE")
print("-" * 70)

status, data = graph_get(
    OBJECT_ID,
    "message"
)

print(f"HTTP Status: {status}")
print(json.dumps(data, ensure_ascii=False, indent=2))

print()


# ---------------------------------------------------------
# TEST 4
# Try attachments
# ---------------------------------------------------------

print("TEST 4 — ATTACHMENTS")
print("-" * 70)

status, data = graph_get(
    OBJECT_ID,
    "attachments"
)

print(f"HTTP Status: {status}")
print(json.dumps(data, ensure_ascii=False, indent=2))

print()


# ---------------------------------------------------------
# TEST 5
# Ask Graph API what fields are available
# ---------------------------------------------------------

print("TEST 5 — METADATA")
print("-" * 70)

status, data = graph_get(
    OBJECT_ID,
    "id"
)

print(f"HTTP Status: {status}")
print(json.dumps(data, ensure_ascii=False, indent=2))

print()
print("=" * 70)
print("DIAGNOSTIC FINISHED")
print("=" * 70)

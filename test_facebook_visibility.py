import os
import sys
import time
from datetime import datetime, timezone

import requests
from PIL import Image, ImageDraw, ImageFont


FACEBOOK_GRAPH_VERSION = "v26.0"

PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
ACCESS_TOKEN = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")

TEST_CAPTION = """🧪 اختبار نشر تلقائي — نبض مدريد

هذا منشور اختبار فقط للتحقق من ظهور المنشورات التي يتم نشرها عبر Facebook Graph API.

يرجى تجاهل هذا المنشور.
"""


def fail(message):
    print(f"❌ {message}")
    sys.exit(1)


def check_configuration():
    print("🔧 Checking Facebook configuration...")

    if not PAGE_ID:
        fail("FACEBOOK_PAGE_ID is missing.")

    if not ACCESS_TOKEN:
        fail("FACEBOOK_PAGE_ACCESS_TOKEN is missing.")

    print(f"✅ Page ID: {PAGE_ID}")
    print("✅ Access Token: configured")


def create_test_image():
    print("\n🖼️ Creating test image...")

    width = 1080
    height = 1080

    image = Image.new("RGB", (width, height), (35, 15, 15))
    draw = ImageDraw.Draw(image)

    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    ]

    font = None

    for path in font_paths:
        if os.path.isfile(path):
            font = ImageFont.truetype(path, 48)
            break

    if font is None:
        font = ImageFont.load_default()

    title = "NABD MADRID"
    subtitle = "FACEBOOK VISIBILITY TEST"

    title_box = draw.textbbox((0, 0), title, font=font)
    subtitle_box = draw.textbbox((0, 0), subtitle, font=font)

    title_width = title_box[2] - title_box[0]
    subtitle_width = subtitle_box[2] - subtitle_box[0]

    draw.text(
        ((width - title_width) / 2, 390),
        title,
        fill=(255, 215, 0),
        font=font,
    )

    draw.text(
        ((width - subtitle_width) / 2, 500),
        subtitle,
        fill=(255, 255, 255),
        font=font,
    )

    draw.rectangle(
        (120, 650, 960, 660),
        fill=(255, 215, 0),
    )

    image_path = "facebook_visibility_test.jpg"
    image.save(image_path, "JPEG", quality=95)

    print(f"✅ Test image created: {image_path}")

    return image_path


def publish_test_image(image_path):
    print("\n📤 Publishing test image to Facebook...")

    url = (
        f"https://graph.facebook.com/"
        f"{FACEBOOK_GRAPH_VERSION}/"
        f"{PAGE_ID}/photos"
    )

    payload = {
        "caption": TEST_CAPTION,
        "published": "true",
        "access_token": ACCESS_TOKEN,
    }

    started_at = datetime.now(timezone.utc)

    try:
        with open(image_path, "rb") as image_file:
            response = requests.post(
                url,
                files={"source": image_file},
                data=payload,
                timeout=120,
            )
    except requests.RequestException as error:
        fail(f"Facebook request failed: {error}")

    try:
        data = response.json()
    except ValueError:
        fail(
            "Facebook returned a non-JSON response.\n"
            f"HTTP status: {response.status_code}\n"
            f"Response: {response.text[:1000]}"
        )

    print(f"HTTP status: {response.status_code}")

    if not response.ok:
        print("Facebook response:")
        print(data)
        fail("Facebook rejected the test publication.")

    if "error" in data:
        print("Facebook error:")
        print(data["error"])
        fail("Facebook returned an API error.")

    photo_id = data.get("id")

    if not photo_id:
        print("Unexpected Facebook response:")
        print(data)
        fail("Facebook did not return a Photo ID.")

    print("✅ Image publication request succeeded.")
    print(f"📸 Photo ID: {photo_id}")

    return photo_id, started_at


def get_photo_details(photo_id):
    print("\n🔎 Reading the created Photo object...")

    url = (
        f"https://graph.facebook.com/"
        f"{FACEBOOK_GRAPH_VERSION}/"
        f"{photo_id}"
    )

    params = {
        "fields": "id,created_time,name,from,link,album",
        "access_token": ACCESS_TOKEN,
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=30,
        )
    except requests.RequestException as error:
        print(f"⚠️ Could not read Photo object: {error}")
        return None

    try:
        data = response.json()
    except ValueError:
        print("⚠️ Photo object returned invalid JSON.")
        return None

    if not response.ok:
        print("⚠️ Could not read Photo object:")
        print(data)
        return None

    print("✅ Photo object exists.")

    created_time = data.get("created_time")
    link = data.get("link")

    if created_time:
        print(f"🕒 Photo created time: {created_time}")

    if link:
        print(f"🔗 Photo link: {link}")

    return data


def get_published_posts():
    print("\n🔎 Looking for the corresponding published Page post...")

    url = (
        f"https://graph.facebook.com/"
        f"{FACEBOOK_GRAPH_VERSION}/"
        f"{PAGE_ID}/published_posts"
    )

    params = {
        "fields": "id,created_time",
        "limit": 100,
        "access_token": ACCESS_TOKEN,
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=30,
        )
    except requests.RequestException as error:
        print(f"⚠️ Could not read published posts: {error}")
        return []

    try:
        data = response.json()
    except ValueError:
        print("⚠️ published_posts returned invalid JSON.")
        return []

    if not response.ok:
        print("⚠️ Could not read published posts:")
        print(data)
        return []

    return data.get("data", [])


def find_matching_page_post(photo_data, started_at):
    print("\n🔎 Matching Photo ID with the actual Page Post ID...")

    photo_created_time = None

    if photo_data:
        photo_created_time = photo_data.get("created_time")

    posts = get_published_posts()

    if not posts:
        print("⚠️ No published posts were returned.")
        return None

    target_time = None

    if photo_created_time:
        try:
            target_time = datetime.fromisoformat(
                photo_created_time.replace("Z", "+00:00")
            )
        except ValueError:
            target_time = None

    if target_time is None:
        target_time = started_at

    best_post = None
    best_difference = None

    for post in posts:
        post_id = post.get("id")
        created_time = post.get("created_time")

        if not post_id or not created_time:
            continue

        try:
            post_time = datetime.fromisoformat(
                created_time.replace("Z", "+00:00")
            )
        except ValueError:
            continue

        difference = abs(
            (post_time - target_time).total_seconds()
        )

        if difference <= 60:
            if best_difference is None or difference < best_difference:
                best_difference = difference
                best_post = post

    if best_post:
        print("✅ Matching published Page post found.")
        print(f"📝 Page Post ID: {best_post['id']}")
        print(f"🕒 Post created time: {best_post['created_time']}")

        return best_post

    print("⚠️ Could not automatically match the Photo to a Page Post.")
    return None


def main():
    print("=" * 70)
    print("FACEBOOK VISIBILITY TEST")
    print("=" * 70)

    check_configuration()

    image_path = create_test_image()

    photo_id, started_at = publish_test_image(image_path)

    time.sleep(3)

    photo_data = get_photo_details(photo_id)

    page_post = find_matching_page_post(
        photo_data=photo_data,
        started_at=started_at,
    )

    print("\n" + "=" * 70)
    print("FINAL TEST RESULT")
    print("=" * 70)

    print(f"Photo ID: {photo_id}")

    if page_post:
        print(f"Page Post ID: {page_post['id']}")
        print("Published Page Post: YES")
    else:
        print("Page Post ID: NOT FOUND")
        print("Published Page Post: NOT CONFIRMED")

    if photo_data and photo_data.get("link"):
        print(f"Photo URL: {photo_data['link']}")

    print("\n⚠️ IMPORTANT:")
    print("The Graph API result confirms whether Facebook created")
    print("the published object. It does NOT prove that another")
    print("Facebook user can see it publicly.")
    print("\nOpen the Photo URL from another Facebook account")
    print("or an incognito/private browser window to test")
    print("actual public visibility.")

    print("=" * 70)


if __name__ == "__main__":
    main()

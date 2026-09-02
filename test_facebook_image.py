import os
import requests

from image_generator import generate_news_image


# ============================================================
# إعدادات
# ============================================================

GRAPH_API_VERSION = "v26.0"

PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
PAGE_ACCESS_TOKEN = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")

OUTPUT_DIR = "generated_images"

TEST_TITLE = "ريال مدريد يستعد لمواجهة جديدة في الموسم"


# ============================================================
# التحقق من إعدادات Facebook
# ============================================================

def check_facebook_config():

    print("===================================")
    print("   FACEBOOK IMAGE PUBLISH TEST")
    print("===================================")

    print()

    if not PAGE_ID:
        print("❌ FACEBOOK_PAGE_ID is missing")
        return False

    if not PAGE_ACCESS_TOKEN:
        print("❌ FACEBOOK_PAGE_ACCESS_TOKEN is missing")
        return False

    print("✅ Facebook Page ID found")
    print("✅ Facebook Page Access Token found")

    return True


# ============================================================
# إنشاء صورة اختبار
# ============================================================

def create_test_image():

    print()
    print("===================================")
    print("STEP 1 - CREATE TEST IMAGE")
    print("===================================")

    try:

        image_path = generate_news_image(
            title=TEST_TITLE,
            category="football",
            image_path=None
        )

    except Exception as error:

        print(
            "❌ Image generation failed:",
            error
        )

        return None

    if not image_path:
        print("❌ No image path returned")
        return None

    if not os.path.exists(image_path):
        print(
            "❌ Image does not exist:",
            image_path
        )
        return None

    print()
    print("✅ Test image created")
    print("Image:", image_path)

    return image_path


# ============================================================
# نشر الصورة على Facebook
# ============================================================

def publish_image(image_path):

    print()
    print("===================================")
    print("STEP 2 - PUBLISH IMAGE TO FACEBOOK")
    print("===================================")

    url = (
        f"https://graph.facebook.com/"
        f"{GRAPH_API_VERSION}/"
        f"{PAGE_ID}/photos"
    )

    caption = (
        f"🚨 {TEST_TITLE}\n\n"
        "📰 اختبار نشر صورة خبر رياضي.\n\n"
        "🏷️ كرة القدم\n\n"
        "📍 نبض مدريد"
    )

    try:

        with open(
            image_path,
            "rb"
        ) as image_file:

            response = requests.post(
                url,
                data={
                    "caption": caption,
                    "access_token": PAGE_ACCESS_TOKEN,
                },
                files={
                    "source": image_file,
                },
                timeout=60,
            )

        print()
        print(
            "Facebook HTTP status:",
            response.status_code
        )

        try:
            data = response.json()
        except Exception:
            data = {}

        if response.ok:

            post_id = (
                data.get("post_id")
                or data.get("id")
                or data.get("post_id")
            )

            print()
            print("✅ FACEBOOK IMAGE PUBLISHED")

            if post_id:
                print(
                    "Post ID:",
                    post_id
                )

            return True

        print()
        print("❌ FACEBOOK IMAGE PUBLISH FAILED")

        error_data = data.get("error")

        if error_data:

            print(
                "Error message:",
                error_data.get(
                    "message",
                    "Unknown error"
                )
            )

            print(
                "Error type:",
                error_data.get(
                    "type",
                    "Unknown"
                )
            )

            print(
                "Error code:",
                error_data.get(
                    "code",
                    "Unknown"
                )
            )

        else:

            print(
                "Response:",
                response.text[:1000]
            )

        return False

    except Exception as error:

        print()
        print(
            "❌ Facebook request error:",
            error
        )

        return False


# ============================================================
# البرنامج الرئيسي
# ============================================================

def main():

    if not check_facebook_config():

        raise SystemExit(1)

    image_path = create_test_image()

    if not image_path:

        raise SystemExit(1)

    success = publish_image(
        image_path
    )

    print()
    print("===================================")
    print("       FACEBOOK IMAGE SUMMARY")
    print("===================================")

    print()

    if success:

        print(
            "✅ FACEBOOK IMAGE PIPELINE WORKS"
        )

    else:

        print(
            "❌ FACEBOOK IMAGE PIPELINE FAILED"
        )

        raise SystemExit(1)

    print()
    print("===================================")
    print("   FACEBOOK IMAGE TEST END")
    print("===================================")


if __name__ == "__main__":

    main()

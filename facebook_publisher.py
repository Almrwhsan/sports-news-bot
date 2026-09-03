import os
import requests


# ============================================================
# إعدادات Facebook
# ============================================================

FACEBOOK_GRAPH_VERSION = "v26.0"

FACEBOOK_PAGE_ID = os.getenv(
    "FACEBOOK_PAGE_ID"
)

FACEBOOK_PAGE_ACCESS_TOKEN = os.getenv(
    "FACEBOOK_PAGE_ACCESS_TOKEN"
)

FACEBOOK_ENABLED = os.getenv(
    "FACEBOOK_ENABLED",
    "false"
).lower() == "true"


# ============================================================
# التحقق من إعداد Facebook
# ============================================================

def is_facebook_configured():

    return bool(
        FACEBOOK_PAGE_ID
        and FACEBOOK_PAGE_ACCESS_TOKEN
    )


# ============================================================
# نشر منشور نصي على الصفحة
# ============================================================

def publish_text_post(message):

    if not FACEBOOK_ENABLED:

        return {
            "success": False,
            "published": False,
            "post_id": None,
            "error": "Facebook publishing is disabled."
        }

    if not is_facebook_configured():

        return {
            "success": False,
            "published": False,
            "post_id": None,
            "error": "Facebook is not configured."
        }

    url = (
        f"https://graph.facebook.com/"
        f"{FACEBOOK_GRAPH_VERSION}/"
        f"{FACEBOOK_PAGE_ID}/feed"
    )

    payload = {
        "message": message,
        "access_token": FACEBOOK_PAGE_ACCESS_TOKEN,
    }

    try:

        response = requests.post(
            url,
            data=payload,
            timeout=30
        )

        data = response.json()

    except requests.RequestException as error:

        return {
            "success": False,
            "published": False,
            "post_id": None,
            "error": str(error)
        }

    except ValueError:

        return {
            "success": False,
            "published": False,
            "post_id": None,
            "error": "Invalid JSON response from Facebook."
        }

    if response.ok and "id" in data:

        return {
            "success": True,
            "published": True,
            "post_id": data["id"],
            "error": None
        }

    return {
        "success": False,
        "published": False,
        "post_id": None,
        "error": data.get(
            "error",
            data
        )
    }


# ============================================================
# نشر صورة + نص على الصفحة
# ============================================================

def publish_image_post(image_path, caption):

    if not FACEBOOK_ENABLED:

        return {
            "success": False,
            "published": False,
            "post_id": None,
            "error": "Facebook publishing is disabled."
        }

    if not is_facebook_configured():

        return {
            "success": False,
            "published": False,
            "post_id": None,
            "error": "Facebook is not configured."
        }

    if not image_path:

        return {
            "success": False,
            "published": False,
            "post_id": None,
            "error": "Image path is empty."
        }

    if not os.path.isfile(image_path):

        return {
            "success": False,
            "published": False,
            "post_id": None,
            "error": f"Image file not found: {image_path}"
        }

    url = (
        f"https://graph.facebook.com/"
        f"{FACEBOOK_GRAPH_VERSION}/"
        f"{FACEBOOK_PAGE_ID}/photos"
    )

    try:

        with open(
            image_path,
            "rb"
        ) as image_file:

            files = {
                "source": image_file
            }

            payload = {
                "caption": caption,
                "access_token": FACEBOOK_PAGE_ACCESS_TOKEN,
            }

            response = requests.post(
                url,
                files=files,
                data=payload,
                timeout=120
            )

        data = response.json()

    except requests.RequestException as error:

        return {
            "success": False,
            "published": False,
            "post_id": None,
            "error": str(error)
        }

    except ValueError:

        return {
            "success": False,
            "published": False,
            "post_id": None,
            "error": "Invalid JSON response from Facebook."
        }

    if response.ok and "id" in data:

        return {
            "success": True,
            "published": True,
            "post_id": data["id"],
            "error": None
        }

    return {
        "success": False,
        "published": False,
        "post_id": None,
        "error": data.get(
            "error",
            data
        )
    }


# ============================================================
# النشر النهائي
# ============================================================

def publish_post(
    message,
    image_path=None
):

    # --------------------------------------------------------
    # إذا توجد صورة
    # --------------------------------------------------------

    if image_path:

        print()
        print(
            f"📸 Image path: {image_path}"
        )

        result = publish_image_post(
            image_path=image_path,
            caption=message
        )

        if result.get("success"):

            print(
                "✅ Image published successfully."
            )

            return result

        # ----------------------------------------------------
        # إذا فشل نشر الصورة
        # ----------------------------------------------------

        print(
            "⚠️ Image publishing failed."
        )

        print(
            "Facebook image error:",
            result.get("error")
        )

        print(
            "📝 Falling back to text-only post..."
        )

    # --------------------------------------------------------
    # لا توجد صورة أو فشل نشر الصورة
    # --------------------------------------------------------

    return publish_text_post(
        message
    )

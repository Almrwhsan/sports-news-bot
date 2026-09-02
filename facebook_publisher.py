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

    # --------------------------------------------------------
    # مفتاح تشغيل / إيقاف النشر
    # --------------------------------------------------------

    if not FACEBOOK_ENABLED:

        return {
            "success": False,
            "published": False,
            "post_id": None,
            "error": "Facebook publishing is disabled."
        }

    # --------------------------------------------------------
    # التحقق من الإعدادات
    # --------------------------------------------------------

    if not is_facebook_configured():

        return {
            "success": False,
            "published": False,
            "post_id": None,
            "error": "Facebook is not configured."
        }

    # --------------------------------------------------------
    # Facebook Graph API
    # --------------------------------------------------------

    url = (
        f"https://graph.facebook.com/"
        f"{FACEBOOK_GRAPH_VERSION}/"
        f"{FACEBOOK_PAGE_ID}/feed"
    )

    payload = {
        "message": message,
        "access_token": FACEBOOK_PAGE_ACCESS_TOKEN,
    }

    # --------------------------------------------------------
    # إرسال الطلب
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # نجاح النشر
    # --------------------------------------------------------

    if response.ok and "id" in data:

        return {
            "success": True,
            "published": True,
            "post_id": data["id"],
            "error": None
        }

    # --------------------------------------------------------
    # فشل النشر
    # --------------------------------------------------------

    return {
        "success": False,
        "published": False,
        "post_id": None,
        "error": data.get(
            "error",
            data
        )
    }

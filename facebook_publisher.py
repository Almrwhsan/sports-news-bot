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


# ============================================================
# حالة النشر
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

    if not is_facebook_configured():

        return {
            "success": False,
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
            "error": str(error)
        }

    except ValueError:

        return {
            "success": False,
            "error": "Invalid JSON response from Facebook."
        }

    # --------------------------------------------------------
    # نجاح
    # --------------------------------------------------------

    if response.ok and "id" in data:

        return {
            "success": True,
            "post_id": data["id"]
        }

    # --------------------------------------------------------
    # فشل
    # --------------------------------------------------------

    return {
        "success": False,
        "error": data.get(
            "error",
            data
        )
    }

#!/usr/bin/env python3

"""
Live Stream Manager
-------------------

إدارة بث HLS / M3U8 مع:
1. قراءة إعدادات البث من config.json
2. التحقق من رابط HLS
3. التعامل مع User-Agent و Referer المصرح بهما
4. إنشاء ملف M3U
5. النشر الاختياري على Facebook Page

ملاحظة:
هذا المشروع لا يتجاوز DRM أو تسجيل الدخول أو أنظمة التحكم
بالوصول. Headers تستخدم فقط عندما تكون مصرحًا باستخدامها
من مزود البث.
"""

import json
import sys
from pathlib import Path
from urllib.parse import urlparse

import requests


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

CONFIG_FILE = BASE_DIR / "config.json"


# ============================================================
# CONFIGURATION
# ============================================================

def load_config():
    """
    قراءة ملف config.json.
    """

    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {CONFIG_FILE}"
        )

    with CONFIG_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


# ============================================================
# VALIDATION
# ============================================================

def validate_stream_url(stream_url):
    """
    التأكد من أن الرابط صالح من ناحية البنية الأساسية.
    """

    if not stream_url:
        raise ValueError("stream_url is empty.")

    parsed = urlparse(stream_url)

    if parsed.scheme not in ("http", "https"):
        raise ValueError(
            "stream_url must start with http:// or https://"
        )

    return True


def get_stream_config(config):
    """
    استخراج إعدادات البث من config.json.
    """

    stream = config.get("stream", {})

    stream_url = str(
        stream.get("stream_url", "")
    ).strip()

    event_title = str(
        stream.get("event_title", "Live Stream")
    ).strip()

    enabled = bool(
        stream.get("enabled", False)
    )

    status = str(
        stream.get("status", "unknown")
    ).strip()

    validate_stream_url(stream_url)

    if not enabled:
        raise ValueError(
            "Stream is disabled in config.json."
        )

    return {
        "stream_url": stream_url,
        "event_title": event_title,
        "status": status
    }


# ============================================================
# HEADERS
# ============================================================

def build_headers(config):
    """
    تجهيز HTTP Headers.

    يتم استخدام Referer و User-Agent فقط إذا تم وضعهما
    في config.json.

    لا نقوم بإنشاء Cookies أو Authorization أو بيانات
    دخول من تلقاء أنفسنا.
    """

    header_config = config.get("headers", {})

    headers = {}

    user_agent = str(
        header_config.get("User-Agent", "")
    ).strip()

    referer = str(
        header_config.get("Referer", "")
    ).strip()

    if user_agent:
        headers["User-Agent"] = user_agent

    if referer:
        headers["Referer"] = referer

    return headers


# ============================================================
# STREAM CHECK
# ============================================================

def check_stream(stream_url, headers):
    """
    اختبار الوصول الأساسي إلى رابط HLS.

    هذا لا يعني أن البث سيعمل في كل مشغل،
    لكنه يعطينا مؤشرًا أوليًا على أن الرابط متاح.
    """

    print()
    print("Checking HLS stream...")
    print(stream_url)

    try:

        response = requests.get(
            stream_url,
            headers=headers,
            timeout=15,
            stream=True
        )

        print(
            f"HTTP Status: {response.status_code}"
        )

        content_type = response.headers.get(
            "Content-Type",
            ""
        )

        print(
            f"Content-Type: {content_type}"
        )

        if response.status_code == 200:

            print("HLS source is reachable.")

            return True

        print(
            "HLS source returned an unexpected HTTP status."
        )

        return False

    except requests.RequestException as error:

        print(
            f"Stream check failed: {error}"
        )

        return False


# ============================================================
# M3U GENERATION
# ============================================================

def generate_playlist(config, stream):
    """
    إنشاء ملف live_playlist.m3u.

    يتم وضع:
    - اسم الحدث
    - User-Agent
    - Referer
    - رابط HLS
    """

    output_config = config.get(
        "output",
        {}
    )

    playlist_name = str(
        output_config.get(
            "playlist_file",
            "live_playlist.m3u"
        )
    ).strip()

    if not playlist_name:
        playlist_name = "live_playlist.m3u"

    output_file = BASE_DIR / playlist_name

    headers = build_headers(config)

    lines = [
        "#EXTM3U",
        f"#EXTINF:-1,{stream['event_title']}"
    ]

    # VLC option
    if headers.get("User-Agent"):

        lines.append(
            "#EXTVLCOPT:http-user-agent="
            + headers["User-Agent"]
        )

    # VLC option
    if headers.get("Referer"):

        lines.append(
            "#EXTVLCOPT:http-referrer="
            + headers["Referer"]
        )

    lines.append(
        stream["stream_url"]
    )

    lines.append("")

    output_file.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )

    print()
    print("Playlist generated:")
    print(output_file)

    return output_file


# ============================================================
# FACEBOOK
# ============================================================

def publish_to_facebook(config, stream, playlist_url=None):
    """
    نشر منشور على صفحة Facebook.

    ملاحظة:
    هذه الوظيفة تنشر معلومات الحدث والرابط الذي نحدده،
    ولا تقوم تلقائيًا بتحويل HLS إلى Facebook Live.

    بث Facebook Live الحقيقي يحتاج مرحلة Streaming/RTMPS
    منفصلة مثل FFmpeg أو Streaming Server.
    """

    facebook = config.get(
        "facebook",
        {}
    )

    enabled = bool(
        facebook.get("enabled", False)
    )

    if not enabled:

        print()
        print(
            "Facebook publishing is disabled."
        )

        return None

    page_id = str(
        facebook.get(
            "page_id",
            ""
        )
    ).strip()

    access_token = str(
        facebook.get(
            "page_access_token",
            ""
        )
    ).strip()

    post_message = bool(
        facebook.get(
            "post_message",
            True
        )
    )

    if not page_id:
        raise ValueError(
            "Facebook Page ID is missing."
        )

    if not access_token:
        raise ValueError(
            "Facebook Page Access Token is missing."
        )

    message_parts = [
        f"🔴 بث مباشر",
        "",
        f"🏟️ {stream['event_title']}",
        "",
        f"📡 الحالة: {stream['status']}"
    ]

    if playlist_url:
        message_parts.extend([
            "",
            f"🔗 المشاهدة:",
            playlist_url
        ])

    message = "\n".join(
        message_parts
    )

    if not post_message:

        print(
            "Facebook post_message is disabled."
        )

        return None

    graph_url = (
        f"https://graph.facebook.com/"
        f"v26.0/{page_id}/feed"
    )

    payload = {
        "message": message,
        "access_token": access_token
    }

    print()
    print("Publishing Facebook post...")

    response = requests.post(
        graph_url,
        data=payload,
        timeout=30
    )

    try:
        result = response.json()
    except ValueError:
        result = {
            "raw_response": response.text
        }

    if response.ok and "id" in result:

        print(
            f"Facebook post created: {result['id']}"
        )

        return result

    print(
        "Facebook publishing failed."
    )

    print(result)

    return None


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("LIVE STREAM MANAGER")
    print("=" * 60)

    try:

        # ---------------------------------------------
        # 1. Load configuration
        # ---------------------------------------------

        config = load_config()

        # ---------------------------------------------
        # 2. Read stream configuration
        # ---------------------------------------------

        stream = get_stream_config(
            config
        )

        print()
        print(
            f"Event : {stream['event_title']}"
        )

        print(
            f"Status: {stream['status']}"
        )

        print(
            f"URL   : {stream['stream_url']}"
        )

        # ---------------------------------------------
        # 3. Build headers
        # ---------------------------------------------

        headers = build_headers(
            config
        )

        print()
        print(
            "Configured headers:"
        )

        for key in headers:

            # لا نطبع قيم حساسة
            print(
                f"  - {key}"
            )

        # ---------------------------------------------
        # 4. Check stream
        # ---------------------------------------------

        stream_available = check_stream(
            stream["stream_url"],
            headers
        )

        if not stream_available:

            print()
            print(
                "Warning: HLS source could not be verified."
            )

        # ---------------------------------------------
        # 5. Generate M3U playlist
        # ---------------------------------------------

        playlist_file = generate_playlist(
            config,
            stream
        )

        # ---------------------------------------------
        # 6. Facebook
        # ---------------------------------------------

        publish_to_facebook(
            config,
            stream
        )

        # ---------------------------------------------
        # 7. Finished
        # ---------------------------------------------

        print()
        print("=" * 60)
        print("DONE")
        print("=" * 60)

        print(
            f"Playlist: {playlist_file}"
        )

    except Exception as error:

        print()
        print("=" * 60)
        print("ERROR")
        print("=" * 60)

        print(error)

        sys.exit(1)


if __name__ == "__main__":
    main()

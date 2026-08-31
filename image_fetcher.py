import os
import re
import requests


# ============================================================
# إعدادات
# ============================================================

IMAGE_DIR = "news_images"

COMMONS_API = "https://commons.wikimedia.org/w/api.php"

USER_AGENT = (
    "SportsNewsBot/1.0 "
    "(football news image fetcher)"
)


# ============================================================
# تنظيف اسم الملف
# ============================================================

def safe_filename(text):

    text = str(text)

    text = re.sub(
        r'[\\/*?:"<>|]',
        "",
        text
    )

    text = re.sub(
        r"\s+",
        "_",
        text
    )

    text = text[:80]

    if not text:
        text = "football_image"

    return text


# ============================================================
# البحث في Wikimedia Commons
# ============================================================

def search_commons(query):

    print()
    print("Searching Wikimedia Commons...")
    print("Query:", query)

    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": 6,
        "gsrlimit": 10,
        "prop": "imageinfo",
        "iiprop": "url|mime|size|extmetadata",
        "iiurlwidth": 1200,
        "format": "json",
    }

    headers = {
        "User-Agent": USER_AGENT
    }

    try:

        response = requests.get(
            COMMONS_API,
            params=params,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        pages = (
            data
            .get("query", {})
            .get("pages", {})
        )

        results = []

        for page in pages.values():

            imageinfo = page.get(
                "imageinfo",
                []
            )

            if not imageinfo:
                continue

            info = imageinfo[0]

            mime = info.get(
                "mime",
                ""
            )

            if not mime.startswith("image/"):
                continue

            metadata = info.get(
                "extmetadata",
                {}
            )

            license_name = (
                metadata
                .get("LicenseShortName", {})
                .get("value", "")
            )

            artist = (
                metadata
                .get("Artist", {})
                .get("value", "")
            )

            description_url = (
                "https://commons.wikimedia.org/wiki/"
                + page.get("title", "").replace(
                    " ",
                    "_"
                )
            )

            results.append({
                "title": page.get(
                    "title",
                    ""
                ),
                "image_url": info.get(
                    "thumburl",
                    info.get("url", "")
                ),
                "original_url": info.get(
                    "url",
                    ""
                ),
                "license": license_name,
                "artist": artist,
                "source_url": description_url,
            })

        print(
            "Images found:",
            len(results)
        )

        return results

    except Exception as error:

        print(
            "Commons search error:",
            error
        )

        return []


# ============================================================
# اختيار صورة مناسبة
# ============================================================

def choose_image(results):

    if not results:
        return None

    for result in results:

        license_name = (
            result.get(
                "license",
                ""
            )
            .lower()
        )

        if (
            "public domain" in license_name
            or "cc0" in license_name
            or "cc by" in license_name
            or "cc-by" in license_name
        ):

            return result

    return results[0]


# ============================================================
# تنزيل الصورة
# ============================================================

def download_image(
    image_url,
    output_path
):

    print(
        "Downloading image..."
    )

    headers = {
        "User-Agent": USER_AGENT
    }

    try:

        response = requests.get(
            image_url,
            headers=headers,
            timeout=60
        )

        response.raise_for_status()

        with open(
            output_path,
            "wb"
        ) as file:

            file.write(
                response.content
            )

        print(
            "Image downloaded:",
            output_path
        )

        return True

    except Exception as error:

        print(
            "Image download error:",
            error
        )

        return False


# ============================================================
# الوظيفة الرئيسية
# ============================================================

def fetch_news_image(
    title,
    keywords=None
):

    os.makedirs(
        IMAGE_DIR,
        exist_ok=True
    )

    # --------------------------------------------------------
    # بناء عبارة البحث
    # --------------------------------------------------------

    query = title

    if keywords:

        query = (
            f"{title} "
            f"{keywords}"
        )

    # --------------------------------------------------------
    # البحث
    # --------------------------------------------------------

    results = search_commons(
        query
    )

    if not results:

        print(
            "No suitable images found."
        )

        return None

    # --------------------------------------------------------
    # اختيار الصورة
    # --------------------------------------------------------

    selected = choose_image(
        results
    )

    if not selected:

        print(
            "Could not select an image."
        )

        return None

    print()
    print(
        "Selected image:"
    )

    print(
        "Title:",
        selected["title"]
    )

    print(
        "License:",
        selected["license"]
    )

    print(
        "Artist:",
        selected["artist"]
    )

    print(
        "Source:",
        selected["source_url"]
    )

    # --------------------------------------------------------
    # اسم الملف
    # --------------------------------------------------------

    filename = (
        safe_filename(title)
        + ".jpg"
    )

    output_path = os.path.join(
        IMAGE_DIR,
        filename
    )

    # --------------------------------------------------------
    # تنزيل
    # --------------------------------------------------------

    success = download_image(
        selected["image_url"],
        output_path
    )

    if not success:

        return None

    # --------------------------------------------------------
    # حفظ معلومات المصدر
    # --------------------------------------------------------

    metadata_path = (
        output_path
        + ".txt"
    )

    try:

        with open(
            metadata_path,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                "Title: "
                + selected["title"]
                + "\n"
            )

            file.write(
                "License: "
                + selected["license"]
                + "\n"
            )

            file.write(
                "Artist: "
                + selected["artist"]
                + "\n"
            )

            file.write(
                "Source: "
                + selected["source_url"]
                + "\n"
            )

    except Exception as error:

        print(
            "Metadata save error:",
            error
        )

    return {
        "image_path": output_path,
        "license": selected["license"],
        "artist": selected["artist"],
        "source_url": selected["source_url"],
        "title": selected["title"],
    }


# ============================================================
# اختبار مستقل
# ============================================================

if __name__ == "__main__":

    TEST_TITLE = (
        "Real Madrid football"
    )

    result = fetch_news_image(
        title=TEST_TITLE
    )

    print()

    if result:

        print(
            "==================================="
        )

        print(
            "IMAGE FETCH SUCCESS"
        )

        print(
            "Image:",
            result["image_path"]
        )

        print(
            "License:",
            result["license"]
        )

        print(
            "Artist:",
            result["artist"]
        )

        print(
            "Source:",
            result["source_url"]
        )

        print(
            "==================================="
        )

    else:

        print(
            "IMAGE FETCH FAILED"
        )

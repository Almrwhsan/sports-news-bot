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

SEARCH_LIMIT = 10
IMAGE_WIDTH = 1200
REQUEST_TIMEOUT = 30
DOWNLOAD_TIMEOUT = 60


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
# تنظيف نص البحث
# ============================================================

def clean_search_text(text):

    if not text:
        return ""

    text = str(text)

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# استخراج كلمات مهمة من العنوان
# ============================================================

def extract_search_terms(title):

    title = clean_search_text(title)

    if not title:
        return []

    # --------------------------------------------------------
    # أسماء الأندية والبطولات المهمة
    # --------------------------------------------------------

    important_terms = [

        # Real Madrid
        "Real Madrid",
        "Madrid",
        "ريال مدريد",

        # Barcelona
        "Barcelona",
        "Barca",
        "برشلونة",

        # Atletico
        "Atletico Madrid",
        "Atlético Madrid",
        "Atletico",
        "أتلتيكو مدريد",
        "أتليتكو مدريد",

        # Manchester
        "Manchester United",
        "Manchester City",

        # Liverpool
        "Liverpool",

        # Arsenal
        "Arsenal",

        # Chelsea
        "Chelsea",

        # Tottenham
        "Tottenham",

        # Bayern
        "Bayern Munich",
        "Bayern",

        # Dortmund
        "Borussia Dortmund",
        "Dortmund",

        # PSG
        "Paris Saint-Germain",
        "PSG",

        # Juventus
        "Juventus",

        # Inter
        "Inter Milan",

        # AC Milan
        "AC Milan",
        "Milan",

        # football
        "football",
        "soccer",
        "كرة القدم",
    ]

    found_terms = []

    lower_title = title.lower()

    for term in important_terms:

        if term.lower() in lower_title:

            if term not in found_terms:

                found_terms.append(
                    term
                )

    return found_terms


# ============================================================
# بناء استعلامات متعددة
# ============================================================

def build_search_queries(
    title,
    keywords=None
):

    title = clean_search_text(title)

    queries = []

    # --------------------------------------------------------
    # 1. العنوان الكامل
    # --------------------------------------------------------

    if title:

        queries.append(
            title
        )

    # --------------------------------------------------------
    # 2. العنوان + football
    # --------------------------------------------------------

    if title:

        queries.append(
            f"{title} football"
        )

    # --------------------------------------------------------
    # 3. الكلمات المهمة
    # --------------------------------------------------------

    important_terms = extract_search_terms(
        title
    )

    if important_terms:

        query = (
            " ".join(
                important_terms
            )
            + " football"
        )

        queries.append(
            query
        )

    # --------------------------------------------------------
    # 4. keywords إضافية
    # --------------------------------------------------------

    if keywords:

        keyword_text = clean_search_text(
            keywords
        )

        if keyword_text:

            queries.append(
                f"{title} {keyword_text}"
            )

            queries.append(
                f"{keyword_text} football"
            )

    # --------------------------------------------------------
    # 5. إذا وجد نادي، ابحث عنه بشكل مباشر
    # --------------------------------------------------------

    club_queries = [

        (
            "Real Madrid",
            "Real Madrid football"
        ),

        (
            "Barcelona",
            "Barcelona football"
        ),

        (
            "Manchester United",
            "Manchester United football"
        ),

        (
            "Manchester City",
            "Manchester City football"
        ),

        (
            "Liverpool",
            "Liverpool FC football"
        ),

        (
            "Arsenal",
            "Arsenal FC football"
        ),

        (
            "Chelsea",
            "Chelsea FC football"
        ),

        (
            "Tottenham",
            "Tottenham Hotspur football"
        ),

        (
            "Bayern",
            "Bayern Munich football"
        ),

        (
            "Dortmund",
            "Borussia Dortmund football"
        ),

        (
            "Juventus",
            "Juventus football"
        ),

        (
            "Milan",
            "AC Milan football"
        ),

        (
            "PSG",
            "Paris Saint-Germain football"
        ),
    ]

    lower_title = title.lower()

    for club_name, club_query in club_queries:

        if club_name.lower() in lower_title:

            queries.append(
                club_query
            )

    # --------------------------------------------------------
    # إزالة الاستعلامات المتكررة
    # --------------------------------------------------------

    unique_queries = []

    for query in queries:

        query = clean_search_text(
            query
        )

        if not query:
            continue

        if query not in unique_queries:

            unique_queries.append(
                query
            )

    return unique_queries


# ============================================================
# البحث في Wikimedia Commons
# ============================================================

def search_commons(query):

    print()
    print(
        "Searching Wikimedia Commons..."
    )

    print(
        "Query:",
        query
    )

    params = {

        "action": "query",

        "generator": "search",

        "gsrsearch": query,

        "gsrnamespace": 6,

        "gsrlimit": SEARCH_LIMIT,

        "prop": "imageinfo",

        "iiprop": (
            "url|mime|size|extmetadata"
        ),

        "iiurlwidth": IMAGE_WIDTH,

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
            timeout=REQUEST_TIMEOUT
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

            if not mime.startswith(
                "image/"
            ):

                continue

            metadata = info.get(
                "extmetadata",
                {}
            )

            license_name = (
                metadata
                .get(
                    "LicenseShortName",
                    {}
                )
                .get(
                    "value",
                    ""
                )
            )

            artist = (
                metadata
                .get(
                    "Artist",
                    {}
                )
                .get(
                    "value",
                    ""
                )
            )

            description_url = (
                "https://commons.wikimedia.org/wiki/"
                + page.get(
                    "title",
                    ""
                ).replace(
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
                    info.get(
                        "url",
                        ""
                    )
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
# البحث باستخدام عدة استعلامات
# ============================================================

def search_commons_multiple(
    title,
    keywords=None
):

    queries = build_search_queries(
        title,
        keywords
    )

    print()
    print(
        "Search queries:"
    )

    for index, query in enumerate(
        queries,
        start=1
    ):

        print(
            f"{index}. {query}"
        )

    all_results = []

    for query in queries:

        results = search_commons(
            query
        )

        if not results:

            continue

        all_results.extend(
            results
        )

        # ----------------------------------------------------
        # إذا وجدنا نتائج، لا نحتاج غالبًا
        # للاستمرار في البحث العشوائي
        # ----------------------------------------------------

        if len(all_results) >= SEARCH_LIMIT:

            break

    # --------------------------------------------------------
    # إزالة الصور المكررة
    # --------------------------------------------------------

    unique_results = []

    seen_urls = set()

    for result in all_results:

        image_url = result.get(
            "image_url",
            ""
        )

        if not image_url:

            continue

        if image_url in seen_urls:

            continue

        seen_urls.add(
            image_url
        )

        unique_results.append(
            result
        )

    print()
    print(
        "Total unique images:",
        len(unique_results)
    )

    return unique_results


# ============================================================
# اختيار صورة مناسبة
# ============================================================

def choose_image(results):

    if not results:

        return None

    # --------------------------------------------------------
    # الأفضلية للتراخيص المفتوحة
    # --------------------------------------------------------

    preferred_results = []

    for result in results:

        license_name = (
            result.get(
                "license",
                ""
            )
            .lower()
        )

        if (
            "public domain"
            in license_name

            or "cc0"
            in license_name

            or "cc by"
            in license_name

            or "cc-by"
            in license_name
        ):

            preferred_results.append(
                result
            )

    if preferred_results:

        return preferred_results[0]

    # --------------------------------------------------------
    # إذا لم توجد صورة بترخيص مفضل
    # نستخدم أول نتيجة
    # --------------------------------------------------------

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
            timeout=DOWNLOAD_TIMEOUT
        )

        response.raise_for_status()

        content_type = (
            response.headers
            .get(
                "Content-Type",
                ""
            )
            .lower()
        )

        if not content_type.startswith(
            "image/"
        ):

            print(
                "Downloaded file is not an image."
            )

            return False

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
# حفظ معلومات الصورة
# ============================================================

def save_image_metadata(
    output_path,
    selected
):

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
                + selected.get(
                    "title",
                    ""
                )
                + "\n"
            )

            file.write(
                "License: "
                + selected.get(
                    "license",
                    ""
                )
                + "\n"
            )

            file.write(
                "Artist: "
                + selected.get(
                    "artist",
                    ""
                )
                + "\n"
            )

            file.write(
                "Source: "
                + selected.get(
                    "source_url",
                    ""
                )
                + "\n"
            )

            file.write(
                "Original URL: "
                + selected.get(
                    "original_url",
                    ""
                )
                + "\n"
            )

        print(
            "Image metadata saved:",
            metadata_path
        )

    except Exception as error:

        print(
            "Metadata save error:",
            error
        )


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

    title = clean_search_text(
        title
    )

    if not title:

        print(
            "Empty title. Cannot search for image."
        )

        return None

    # --------------------------------------------------------
    # البحث بعدة طرق
    # --------------------------------------------------------

    results = search_commons_multiple(
        title,
        keywords
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
        selected.get(
            "title",
            ""
        )
    )

    print(
        "License:",
        selected.get(
            "license",
            ""
        )
    )

    print(
        "Artist:",
        selected.get(
            "artist",
            ""
        )
    )

    print(
        "Source:",
        selected.get(
            "source_url",
            ""
        )
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
    # تنزيل الصورة
    # --------------------------------------------------------

    success = download_image(
        selected.get(
            "image_url",
            ""
        ),
        output_path
    )

    if not success:

        return None

    # --------------------------------------------------------
    # حفظ معلومات المصدر
    # --------------------------------------------------------

    save_image_metadata(
        output_path,
        selected
    )

    # --------------------------------------------------------
    # النتيجة
    # --------------------------------------------------------

    return {

        "image_path": output_path,

        "license": selected.get(
            "license",
            ""
        ),

        "artist": selected.get(
            "artist",
            ""
        ),

        "source_url": selected.get(
            "source_url",
            ""
        ),

        "title": selected.get(
            "title",
            ""
        ),

    }


# ============================================================
# اختبار مستقل
# ============================================================

if __name__ == "__main__":

    TEST_TITLE = (
        "Real Madrid signs a new midfielder"
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
            "===================================",
        )

    else:

        print(
            "IMAGE FETCH FAILED"
            )

import os
import re
import time
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

# عدد محاولات البحث القصوى للخبر الواحد
MAX_SEARCH_ATTEMPTS = 3

# تأخير بسيط بين طلبات Wikimedia
REQUEST_DELAY = 1.5


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
# استخراج أسماء الأندية من العنوان
# ============================================================

def extract_club_terms(title):

    title = clean_search_text(
        title
    )

    lower_title = title.lower()

    clubs = [

        (
            "real madrid",
            "Real Madrid football"
        ),

        (
            "madrid",
            "Real Madrid football"
        ),

        (
            "ريال مدريد",
            "Real Madrid football"
        ),

        (
            "barcelona",
            "FC Barcelona football"
        ),

        (
            "barca",
            "FC Barcelona football"
        ),

        (
            "برشلونة",
            "FC Barcelona football"
        ),

        (
            "atletico madrid",
            "Atletico Madrid football"
        ),

        (
            "atlético madrid",
            "Atletico Madrid football"
        ),

        (
            "أتلتيكو مدريد",
            "Atletico Madrid football"
        ),

        (
            "أتليتكو مدريد",
            "Atletico Madrid football"
        ),

        (
            "manchester united",
            "Manchester United football"
        ),

        (
            "manchester city",
            "Manchester City football"
        ),

        (
            "liverpool",
            "Liverpool FC football"
        ),

        (
            "arsenal",
            "Arsenal FC football"
        ),

        (
            "chelsea",
            "Chelsea FC football"
        ),

        (
            "tottenham",
            "Tottenham Hotspur football"
        ),

        (
            "bayern",
            "Bayern Munich football"
        ),

        (
            "borussia dortmund",
            "Borussia Dortmund football"
        ),

        (
            "dortmund",
            "Borussia Dortmund football"
        ),

        (
            "juventus",
            "Juventus football"
        ),

        (
            "psg",
            "Paris Saint-Germain football"
        ),

        (
            "paris saint-germain",
            "Paris Saint-Germain football"
        ),

        (
            "ac milan",
            "AC Milan football"
        ),

        (
            "milan",
            "AC Milan football"
        ),

        (
            "inter milan",
            "Inter Milan football"
        ),
    ]

    found = []

    for keyword, query in clubs:

        if keyword in lower_title:

            if query not in found:

                found.append(
                    query
                )

    return found


# ============================================================
# استخراج كلمات مهمة من العنوان
# ============================================================

def extract_person_terms(title):

    title = clean_search_text(
        title
    )

    if not title:
        return []

    terms = []

    # --------------------------------------------------------
    # أسماء معروفة تظهر كثيرًا في أخبار كرة القدم
    # --------------------------------------------------------

    known_people = [

        "Benzema",
        "Karim Benzema",

        "Pogba",
        "Paul Pogba",

        "Coutinho",
        "Philippe Coutinho",

        "Mbappe",
        "Mbappé",
        "Kylian Mbappe",

        "Vinicius",
        "Vinicius Junior",

        "Bellingham",
        "Jude Bellingham",

        "Rodrygo",

        "Modric",
        "Luka Modric",

        "Kroos",
        "Toni Kroos",

        "De Bruyne",
        "Kevin De Bruyne",

        "Haaland",
        "Erling Haaland",

        "Foden",
        "Phil Foden",

        "Salah",
        "Mohamed Salah",

        "Ronaldo",
        "Cristiano Ronaldo",

        "Messi",
        "Lionel Messi",

        "Deco",

        "Lewandowski",
        "Robert Lewandowski",

        "Pedri",

        "Gavi",

        "Yamal",
        "Lamine Yamal",

        "Neymar",

        "Kane",
        "Harry Kane",

        "Guardiola",
        "Pep Guardiola",

        "Mourinho",
        "Jose Mourinho",

        "Ancelotti",
        "Carlo Ancelotti",
    ]

    lower_title = title.lower()

    for person in known_people:

        if person.lower() in lower_title:

            if person not in terms:

                terms.append(
                    person
                )

    return terms


# ============================================================
# بناء استعلامات البحث
# ============================================================

def build_search_queries(
    title,
    keywords=None
):

    title = clean_search_text(
        title
    )

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
    # 3. النادي
    # --------------------------------------------------------

    club_queries = extract_club_terms(
        title
    )

    for query in club_queries:

        queries.append(
            query
        )

    # --------------------------------------------------------
    # 4. اللاعب
    # --------------------------------------------------------

    person_terms = extract_person_terms(
        title
    )

    for person in person_terms:

        queries.append(
            f"{person} football"
        )

    # --------------------------------------------------------
    # 5. اللاعب + النادي
    # --------------------------------------------------------

    for person in person_terms:

        for club_query in club_queries:

            queries.append(
                f"{person} {club_query}"
            )

    # --------------------------------------------------------
    # 6. الكلمات الإضافية
    # --------------------------------------------------------

    if keywords:

        keyword_text = clean_search_text(
            keywords
        )

        if keyword_text:

            queries.append(
                f"{keyword_text} football"
            )

    # --------------------------------------------------------
    # إزالة التكرار
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

        # ----------------------------------------------------
        # معالجة 429 بشكل صحيح
        # ----------------------------------------------------

        if response.status_code == 429:

            retry_after = (
                response.headers
                .get(
                    "Retry-After"
                )
            )

            if retry_after:

                try:
                    wait_seconds = int(
                        retry_after
                    )
                except ValueError:
                    wait_seconds = 5

            else:

                wait_seconds = 5

            print(
                "⚠️ Wikimedia rate limit reached."
            )

            print(
                f"Waiting {wait_seconds} seconds..."
            )

            time.sleep(
                wait_seconds
            )

            return []

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

    except requests.exceptions.HTTPError as error:

        print(
            "Commons HTTP error:",
            error
        )

        return []

    except Exception as error:

        print(
            "Commons search error:",
            error
        )

        return []


# ============================================================
# البحث باستخدام استعلامات متعددة
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

    attempts = 0

    for query in queries:

        if attempts >= MAX_SEARCH_ATTEMPTS:

            break

        attempts += 1

        results = search_commons(
            query
        )

        # ----------------------------------------------------
        # إذا حصلنا على نتائج نكتفي بها
        # ----------------------------------------------------

        if results:

            all_results.extend(
                results
            )

            break

        # ----------------------------------------------------
        # تأخير قبل الطلب التالي
        # ----------------------------------------------------

        time.sleep(
            REQUEST_DELAY
        )

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
# اختيار الصورة المناسبة
# ============================================================

def choose_image(results):

    if not results:

        return None

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
    # البحث
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
    # تنزيل
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
            "==================================="
        )

    else:

        print(
            "IMAGE FETCH FAILED"
    )

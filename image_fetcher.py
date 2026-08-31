import os
import re
import html
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

REQUEST_TIMEOUT = 30
DOWNLOAD_TIMEOUT = 60

MAX_SEARCH_RESULTS = 10

# الامتدادات المقبولة
ALLOWED_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp",
}

# أنواع MIME المقبولة
ALLOWED_MIMES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


# ============================================================
# كلمات لا نريد استخدامها في استخراج أسماء الأشخاص/الأندية
# ============================================================

STOP_WORDS = {
    "the",
    "and",
    "for",
    "from",
    "with",
    "after",
    "before",
    "into",
    "over",
    "under",
    "agree",
    "agrees",
    "agreed",
    "fee",
    "deal",
    "sign",
    "signs",
    "signed",
    "transfer",
    "transfered",
    "transfers",
    "football",
    "soccer",
    "match",
    "matches",
    "news",
    "latest",
    "breaking",
    "city",
    "club",
    "fc",

    "ال",
    "في",
    "من",
    "إلى",
    "عن",
    "مع",
    "على",
    "بعد",
    "قبل",
    "كرة",
    "القدم",
    "مباراة",
    "مباريات",
    "خبر",
    "أخبار",
    "صفقة",
    "انتقال",
    "ينتقل",
    "ينضم",
    "تعاقد",
    "نادي",
}


# ============================================================
# تنظيف HTML
# ============================================================

def clean_html_text(text):

    if not text:
        return ""

    text = str(text)

    text = html.unescape(text)

    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# تنظيف اسم الملف
# ============================================================

def safe_filename(text):

    text = str(text)

    text = clean_html_text(text)

    # إزالة الرموز غير المناسبة لأسماء الملفات
    text = re.sub(
        r'[\\/*?:"<>|]',
        "",
        text
    )

    # إزالة بعض رموز الترقيم
    text = re.sub(
        r"[^\w\s\u0600-\u06FF\-]",
        "",
        text,
        flags=re.UNICODE
    )

    # استبدال المسافات
    text = re.sub(
        r"\s+",
        "_",
        text
    )

    # إزالة _ المتكررة
    text = re.sub(
        r"_+",
        "_",
        text
    )

    text = text.strip("_")

    # الحد الأقصى
    text = text[:80]

    if not text:
        text = "football_image"

    return text


# ============================================================
# استخراج امتداد الصورة
# ============================================================

def get_image_extension(image_url, mime=""):

    mime = (mime or "").lower().strip()

    if mime == "image/jpeg":
        return "jpg"

    if mime == "image/png":
        return "png"

    if mime == "image/webp":
        return "webp"

    # محاولة استخراج الامتداد من الرابط
    url_without_query = image_url.split("?", 1)[0]

    match = re.search(
        r"\.([a-zA-Z0-9]+)$",
        url_without_query
    )

    if match:

        extension = match.group(1).lower()

        if extension == "jpeg":
            return "jpg"

        if extension in ALLOWED_EXTENSIONS:
            return extension

    return "jpg"


# ============================================================
# التحقق من أن النتيجة صورة
# ============================================================

def is_valid_image(info):

    mime = (
        info.get("mime", "")
        .lower()
        .strip()
    )

    if mime in ALLOWED_MIMES:
        return True

    image_url = (
        info.get("thumburl")
        or info.get("url")
        or ""
    )

    extension = get_image_extension(
        image_url,
        mime
    )

    return extension in ALLOWED_EXTENSIONS


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
        "gsrlimit": MAX_SEARCH_RESULTS,
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

            if not is_valid_image(info):
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

            # تنظيف HTML من Artist
            artist = clean_html_text(
                artist
            )

            page_title = page.get(
                "title",
                ""
            )

            description_url = (
                "https://commons.wikimedia.org/wiki/"
                + page_title.replace(
                    " ",
                    "_"
                )
            )

            image_url = info.get(
                "thumburl",
                info.get(
                    "url",
                    ""
                )
            )

            original_url = info.get(
                "url",
                ""
            )

            if not image_url:
                continue

            results.append({

                "title": page_title,

                "image_url": image_url,

                "original_url": original_url,

                "license": clean_html_text(
                    license_name
                ),

                "artist": artist,

                "source_url": description_url,

                "mime": info.get(
                    "mime",
                    ""
                ),

            })

        print(
            "Images found:",
            len(results)
        )

        return results

    except requests.RequestException as error:

        print(
            "Commons network error:",
            error
        )

        return []

    except ValueError as error:

        print(
            "Commons JSON error:",
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
# استخراج كلمات مهمة من عنوان الخبر
# ============================================================

def extract_search_terms(title):

    title = clean_html_text(
        title
    )

    # إزالة المبالغ المالية
    title = re.sub(
        r"[£$€]\s?\d+(?:[.,]\d+)?(?:m|k|million|million)?",
        " ",
        title,
        flags=re.IGNORECASE
    )

    # إزالة الأرقام
    title = re.sub(
        r"\b\d+\b",
        " ",
        title
    )

    # فصل الكلمات
    words = re.findall(
        r"[A-Za-zÀ-ÖØ-öø-ÿ\u0600-\u06FF'-]+",
        title
    )

    useful_words = []

    for word in words:

        clean_word = word.strip(
            "'-"
        )

        if not clean_word:
            continue

        if len(clean_word) < 3:
            continue

        if clean_word.lower() in STOP_WORDS:
            continue

        useful_words.append(
            clean_word
        )

    return useful_words


# ============================================================
# بناء استعلامات بحث بديلة
# ============================================================

def build_search_queries(title, keywords=None):

    title = clean_html_text(
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
    # 3. العنوان + soccer
    # --------------------------------------------------------

    if title:

        queries.append(
            f"{title} soccer"
        )

    # --------------------------------------------------------
    # استخراج الكلمات المهمة
    # --------------------------------------------------------

    terms = extract_search_terms(
        title
    )

    # --------------------------------------------------------
    # آخر الكلمات المهمة
    # --------------------------------------------------------

    if terms:

        # أول 4 كلمات مهمة
        short_terms = terms[:4]

        queries.append(
            " ".join(short_terms)
        )

        queries.append(
            " ".join(short_terms)
            + " football"
        )

    # --------------------------------------------------------
    # محاولة العثور على أسماء الأندية/الأشخاص
    # --------------------------------------------------------

    if len(terms) >= 2:

        # مثال:
        # Hull Everton Iroegbunam
        entity_query = " ".join(
            terms[:3]
        )

        queries.append(
            entity_query
        )

        queries.append(
            entity_query
            + " football"
        )

    # --------------------------------------------------------
    # الكلمات الإضافية
    # --------------------------------------------------------

    if keywords:

        keywords = clean_html_text(
            keywords
        )

        if keywords:

            queries.append(
                f"{title} {keywords}"
            )

            queries.append(
                f"{keywords} football"
            )

    # --------------------------------------------------------
    # إزالة التكرارات
    # --------------------------------------------------------

    unique_queries = []

    seen = set()

    for query in queries:

        query = query.strip()

        normalized = query.lower()

        if not query:
            continue

        if normalized in seen:
            continue

        seen.add(
            normalized
        )

        unique_queries.append(
            query
        )

    return unique_queries


# ============================================================
# حساب أفضلية الصورة
# ============================================================

def image_score(result):

    score = 0

    title = (
        result.get(
            "title",
            ""
        )
        .lower()
    )

    license_name = (
        result.get(
            "license",
            ""
        )
        .lower()
    )

    # --------------------------------------------------------
    # أولوية التراخيص
    # --------------------------------------------------------

    if "public domain" in license_name:
        score += 100

    elif "cc0" in license_name:
        score += 100

    elif "cc by-sa" in license_name:
        score += 80

    elif "cc by" in license_name:
        score += 70

    elif "cc-by-sa" in license_name:
        score += 80

    elif "cc-by" in license_name:
        score += 70

    # --------------------------------------------------------
    # صور فوتوغرافية
    # --------------------------------------------------------

    if any(
        word in title
        for word in [
            "match",
            "stadium",
            "football",
            "soccer",
            "player",
            "fc",
            "club",
        ]
    ):
        score += 10

    # --------------------------------------------------------
    # نستبعد بعض أنواع الملفات غير المفيدة
    # --------------------------------------------------------

    if any(
        word in title
        for word in [
            "logo",
            "flag",
            "icon",
            "crest",
            "map",
        ]
    ):
        score -= 30

    return score


# ============================================================
# اختيار الصورة المناسبة
# ============================================================

def choose_image(results):

    if not results:
        return None

    # ترتيب النتائج حسب الأفضلية
    sorted_results = sorted(
        results,
        key=image_score,
        reverse=True
    )

    # --------------------------------------------------------
    # أولًا نحاول اختيار صورة ذات ترخيص واضح
    # --------------------------------------------------------

    for result in sorted_results:

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

    # --------------------------------------------------------
    # إذا لم توجد رخصة من الأنواع السابقة
    # نعيد أفضل نتيجة موجودة.
    # --------------------------------------------------------

    return sorted_results[0]


# ============================================================
# البحث الذكي عن صورة
# ============================================================

def find_news_image(
    title,
    keywords=None
):

    queries = build_search_queries(
        title,
        keywords
    )

    if not queries:
        return None

    all_results = []

    seen_urls = set()

    # --------------------------------------------------------
    # تجربة عدة استعلامات
    # --------------------------------------------------------

    for query in queries:

        results = search_commons(
            query
        )

        if not results:
            continue

        for result in results:

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

            all_results.append(
                result
            )

        # ----------------------------------------------------
        # إذا وجدنا نتائج جيدة بتراخيص مناسبة
        # نتوقف مبكرًا.
        # ----------------------------------------------------

        if any(
            (
                "public domain"
                in result.get(
                    "license",
                    ""
                ).lower()
                or
                "cc0"
                in result.get(
                    "license",
                    ""
                ).lower()
                or
                "cc by"
                in result.get(
                    "license",
                    ""
                ).lower()
                or
                "cc-by"
                in result.get(
                    "license",
                    ""
                ).lower()
            )
            for result in results
        ):

            break

    print()
    print(
        "Total unique images collected:",
        len(all_results)
    )

    if not all_results:
        return None

    return choose_image(
        all_results
    )


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
            .split(";")[0]
            .lower()
            .strip()
        )

        # ----------------------------------------------------
        # التحقق من نوع الملف
        # ----------------------------------------------------

        if (
            content_type
            and content_type not in ALLOWED_MIMES
        ):

            print(
                "Warning: unexpected content type:",
                content_type
            )

        # ----------------------------------------------------
        # التحقق من وجود محتوى
        # ----------------------------------------------------

        if not response.content:

            print(
                "Downloaded file is empty."
            )

            return False

        # ----------------------------------------------------
        # حفظ الصورة
        # ----------------------------------------------------

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

        print(
            "File size:",
            len(response.content),
            "bytes"
        )

        return True

    except requests.RequestException as error:

        print(
            "Image download error:",
            error
        )

        return False

    except OSError as error:

        print(
            "File save error:",
            error
        )

        return False

    except Exception as error:

        print(
            "Unexpected download error:",
            error
        )

        return False


# ============================================================
# حفظ بيانات المصدر
# ============================================================

def save_metadata(
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
                + str(
                    selected.get(
                        "title",
                        ""
                    )
                )
                + "\n"
            )

            file.write(
                "License: "
                + str(
                    selected.get(
                        "license",
                        ""
                    )
                )
                + "\n"
            )

            file.write(
                "Artist: "
                + str(
                    selected.get(
                        "artist",
                        ""
                    )
                )
                + "\n"
            )

                       file.write(
                "Source: "
                + str(
                    selected.get(
                        "source_url",
                        ""
                    )
                )
                + "\n"
            )

            file.write(
                "Original URL: "
                + str(
                    selected.get(
                        "original_url",
                        ""
                    )
                )
                + "\n"
            )

        print(
            "Metadata saved:",
            metadata_path
        )

        return True

    except OSError as error:

        print(
            "Metadata save error:",
            error
        )

        return False

    except Exception as error:

        print(
            "Unexpected metadata error:",
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

    # --------------------------------------------------------
    # إنشاء مجلد الصور
    # --------------------------------------------------------

    os.makedirs(
        IMAGE_DIR,
        exist_ok=True
    )

    print()
    print(
        "Searching for news image..."
    )

    # --------------------------------------------------------
    # البحث الذكي
    # --------------------------------------------------------

    selected = find_news_image(
        title=title,
        keywords=keywords
    )

    # --------------------------------------------------------
    # لا توجد صورة
    # --------------------------------------------------------

    if not selected:

        print(
            "No suitable images found."
        )

        return None

    # --------------------------------------------------------
    # عرض معلومات الصورة
    # --------------------------------------------------------

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
    # تحديد امتداد الصورة
    # --------------------------------------------------------

    extension = get_image_extension(
        selected.get(
            "image_url",
            ""
        ),
        selected.get(
            "mime",
            ""
        )
    )

    # --------------------------------------------------------
    # اسم الملف
    # --------------------------------------------------------

    filename = (
        safe_filename(title)
        + "."
        + extension
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

        print(
            "Could not download selected image."
        )

        return None

    # --------------------------------------------------------
    # حفظ معلومات المصدر
    # --------------------------------------------------------

    save_metadata(
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

        "original_url": selected.get(
            "original_url",
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
        "Hull agree £22m fee for Everton's Iroegbunam"
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
              

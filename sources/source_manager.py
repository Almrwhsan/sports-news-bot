# ============================================================
# مدير المصادر
# ============================================================

import feedparser


# ============================================================
# امتدادات الصور والفيديو
# ============================================================

IMAGE_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".gif",
    ".bmp",
    ".avif",
)

VIDEO_EXTENSIONS = (
    ".mp4",
    ".webm",
    ".mov",
    ".m4v",
    ".avi",
    ".mkv",
    ".m3u8",
)


# ============================================================
# التحقق من أن الرابط صورة
# ============================================================

def is_image_url(url):
    if not url:
        return False

    url = url.lower().split("?")[0].split("#")[0]

    return url.endswith(IMAGE_EXTENSIONS)


# ============================================================
# التحقق من أن الرابط فيديو
# ============================================================

def is_video_url(url):
    if not url:
        return False

    url = url.lower().split("?")[0].split("#")[0]

    return url.endswith(VIDEO_EXTENSIONS)


# ============================================================
# استخراج رابط الوسائط من عنصر RSS
# ============================================================

def extract_media_url(item):
    if not item:
        return None, None

    # --------------------------------------------------------
    # قراءة البيانات الأساسية
    # --------------------------------------------------------

    url = (
        item.get("url")
        or item.get("href")
        or ""
    )

    mime_type = (
        item.get("type")
        or ""
    ).lower().strip()

    medium = (
        item.get("medium")
        or ""
    ).lower().strip()

    # --------------------------------------------------------
    # فيديو
    # --------------------------------------------------------

    if (
        mime_type.startswith("video/")
        or medium == "video"
        or is_video_url(url)
    ):
        return url or None, "video"

    # --------------------------------------------------------
    # صورة
    # --------------------------------------------------------

    if (
        mime_type.startswith("image/")
        or medium == "image"
        or is_image_url(url)
    ):
        return url or None, "image"

    # --------------------------------------------------------
    # إذا كان هناك رابط ولكن نوعه غير معروف
    # --------------------------------------------------------

    if url:

        # نحاول معرفة النوع من الامتداد
        if is_image_url(url):
            return url, "image"

        if is_video_url(url):
            return url, "video"

    return None, None


# ============================================================
# استخراج صورة / فيديو من خبر RSS
# ============================================================

def extract_media_from_entry(entry):

    image_candidates = []
    video_found = False

    # --------------------------------------------------------
    # Media RSS - media:content
    # --------------------------------------------------------

    media_content = entry.get(
        "media_content",
        []
    ) or []

    for item in media_content:

        url, media_type = extract_media_url(item)

        if media_type == "image" and url:
            image_candidates.append(url)

        elif media_type == "video":
            video_found = True

    # --------------------------------------------------------
    # Media RSS - media:thumbnail
    # --------------------------------------------------------

    media_thumbnail = entry.get(
        "media_thumbnail",
        []
    ) or []

    for item in media_thumbnail:

        url, media_type = extract_media_url(item)

        if media_type == "image" and url:
            image_candidates.append(url)

        elif media_type == "video":
            video_found = True

    # --------------------------------------------------------
    # RSS enclosure
    # --------------------------------------------------------

    enclosures = entry.get(
        "enclosures",
        []
    ) or []

    for item in enclosures:

        url, media_type = extract_media_url(item)

        if media_type == "image" and url:
            image_candidates.append(url)

        elif media_type == "video":
            video_found = True

    # --------------------------------------------------------
    # entry.image
    # --------------------------------------------------------

    entry_image = entry.get(
        "image"
    )

    if entry_image:

        if isinstance(entry_image, dict):

            url, media_type = extract_media_url(
                entry_image
            )

            if media_type == "image" and url:
                image_candidates.append(url)

            elif media_type == "video":
                video_found = True

        elif isinstance(entry_image, str):

            if is_image_url(entry_image):
                image_candidates.append(
                    entry_image
                )

            elif is_video_url(entry_image):
                video_found = True

    # --------------------------------------------------------
    # iTunes image
    # --------------------------------------------------------

    itunes_image = entry.get(
        "itunes_image"
    )

    if itunes_image:

        if isinstance(itunes_image, dict):

            url, media_type = extract_media_url(
                itunes_image
            )

            if media_type == "image" and url:
                image_candidates.append(url)

            elif media_type == "video":
                video_found = True

        elif isinstance(itunes_image, str):

            if is_image_url(itunes_image):
                image_candidates.append(
                    itunes_image
                )

    # --------------------------------------------------------
    # الروابط الموجودة داخل entry.links
    # --------------------------------------------------------

    links = entry.get(
        "links",
        []
    ) or []

    for item in links:

        url, media_type = extract_media_url(item)

        if media_type == "image" and url:
            image_candidates.append(url)

        elif media_type == "video":
            video_found = True

    # --------------------------------------------------------
    # إزالة التكرار مع الحفاظ على الترتيب
    # --------------------------------------------------------

    unique_images = []

    for image_url in image_candidates:

        if image_url not in unique_images:
            unique_images.append(image_url)

    # --------------------------------------------------------
    # إذا وجدنا صورة، نستخدمها
    # --------------------------------------------------------

    if unique_images:

        return {
            "image_url": unique_images[0],
            "media_type": "image",
        }

    # --------------------------------------------------------
    # إذا لم توجد صورة وكان الموجود فيديو
    # --------------------------------------------------------

    if video_found:

        return {
            "image_url": "",
            "media_type": "video",
        }

    # --------------------------------------------------------
    # لا توجد صورة ولا فيديو
    # --------------------------------------------------------

    return {
        "image_url": "",
        "media_type": None,
    }


# ============================================================
# جلب الأخبار من مصدر واحد
# ============================================================

def fetch_source(source):

    # --------------------------------------------------------
    # التحقق من تفعيل المصدر
    # --------------------------------------------------------

    if not source.get("enabled", True):

        return []

    # --------------------------------------------------------
    # قراءة رابط RSS
    # --------------------------------------------------------

    feed_url = source.get("feed")

    if not feed_url:

        return []

    # --------------------------------------------------------
    # قراءة RSS
    # --------------------------------------------------------

    try:

        feed = feedparser.parse(
            feed_url
        )

    except Exception as error:

        print(
            f"❌ Failed to fetch "
            f"{source.get('name', 'Unknown Source')}: "
            f"{error}"
        )

        return []

    # --------------------------------------------------------
    # تحويل الأخبار إلى صيغة موحدة
    # --------------------------------------------------------

    news = []

    for entry in feed.entries:

        # ----------------------------------------------------
        # استخراج بيانات الصورة / الفيديو
        # ----------------------------------------------------

        media = extract_media_from_entry(
            entry
        )

        # ----------------------------------------------------
        # إنشاء الخبر
        # ----------------------------------------------------

        news.append({

            "title": entry.get(
                "title",
                ""
            ),

            "url": entry.get(
                "link",
                ""
            ),

            "summary": entry.get(
                "summary",
                ""
            ),

            "published": entry.get(
                "published",
                ""
            ),

            "source": source.get(
                "name",
                "Unknown"
            ),

            "language": source.get(
                "language",
                ""
            ),

            "type": source.get(
                "type",
                ""
            ),

            "category": source.get(
                "category",
                ""
            ),

            "priority": source.get(
                "priority",
                999
            ),

            # ------------------------------------------------
            # بيانات الوسائط الجديدة
            # ------------------------------------------------

            "image_url": media.get(
                "image_url",
                ""
            ),

            "media_type": media.get(
                "media_type"
            ),

        })

    return news


# ============================================================
# جلب الأخبار من جميع المصادر
# ============================================================

def fetch_all_sources(sources):

    all_news = []

    # --------------------------------------------------------
    # ترتيب المصادر حسب الأولوية
    # --------------------------------------------------------

    sorted_sources = sorted(
        sources,
        key=lambda source: source.get(
            "priority",
            999
        )
    )

    # --------------------------------------------------------
    # تشغيل المصادر واحدًا تلو الآخر
    # --------------------------------------------------------

    for source in sorted_sources:

        print()
        print(
            f"Fetching: "
            f"{source.get('name', 'Unknown Source')}"
        )

        news = fetch_source(
            source
        )

        print(
            f"Entries received: "
            f"{len(news)}"
        )

        all_news.extend(
            news
        )

    # --------------------------------------------------------
    # إرجاع جميع الأخبار
    # --------------------------------------------------------

    return all_news

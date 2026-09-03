# ============================================================
# جالب صور الأخبار
# ============================================================
#
# المنطق:
#
# 1) استخدام الصورة القادمة من RSS إن وجدت.
# 2) إذا لم توجد صورة في RSS:
#       فحص صفحة الخبر الأصلية بحثًا عن:
#       - og:image
#       - twitter:image
#       - JSON-LD image
#       - image_src
#       - صور المقال
# 3) إذا كان الخبر فيديو فقط أو لا توجد صورة:
#       إرجاع None
#
# لا يوجد Wikimedia Commons
# لا يوجد بحث عن صور خارج مصدر الخبر
# ============================================================

import os
import re
import json
import hashlib
from io import BytesIO
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

import requests
from PIL import Image


# ============================================================
# إعدادات
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

IMAGE_DIR = os.path.join(
    BASE_DIR,
    "news_images"
)

REQUEST_TIMEOUT = 15

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)


# ============================================================
# امتدادات الصور
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


# ============================================================
# امتدادات الفيديو
# ============================================================

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
# كلمات تدل غالبًا على صور غير مناسبة
# ============================================================

IGNORED_IMAGE_WORDS = (
    "logo",
    "favicon",
    "icon",
    "avatar",
    "placeholder",
    "sprite",
    "default-image",
    "default_image",
    "defaultimage",
    "advert",
    "advertisement",
    "banner-ad",
    "banner_ad",
)


# ============================================================
# إنشاء مجلد الصور
# ============================================================

def ensure_image_directory():

    os.makedirs(
        IMAGE_DIR,
        exist_ok=True
    )


# ============================================================
# تنظيف اسم الملف
# ============================================================

def safe_filename(text):

    if not text:
        text = "news"

    text = str(text)

    text = re.sub(
        r"[^\w\-]+",
        "_",
        text,
        flags=re.UNICODE
    )

    text = text.strip("_")

    if not text:
        text = "news"

    return text[:100]


# ============================================================
# التحقق من رابط فيديو
# ============================================================

def is_video_url(url):

    if not url:
        return False

    try:
        path = urlparse(url).path.lower()
    except Exception:
        path = url.lower()

    return path.endswith(
        VIDEO_EXTENSIONS
    )


# ============================================================
# التحقق من رابط صورة
# ============================================================

def is_image_url(url):

    if not url:
        return False

    try:
        path = urlparse(url).path.lower()
    except Exception:
        path = url.lower()

    return path.endswith(
        IMAGE_EXTENSIONS
    )


# ============================================================
# التحقق من صورة غير مرغوبة
# ============================================================

def is_ignored_image(url):

    if not url:
        return True

    lowered = url.lower()

    for word in IGNORED_IMAGE_WORDS:

        if word in lowered:
            return True

    return False


# ============================================================
# تحويل الرابط إلى رابط مطلق
# ============================================================

def make_absolute_url(
    image_url,
    article_url=None
):

    if not image_url:
        return None

    image_url = str(
        image_url
    ).strip()

    if not image_url:
        return None

    if image_url.startswith(
        "//"
    ):

        return "https:" + image_url

    if article_url:

        image_url = urljoin(
            article_url,
            image_url
        )

    return image_url


# ============================================================
# Parser بسيط لاستخراج بيانات HTML
# ============================================================

class SourceImageParser(HTMLParser):

    def __init__(self):

        super().__init__(
            convert_charrefs=True
        )

        self.meta_images = []

        self.link_images = []

        self.img_images = []

        self.json_ld_blocks = []

        self.current_script_type = None

        self.current_script_data = []

        self.og_type = ""

        self.has_video = False

        self.in_article = 0

    # --------------------------------------------------------
    # بداية العنصر
    # --------------------------------------------------------

    def handle_starttag(
        self,
        tag,
        attrs
    ):

        attrs_dict = dict(
            attrs
        )

        tag = tag.lower()

        # ----------------------------------------------------
        # Meta
        # ----------------------------------------------------

        if tag == "meta":

            property_name = (
                attrs_dict.get(
                    "property",
                    ""
                )
                or attrs_dict.get(
                    "name",
                    ""
                )
            ).lower().strip()

            content = (
                attrs_dict.get(
                    "content",
                    ""
                )
                or ""
            ).strip()

            # og:image
            if property_name in (
                "og:image",
                "og:image:url",
                "og:image:secure_url",
                "twitter:image",
                "twitter:image:src",
            ):

                if content:

                    self.meta_images.append(
                        content
                    )

            # og:type
            if property_name == "og:type":

                self.og_type = (
                    content.lower()
                )

        # ----------------------------------------------------
        # Link image_src
        # ----------------------------------------------------

        elif tag == "link":

            rel = (
                attrs_dict.get(
                    "rel",
                    ""
                )
                or ""
            ).lower()

            href = (
                attrs_dict.get(
                    "href",
                    ""
                )
                or ""
            ).strip()

            if (
                "image_src" in rel
                and href
            ):

                self.link_images.append(
                    href
                )

        # ----------------------------------------------------
        # صور HTML
        # ----------------------------------------------------

        elif tag == "img":

            src = (
                attrs_dict.get(
                    "src"
                )
                or attrs_dict.get(
                    "data-src"
                )
                or attrs_dict.get(
                    "data-original"
                )
                or attrs_dict.get(
                    "data-lazy-src"
                )
                or attrs_dict.get(
                    "data-lazy"
                )
                or ""
            ).strip()

            if src:

                self.img_images.append(
                    src
                )

        # ----------------------------------------------------
        # فيديو
        # ----------------------------------------------------

        elif tag in (
            "video",
            "iframe",
            "source",
        ):

            self.has_video = True

        # ----------------------------------------------------
        # Article
        # ----------------------------------------------------

        elif tag in (
            "article",
            "main",
        ):

            self.in_article += 1

        # ----------------------------------------------------
        # JSON-LD
        # ----------------------------------------------------

        elif tag == "script":

            script_type = (
                attrs_dict.get(
                    "type",
                    ""
                )
                or ""
            ).lower().strip()

            if (
                "ld+json"
                in script_type
            ):

                self.current_script_type = (
                    script_type
                )

                self.current_script_data = []

    # --------------------------------------------------------
    # نص داخل العنصر
    # --------------------------------------------------------

    def handle_data(
        self,
        data
    ):

        if self.current_script_type:

            self.current_script_data.append(
                data
            )

    # --------------------------------------------------------
    # نهاية العنصر
    # --------------------------------------------------------

    def handle_endtag(
        self,
        tag
    ):

        tag = tag.lower()

        if tag == "script":

            if self.current_script_type:

                content = "".join(
                    self.current_script_data
                ).strip()

                if content:

                    self.json_ld_blocks.append(
                        content
                    )

            self.current_script_type = None

            self.current_script_data = []

        elif tag in (
            "article",
            "main",
        ):

            if self.in_article > 0:

                self.in_article -= 1


# ============================================================
# استخراج الصور من JSON-LD
# ============================================================

def extract_json_ld_images(
    json_blocks
):

    images = []

    def collect_images(
        value
    ):

        # ----------------------------------------------------
        # String
        # ----------------------------------------------------

        if isinstance(
            value,
            str
        ):

            value = value.strip()

            if (
                value.startswith(
                    "http://"
                )
                or value.startswith(
                    "https://"
                )
                or value.startswith(
                    "//"
                )
                or value.startswith(
                    "/"
                )
            ):

                images.append(
                    value
                )

            return

        # ----------------------------------------------------
        # List
        # ----------------------------------------------------

        if isinstance(
            value,
            list
        ):

            for item in value:

                collect_images(
                    item
                )

            return

        # ----------------------------------------------------
        # Dictionary
        # ----------------------------------------------------

        if isinstance(
            value,
            dict
        ):

            # image
            if "image" in value:

                collect_images(
                    value["image"]
                )

            # thumbnailUrl
            if "thumbnailUrl" in value:

                collect_images(
                    value["thumbnailUrl"]
                )

            # contentUrl
            if "contentUrl" in value:

                collect_images(
                    value["contentUrl"]
                )

            return

    for block in json_blocks:

        try:

            data = json.loads(
                block
            )

            collect_images(
                data
            )

        except Exception:

            continue

    return images


# ============================================================
# اختيار صورة مناسبة من HTML
# ============================================================

def extract_page_image(
    html,
    article_url
):

    parser = SourceImageParser()

    try:

        parser.feed(
            html
        )

    except Exception as error:

        print(
            "⚠️ HTML parsing warning:",
            error
        )

    # --------------------------------------------------------
    # إذا كانت الصفحة فيديو بوضوح
    # --------------------------------------------------------

    is_video_page = (
        parser.og_type.startswith(
            "video"
        )
        or parser.og_type in (
            "video",
            "video.other",
            "video.movie",
            "video.episode",
            "video.tv_show",
        )
    )

    # --------------------------------------------------------
    # JSON-LD
    # --------------------------------------------------------

    json_ld_images = (
        extract_json_ld_images(
            parser.json_ld_blocks
        )
    )

    # --------------------------------------------------------
    # الأولوية:
    #
    # og:image
    # twitter:image
    # JSON-LD
    # image_src
    # img
    # --------------------------------------------------------

    candidates = []

    # إذا كانت الصفحة فيديو فقط
    # لا نستخدم poster أو og:image الخاص بالفيديو.
    if not is_video_page:

        candidates.extend(
            parser.meta_images
        )

        candidates.extend(
            json_ld_images
        )

        candidates.extend(
            parser.link_images
        )

        candidates.extend(
            parser.img_images
        )

    # --------------------------------------------------------
    # تنظيف واختيار أول صورة صالحة
    # --------------------------------------------------------

    unique_candidates = []

    for candidate in candidates:

        candidate = make_absolute_url(
            candidate,
            article_url
        )

        if not candidate:
            continue

        if is_video_url(
            candidate
        ):
            continue

        if is_ignored_image(
            candidate
        ):
            continue

        if candidate not in unique_candidates:

            unique_candidates.append(
                candidate
            )

    # --------------------------------------------------------
    # إرجاع أول صورة
    # --------------------------------------------------------

    if unique_candidates:

        return unique_candidates[0]

    # --------------------------------------------------------
    # إذا لم توجد صورة وكان هناك فيديو
    # --------------------------------------------------------

    if (
        is_video_page
        or parser.has_video
    ):

        return None

    return None


# ============================================================
# جلب صفحة الخبر
# ============================================================

def fetch_article_page(
    article_url
):

    if not article_url:

        return None

    try:

        response = requests.get(
            article_url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": (
                    "text/html,"
                    "application/xhtml+xml,"
                    "application/xml;q=0.9,"
                    "*/*;q=0.8"
                ),
                "Accept-Language": (
                    "en-US,en;q=0.9"
                ),
            },
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True,
        )

        response.raise_for_status()

        content_type = (
            response.headers.get(
                "Content-Type",
                ""
            ).lower()
        )

        if (
            "text/html"
            not in content_type
            and "application/xhtml"
            not in content_type
        ):

            print(
                "⚠️ Source page is not HTML."
            )

            return None

        return response.text

    except requests.RequestException as error:

        print(
            "⚠️ Failed to fetch article page:",
            error
        )

        return None

    except Exception as error:

        print(
            "⚠️ Unexpected article page error:",
            error
        )

        return None


# ============================================================
# تنزيل الصورة والتحقق منها
# ============================================================

def download_image(
    image_url,
    title
):

    if not image_url:

        return None

    if is_video_url(
        image_url
    ):

        print(
            "⚠️ Media URL is a video."
        )

        return None

    if is_ignored_image(
        image_url
    ):

        print(
            "⚠️ Ignored image URL."
        )

        return None

    try:

        response = requests.get(
            image_url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": (
                    "image/avif,image/webp,"
                    "image/apng,image/svg+xml,"
                    "image/*,*/*;q=0.8"
                ),
            },
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True,
        )

        response.raise_for_status()

        # ----------------------------------------------------
        # التحقق من Content-Type
        # ----------------------------------------------------

        content_type = (
            response.headers.get(
                "Content-Type",
                ""
            ).lower()
        )

        if not content_type.startswith(
            "image/"
        ):

            print(
                "⚠️ URL did not return an image."
            )

            return None

        # ----------------------------------------------------
        # فتح الصورة بواسطة Pillow
        # ----------------------------------------------------

        image_data = response.content

        if not image_data:

            return None

        try:

            image = Image.open(
                BytesIO(image_data)
            )

            image.load()

        except Exception as error:

            print(
                "⚠️ Invalid image:",
                error
            )

            return None

        # ----------------------------------------------------
        # التحقق من الحجم
        # ----------------------------------------------------

        width, height = image.size

        if (
            width < 200
            or height < 120
        ):

            print(
                f"⚠️ Image too small: "
                f"{width}x{height}"
            )

            return None

        # ----------------------------------------------------
        # تجهيز الصورة
        # ----------------------------------------------------

        if image.mode in (
            "RGBA",
            "LA",
            "P",
        ):

            background = Image.new(
                "RGB",
                image.size,
                "white"
            )

            if image.mode == "P":

                image = image.convert(
                    "RGBA"
                )

            background.paste(
                image,
                mask=(
                    image.getchannel("A")
                    if "A" in image.getbands()
                    else None
                ),
            )

            image = background

        else:

            image = image.convert(
                "RGB"
            )

        # ----------------------------------------------------
        # اسم فريد للصورة
        # ----------------------------------------------------

        title_part = safe_filename(
            title
        )

        url_hash = hashlib.sha1(
            image_url.encode(
                "utf-8",
                errors="ignore"
            )
        ).hexdigest()[:12]

        filename = (
            f"{title_part}_"
            f"{url_hash}.jpg"
        )

        ensure_image_directory()

        output_path = os.path.join(
            IMAGE_DIR,
            filename
        )

        # ----------------------------------------------------
        # حفظ JPEG
        # ----------------------------------------------------

        image.save(
            output_path,
            "JPEG",
            quality=92,
            optimize=True
        )

        # ----------------------------------------------------
        # التأكد من وجود الملف
        # ----------------------------------------------------

        if not os.path.exists(
            output_path
        ):

            return None

        print(
            f"✅ Source image downloaded: "
            f"{output_path}"
        )

        print(
            f"   Size: {width}x{height}"
        )

        return output_path

    except requests.RequestException as error:

        print(
            "⚠️ Failed to download image:",
            error
        )

        return None

    except Exception as error:

        print(
            "⚠️ Image processing error:",
            error
        )

        return None


# ============================================================
# الدالة الرئيسية
# ============================================================

def fetch_news_image(
    title,
    keywords=None,
    article_url=None,
    image_url=None,
    media_type=None
):

    print()
    print(
        "==================================="
    )
    print(
        "SOURCE IMAGE FETCHER"
    )
    print(
        "==================================="
    )

    print(
        f"📰 Title: {title}"
    )

    # --------------------------------------------------------
    # المرحلة الأولى:
    # صورة RSS
    # --------------------------------------------------------

    if image_url:

        print(
            "📡 RSS image found."
        )

        image_url = make_absolute_url(
            image_url,
            article_url
        )

        # ----------------------------------------------------
        # إذا كانت RSS تشير إلى فيديو
        # ----------------------------------------------------

        if (
            media_type == "video"
            and not image_url
        ):

            print(
                "🎥 RSS item is video only."
            )

            return None

        # ----------------------------------------------------
        # إذا كان الرابط نفسه فيديو
        # ----------------------------------------------------

        if is_video_url(
            image_url
        ):

            print(
                "🎥 RSS media is video."
            )

            return None

        # ----------------------------------------------------
        # محاولة تنزيل صورة RSS
        # ----------------------------------------------------

        downloaded_path = download_image(
            image_url=image_url,
            title=title,
        )

        if downloaded_path:

            return {
                "image_path": downloaded_path,
                "image_url": image_url,
                "source_url": article_url,
                "license": None,
                "artist": None,
                "title": title,
            }

        print(
            "⚠️ RSS image could not be downloaded."
        )

    # --------------------------------------------------------
    # المرحلة الثانية:
    # إذا كان RSS يقول فيديو ولا توجد صورة
    # --------------------------------------------------------

    if (
        media_type == "video"
        and not image_url
    ):

        print(
            "🎥 Source contains video only."
        )

        print(
            "➡️ No external image search will be used."
        )

        return None

    # --------------------------------------------------------
    # المرحلة الثالثة:
    # فحص صفحة الخبر الأصلية
    # --------------------------------------------------------

    if article_url:

        print(
            "🌐 Checking original article page..."
        )

        html = fetch_article_page(
            article_url
        )

        if html:

            page_image_url = extract_page_image(
                html,
                article_url
            )

            if page_image_url:

                print(
                    "🖼️ Image found on original article page."
                )

                downloaded_path = download_image(
                    image_url=page_image_url,
                    title=title,
                )

                if downloaded_path:

                    return {
                        "image_path": downloaded_path,
                        "image_url": page_image_url,
                        "source_url": article_url,
                        "license": None,
                        "artist": None,
                        "title": title,
                    }

                print(
                    "⚠️ Article image could not be downloaded."
                )

            else:

                print(
                    "⚠️ No suitable image found on article page."
                )

    # --------------------------------------------------------
    # لا توجد صورة
    # --------------------------------------------------------

    print(
        "❌ No source image available."
    )

    print(
        "➡️ Returning None for logo fallback."
    )

    return None

import os
import re

from PIL import (
    Image,
    ImageDraw,
    ImageFont,
    ImageFilter,
    ImageOps,
)

import arabic_reshaper
from bidi.algorithm import get_display


# ============================================================
# 1. المسارات والإعدادات
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

IMAGE_WIDTH = 1080
IMAGE_HEIGHT = 1080

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "generated_images"
)

PAGE_NAME = "نبض مدريد"

FONT_FILE = os.path.join(
    BASE_DIR,
    "Cairo-Bold.ttf"
)


# ============================================================
# 2. الألوان
# ============================================================

BACKGROUND_DARK = (8, 10, 16)
BACKGROUND_MID = (17, 21, 30)
BACKGROUND_CARD = (18, 22, 32)

ACCENT_RED = (220, 20, 50)
ACCENT_GOLD = (235, 180, 45)

WHITE = (255, 255, 255)
LIGHT_GRAY = (215, 218, 225)
MUTED_TEXT = (145, 150, 165)

BORDER = (75, 80, 95)


# ============================================================
# 3. تحميل الخط
# ============================================================

def load_font(size):
    """
    تحميل Cairo-Bold.ttf من نفس مجلد المشروع.
    """

    if os.path.isfile(FONT_FILE):
        try:
            return ImageFont.truetype(
                FONT_FILE,
                size
            )
        except Exception as error:
            print(
                f"⚠️ تعذر تحميل الخط: {error}"
            )

    print(
        f"⚠️ الخط غير موجود: {FONT_FILE}"
    )

    return ImageFont.load_default()


# ============================================================
# 4. معالجة العربية
# ============================================================

def fix_arabic(text):
    """
    تجهيز النص العربي للرسم باستخدام:
    arabic_reshaper + python-bidi
    """

    if text is None:
        return ""

    text = str(text).strip()

    if not text:
        return ""

    try:
        reshaped = arabic_reshaper.reshape(text)

        return get_display(
            reshaped
        )

    except Exception as error:
        print(
            f"⚠️ خطأ في معالجة العربية: {error}"
        )

        return text


# ============================================================
# 5. تنظيف النص
# ============================================================

def clean_text(text):

    if text is None:
        return ""

    text = str(text)

    # إزالة المسافات الزائدة
    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


# ============================================================
# 6. حساب عرض النص العربي بعد المعالجة
# ============================================================

def get_text_size(
    draw,
    text,
    font
):

    fixed_text = fix_arabic(
        text
    )

    if not fixed_text:
        return 0, 0

    bbox = draw.textbbox(
        (0, 0),
        fixed_text,
        font=font
    )

    width = (
        bbox[2] - bbox[0]
    )

    height = (
        bbox[3] - bbox[1]
    )

    return width, height


# ============================================================
# 7. رسم النص العربي من اليمين
# ============================================================

def draw_arabic_text(
    draw,
    text,
    right_x,
    top_y,
    font,
    fill=WHITE
):

    text = clean_text(
        text
    )

    if not text:
        return

    fixed_text = fix_arabic(
        text
    )

    bbox = draw.textbbox(
        (0, 0),
        fixed_text,
        font=font
    )

    text_width = (
        bbox[2] - bbox[0]
    )

    # محاذاة يدوية من اليمين
    x = (
        right_x
        -
        text_width
    )

    draw.text(
        (
            x,
            top_y
        ),
        fixed_text,
        font=font,
        fill=fill
    )


# ============================================================
# 8. اسم ملف آمن
# ============================================================

def safe_filename(text):

    text = clean_text(
        text
    )

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

    text = re.sub(
        r"_+",
        "_",
        text
    )

    if not text:
        text = "news_card"

    return text[:80]


# ============================================================
# 9. الخلفية
# ============================================================

def create_modern_background():

    image = Image.new(
        "RGB",
        (
            IMAGE_WIDTH,
            IMAGE_HEIGHT
        ),
        BACKGROUND_DARK
    )

    draw = ImageDraw.Draw(
        image
    )

    # --------------------------------------------------------
    # تدرج الخلفية
    # --------------------------------------------------------

    for y in range(
        IMAGE_HEIGHT
    ):

        ratio = (
            y /
            (IMAGE_HEIGHT - 1)
        )

        r = int(
            BACKGROUND_DARK[0]
            +
            (
                BACKGROUND_MID[0]
                -
                BACKGROUND_DARK[0]
            )
            *
            ratio
        )

        g = int(
            BACKGROUND_DARK[1]
            +
            (
                BACKGROUND_MID[1]
                -
                BACKGROUND_DARK[1]
            )
            *
            ratio
        )

        b = int(
            BACKGROUND_DARK[2]
            +
            (
                BACKGROUND_MID[2]
                -
                BACKGROUND_DARK[2]
            )
            *
            ratio
        )

        draw.line(
            (
                0,
                y,
                IMAGE_WIDTH,
                y
            ),
            fill=(
                r,
                g,
                b
            )
        )

    # --------------------------------------------------------
    # Glow
    # --------------------------------------------------------

    glow = Image.new(
        "RGBA",
        (
            IMAGE_WIDTH,
            IMAGE_HEIGHT
        ),
        (
            0,
            0,
            0,
            0
        )
    )

    glow_draw = ImageDraw.Draw(
        glow
    )

    glow_draw.ellipse(
        (
            -250,
            -250,
            500,
            500
        ),
        fill=(
            *ACCENT_RED,
            50
        )
    )

    glow_draw.ellipse(
        (
            650,
            700,
            1250,
            1300
        ),
        fill=(
            *ACCENT_RED,
            35
        )
    )

    glow_draw.ellipse(
        (
            650,
            -200,
            1200,
            300
        ),
        fill=(
            *ACCENT_GOLD,
            18
        )
    )

    glow = glow.filter(
        ImageFilter.GaussianBlur(
            110
        )
    )

    image = Image.alpha_composite(
        image.convert("RGBA"),
        glow
    ).convert("RGB")

    # --------------------------------------------------------
    # الخطوط الهندسية
    # --------------------------------------------------------

    draw = ImageDraw.Draw(
        image
    )

    for x in range(
        -400,
        IMAGE_WIDTH + 600,
        160
    ):

        draw.line(
            (
                x,
                0,
                x - 420,
                IMAGE_HEIGHT
            ),
            fill=(
                45,
                49,
                60
            ),
            width=1
        )

    return image


# ============================================================
# 10. العثور على الشعار
# ============================================================

def find_logo_file():

    candidates = [
        "logo.jpg",
        "logo.jpeg",
        "logo.png",
        "logo.webp",
        "LOGO.JPG",
        "LOGO.PNG",
    ]

    for filename in candidates:

        path = os.path.join(
            BASE_DIR,
            filename
        )

        if os.path.isfile(path):
            return path

    return None


# ============================================================
# 11. تحميل صورة الخبر
# ============================================================

def load_news_image(
    image_path,
    width,
    height
):

    if not image_path:
        return None

    if not os.path.isabs(
        image_path
    ):

        image_path = os.path.join(
            BASE_DIR,
            image_path
        )

    if not os.path.isfile(
        image_path
    ):
        print(
            f"⚠️ الصورة غير موجودة: {image_path}"
        )

        return None

    try:

        photo = Image.open(
            image_path
        ).convert("RGB")

        photo = ImageOps.fit(
            photo,
            (
                width,
                height
            ),
            method=Image.Resampling.LANCZOS
        )

        return photo

    except Exception as error:

        print(
            f"⚠️ تعذر فتح صورة الخبر: {error}"
        )

        return None


# ============================================================
# 12. إنشاء قناع دائري للشعار
# ============================================================

def create_circle_mask(
    width,
    height
):

    mask = Image.new(
        "L",
        (
            width,
            height
        ),
        0
    )

    draw = ImageDraw.Draw(
        mask
    )

    draw.ellipse(
        (
            0,
            0,
            width - 1,
            height - 1
        ),
        fill=255
    )

    return mask


# ============================================================
# 13. مربع الصورة الرئيسي
# ============================================================

def add_main_content_image(
    image,
    image_path=None
):

    x1 = 60
    y1 = 155
    x2 = 1020
    y2 = 640

    width = x2 - x1
    height = y2 - y1

    # ========================================================
    # الحالة الأولى:
    # توجد صورة حقيقية للخبر
    # ========================================================

    news_photo = load_news_image(
        image_path,
        width,
        height
    )

    if news_photo is not None:

        mask = Image.new(
            "L",
            (
                width,
                height
            ),
            0
        )

        ImageDraw.Draw(
            mask
        ).rounded_rectangle(
            (
                0,
                0,
                width,
                height
            ),
            radius=30,
            fill=255
        )

        image.paste(
            news_photo,
            (
                x1,
                y1
            ),
            mask
        )

        draw = ImageDraw.Draw(
            image
        )

        draw.rounded_rectangle(
            (
                x1,
                y1,
                x2,
                y2
            ),
            radius=30,
            outline=BORDER,
            width=2
        )

        # شريط أحمر علوي
        draw.rounded_rectangle(
            (
                x1,
                y1,
                x1 + 170,
                y1 + 8
            ),
            radius=4,
            fill=ACCENT_RED
        )

        print(
            "🖼️ تم استخدام صورة الخبر."
        )

        return

    # ========================================================
    # الحالة الثانية:
    # لا توجد صورة
    # نستخدم شعار الصفحة
    # ========================================================

    print(
        "ℹ️ لا توجد صورة للخبر."
    )

    print(
        "🛡️ سيتم استخدام شعار الصفحة."
    )

    card = Image.new(
        "RGB",
        (
            width,
            height
        ),
        BACKGROUND_CARD
    )

    # --------------------------------------------------------
    # Glow خلف الشعار
    # --------------------------------------------------------

    glow = Image.new(
        "RGBA",
        (
            width,
            height
        ),
        (
            0,
            0,
            0,
            0
        )
    )

    glow_draw = ImageDraw.Draw(
        glow
    )

    glow_draw.ellipse(
        (
            width // 2 - 260,
            height // 2 - 260,
            width // 2 + 260,
            height // 2 + 260
        ),
        fill=(
            *ACCENT_RED,
            35
        )
    )

    glow = glow.filter(
        ImageFilter.GaussianBlur(
            80
        )
    )

    card = Image.alpha_composite(
        card.convert("RGBA"),
        glow
    ).convert("RGB")

    # --------------------------------------------------------
    # الشعار
    # --------------------------------------------------------

    logo_path = find_logo_file()

    if logo_path:

        try:

            logo = Image.open(
                logo_path
            ).convert("RGBA")

            # نريد الشعار واضحًا وكبيرًا
            max_logo_size = min(
                width,
                height
            ) - 90

            logo = ImageOps.contain(
                logo,
                (
                    max_logo_size,
                    max_logo_size
                ),
                method=Image.Resampling.LANCZOS
            )

            # ------------------------------------------------
            # إذا كان الشعار أصغر من المطلوب،
            # نضمن أن يكون حجمه واضحًا
            # ------------------------------------------------

            min_logo_size = 260

            if logo.width < min_logo_size:

                target = min_logo_size

                logo = ImageOps.contain(
                    logo,
                    (
                        target,
                        target
                    ),
                    method=Image.Resampling.LANCZOS
                )

            logo_x = (
                (width - logo.width)
                // 2
            )

            logo_y = (
                (height - logo.height)
                // 2
            )

            # ------------------------------------------------
            # ظل الشعار
            # ------------------------------------------------

            shadow = Image.new(
                "RGBA",
                logo.size,
                (
                    0,
                    0,
                    0,
                    0
                )
            )

            shadow_draw = ImageDraw.Draw(
                shadow
            )

            shadow_draw.rectangle(
                (
                    10,
                    10,
                    logo.width - 10,
                    logo.height - 10
                ),
                fill=(
                    0,
                    0,
                    0,
                    120
                )
            )

            shadow = shadow.filter(
                ImageFilter.GaussianBlur(
                    18
                )
            )

            card.paste(
                shadow,
                (
                    logo_x + 8,
                    logo_y + 12
                ),
                shadow
            )

            # ------------------------------------------------
            # الشعار
            # ------------------------------------------------

            card.paste(
                logo,
                (
                    logo_x,
                    logo_y
                ),
                logo
            )

        except Exception as error:

            print(
                f"⚠️ خطأ في الشعار: {error}"
            )

    else:

        # ----------------------------------------------------
        # fallback أخير
        # ----------------------------------------------------

        print(
            "⚠️ logo.jpg غير موجود."
        )

        font = load_font(
            52
        )

        text = fix_arabic(
            PAGE_NAME
        )

        bbox = ImageDraw.Draw(
            card
        ).textbbox(
            (0, 0),
            text,
            font=font
        )

        tw = (
            bbox[2] - bbox[0]
        )

        th = (
            bbox[3] - bbox[1]
        )

        ImageDraw.Draw(
            card
        ).text(
            (
                (width - tw) // 2,
                (height - th) // 2
            ),
            text,
            font=font,
            fill=WHITE
        )

    # --------------------------------------------------------
    # وضع البطاقة
    # --------------------------------------------------------

    mask = Image.new(
        "L",
        (
            width,
            height
        ),
        0
    )

    ImageDraw.Draw(
        mask
    ).rounded_rectangle(
        (
            0,
            0,
            width,
            height
        ),
        radius=30,
        fill=255
    )

    image.paste(
        card,
        (
            x1,
            y1
        ),
        mask
    )

    draw = ImageDraw.Draw(
        image
    )

    draw.rounded_rectangle(
        (
            x1,
            y1,
            x2,
            y2
        ),
        radius=30,
        outline=BORDER,
        width=2
    )

    draw.rounded_rectangle(
        (
            x1,
            y1,
            x1 + 170,
            y1 + 8
        ),
        radius=4,
        fill=ACCENT_GOLD
    )


# ============================================================
# 14. الهيدر
# ============================================================

def draw_header(
    image
):

    draw = ImageDraw.Draw(
        image
    )

    # --------------------------------------------------------
    # الشعار العلوي
    # --------------------------------------------------------

    logo_size = 64

    logo_x = 952
    logo_y = 45

    logo_path = find_logo_file()

    if logo_path:

        try:

            logo = Image.open(
                logo_path
            ).convert("RGBA")

            logo = ImageOps.fit(
                logo,
                (
                    logo_size,
                    logo_size
                ),
                method=Image.Resampling.LANCZOS
            )

            mask = create_circle_mask(
                logo_size,
                logo_size
            )

            draw.ellipse(
                (
                    logo_x - 4,
                    logo_y - 4,
                    logo_x + logo_size + 4,
                    logo_y + logo_size + 4
                ),
                outline=ACCENT_GOLD,
                width=2
            )

            image.paste(
                logo,
                (
                    logo_x,
                    logo_y
                ),
                mask
            )

        except Exception as error:

            print(
                f"⚠️ خطأ في شعار الهيدر: {error}"
            )

    # --------------------------------------------------------
    # اسم الصفحة
    # --------------------------------------------------------

    page_font = load_font(
        38
    )

    draw_arabic_text(
        draw,
        PAGE_NAME,
        930,
        53,
        page_font,
        WHITE
    )

    # --------------------------------------------------------
    # الزخرفة
    # --------------------------------------------------------

    draw.rounded_rectangle(
        (
            60,
            62,
            180,
            70
        ),
        radius=4,
        fill=ACCENT_RED
    )

    draw.ellipse(
        (
            190,
            58,
            202,
            70
        ),
        fill=ACCENT_GOLD
    )


# ============================================================
# 15. تصنيف الخبر
# ============================================================

def get_category_label(
    category
):

    labels = {

        "football":
            "كرة القدم",

        "real_madrid":
            "ريال مدريد",

        "barcelona":
            "برشلونة",

        "atletico_madrid":
            "أتلتيكو مدريد",

        "world_football":
            "كرة عالمية",

        "transfers":
            "انتقالات",

        "injuries":
            "إصابات",

        "matches":
            "مباريات",

        "breaking":
            "عاجل",
    }

    return labels.get(
        category,
        "كرة القدم"
    )


# ============================================================
# 16. بناء سطور العنوان
# ============================================================

def build_title_lines(
    draw,
    title,
    font,
    max_width,
    max_lines=3
):

    title = clean_text(
        title
    )

    if not title:
        return []

    words = title.split()

    lines = []

    current = ""

    for word in words:

        if not current:

            candidate = word

        else:

            candidate = (
                current
                +
                " "
                +
                word
            )

        width, _ = get_text_size(
            draw,
            candidate,
            font
        )

        if width <= max_width:

            current = candidate

        else:

            if current:

                lines.append(
                    current
                )

            current = word

    if current:

        lines.append(
            current
        )

    # --------------------------------------------------------
    # لا نتجاوز 3 أسطر
    # --------------------------------------------------------

    if len(lines) <= max_lines:

        return lines

    # --------------------------------------------------------
    # دمج ما تبقى في السطر الثالث
    # --------------------------------------------------------

    first_lines = lines[
        :max_lines - 1
    ]

    remaining = " ".join(
        lines[
            max_lines - 1:
        ]
    )

    # حاول إدخال أكبر قدر ممكن
    # من السطر الأخير
    last_line = ""

    for word in remaining.split():

        candidate = (
            word
            if not last_line
            else
            last_line
            +
            " "
            +
            word
        )

        width, _ = get_text_size(
            draw,
            candidate,
            font
        )

        if width <= max_width:

            last_line = candidate

        else:

            break

    if not last_line:

        last_line = (
            remaining
        )

    if len(
        " ".join(
            first_lines
            +
            [last_line]
        )
    ) < len(title):

        last_line += "…"

    return (
        first_lines
        +
        [last_line]
    )


# ============================================================
# 17. جسم الخبر
# ============================================================

def draw_news_body(
    image,
    title,
    category
):

    draw = ImageDraw.Draw(
        image
    )

    # --------------------------------------------------------
    # شارة التصنيف
    # --------------------------------------------------------

    category_text = get_category_label(
        category
    )

    category_font = load_font(
        25
    )

    category_fixed = fix_arabic(
        category_text
    )

    bbox = draw.textbbox(
        (
            0,
            0
        ),
        category_fixed,
        font=category_font
    )

    category_width = (
        bbox[2] - bbox[0]
    )

    category_height = (
        bbox[3] - bbox[1]
    )

    padding_x = 26
    padding_y = 10

    badge_width = (
        category_width
        +
        padding_x * 2
    )

    badge_height = (
        category_height
        +
        padding_y * 2
    )

    badge_right = 1020
    badge_left = (
        badge_right
        -
        badge_width
    )

    badge_top = 675
    badge_bottom = (
        badge_top
        +
        badge_height
    )

    draw.rounded_rectangle(
        (
            badge_left,
            badge_top,
            badge_right,
            badge_bottom
        ),
        radius=16,
        fill=ACCENT_RED
    )

    draw_arabic_text(
        draw,
        category_text,
        badge_right - padding_x,
        badge_top + padding_y - 2,
        category_font,
        WHITE
    )

    # --------------------------------------------------------
    # العنوان
    # --------------------------------------------------------

    max_width = 920

    font_candidates = [
        46,
        42,
        38,
        35,
        32
    ]

    selected_font = None
    selected_lines = []

    for size in font_candidates:

        font = load_font(
            size
        )

        lines = build_title_lines(
            draw,
            title,
            font,
            max_width,
            3
        )

        if len(lines) <= 3:

            selected_font = font
            selected_lines = lines

            break

    if selected_font is None:

        selected_font = load_font(
            32
        )

        selected_lines = build_title_lines(
            draw,
            title,
            selected_font,
            max_width,
            3
        )

    # --------------------------------------------------------
    # رسم العنوان
    # --------------------------------------------------------

    line_height = int(
        selected_font.size
        *
        1.45
    )

    start_y = 755

    for line in selected_lines:

        draw_arabic_text(
            draw,
            line,
            1020,
            start_y,
            selected_font,
            WHITE
        )

        start_y += line_height


# ============================================================
# 18. التذييل
# ============================================================

def draw_footer(
    image
):

    draw = ImageDraw.Draw(
        image
    )

    y = 995

    draw.line(
        (
            60,
            y,
            1020,
            y
        ),
        fill=(
            60,
            65,
            80
        ),
        width=1
    )

    draw.rounded_rectangle(
        (
            60,
            y - 2,
            180,
            y + 2
        ),
        radius=2,
        fill=ACCENT_RED
    )

    footer_font = load_font(
        21
    )

    footer = (
        PAGE_NAME
        +
        " • المصدر الرسمي"
    )

    draw_arabic_text(
        draw,
        footer,
        1020,
        y + 15,
        footer_font,
        MUTED_TEXT
    )


# ============================================================
# 19. الدالة الرئيسية
# ============================================================

def generate_news_image(
    title,
    category="football",
    image_path=None,
    output_path=None
):

    title = clean_text(
        title
    )

    if not title:

        title = "خبر رياضي"

    # --------------------------------------------------------
    # الخلفية
    # --------------------------------------------------------

    image = create_modern_background()

    # --------------------------------------------------------
    # الهيدر
    # --------------------------------------------------------

    draw_header(
        image
    )

    # --------------------------------------------------------
    # الصورة أو الشعار
    # --------------------------------------------------------

    add_main_content_image(
        image,
        image_path
    )

    # --------------------------------------------------------
    # النص
    # --------------------------------------------------------

    draw_news_body(
        image,
        title,
        category
    )

    # --------------------------------------------------------
    # التذييل
    # --------------------------------------------------------

    draw_footer(
        image
    )

    # --------------------------------------------------------
    # مجلد الإخراج
    # --------------------------------------------------------

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    # --------------------------------------------------------
    # اسم الملف
    # --------------------------------------------------------

    if output_path is None:

        filename = (
            safe_filename(title)
            +
            ".png"
        )

        output_path = os.path.join(
            OUTPUT_DIR,
            filename
        )

    elif not os.path.isabs(
        output_path
    ):

        output_path = os.path.join(
            BASE_DIR,
            output_path
        )

    # --------------------------------------------------------
    # حفظ الصورة
    # --------------------------------------------------------

    image.save(
        output_path,
        "PNG",
        optimize=True
    )

    print(
        f"✅ تم إنشاء الصورة: {output_path}"
    )

    return output_path


# ============================================================
# 20. اختبار الملف
# ============================================================

if __name__ == "__main__":

    test_title = (
        "ريال مدريد يستعد لمواجهة قوية "
        "في الدوري الإسباني"
    )

    generate_news_image(
        title=test_title,
        category="real_madrid",
        image_path=None
    )

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
# 1. المسارات الأساسية
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

LOGO_FILE = os.path.join(
    BASE_DIR,
    "logo.jpg"
)


# ============================================================
# 2. الألوان
# ============================================================

BACKGROUND_DARK = (10, 12, 18)
BACKGROUND_MID = (17, 21, 30)
BACKGROUND_CARD = (20, 24, 34)

ACCENT_RED = (220, 20, 50)
ACCENT_GOLD = (235, 180, 45)

WHITE = (255, 255, 255)
LIGHT_GRAY = (210, 215, 225)
MUTED_TEXT = (140, 145, 160)


# ============================================================
# 3. تحميل الخط
# ============================================================

def load_font(size):
    """
    تحميل Cairo-Bold الموجود بجانب bot.py.
    """

    if os.path.isfile(FONT_FILE):
        try:
            return ImageFont.truetype(
                FONT_FILE,
                size
            )
        except Exception as error:
            print(
                f"⚠️ تعذر تحميل Cairo-Bold.ttf: {error}"
            )

    print(
        "⚠️ لم يتم العثور على Cairo-Bold.ttf"
    )

    return ImageFont.load_default()


# ============================================================
# 4. معالجة النص العربي
# ============================================================

def fix_arabic(text):
    """
    تحويل النص العربي إلى الشكل المناسب للرسم بواسطة Pillow.
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
            f"⚠️ خطأ في معالجة النص العربي: {error}"
        )

        return text


# ============================================================
# 5. رسم النص من اليمين إلى اليسار
# ============================================================

def draw_rtl_text(
    draw,
    text,
    x,
    y,
    font,
    fill=WHITE
):
    """
    رسم النص العربي بمحاذاة يمين ثابتة.
    لا نعتمد على anchor=ra لأن بعض بيئات Pillow/Linux
    قد تتعامل معه بشكل غير متوقع مع النص المعالج بـ Bidi.
    """

    fixed_text = fix_arabic(text)

    if not fixed_text:
        return

    bbox = draw.textbbox(
        (0, 0),
        fixed_text,
        font=font
    )

    text_width = (
        bbox[2] - bbox[0]
    )

    draw.text(
        (
            x - text_width,
            y
        ),
        fixed_text,
        fill=fill,
        font=font
    )


# ============================================================
# 6. اسم ملف آمن
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

    text = re.sub(
        r"_+",
        "_",
        text
    )

    return (
        text[:80]
        if text
        else "news_card"
    )


# ============================================================
# 7. الخلفية الحديثة
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

    draw = ImageDraw.Draw(image)

    # --------------------------------------------------------
    # التدرج الرأسي
    # --------------------------------------------------------

    for y in range(IMAGE_HEIGHT):

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
            * ratio
        )

        g = int(
            BACKGROUND_DARK[1]
            +
            (
                BACKGROUND_MID[1]
                -
                BACKGROUND_DARK[1]
            )
            * ratio
        )

        b = int(
            BACKGROUND_DARK[2]
            +
            (
                BACKGROUND_MID[2]
                -
                BACKGROUND_DARK[2]
            )
            * ratio
        )

        draw.line(
            [
                (0, y),
                (IMAGE_WIDTH, y)
            ],
            fill=(r, g, b)
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
        (0, 0, 0, 0)
    )

    glow_draw = ImageDraw.Draw(glow)

    glow_draw.ellipse(
        (-250, -250, 500, 500),
        fill=(
            *ACCENT_RED,
            55
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
            40
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
            20
        )
    )

    glow = glow.filter(
        ImageFilter.GaussianBlur(110)
    )

    image = Image.alpha_composite(
        image.convert("RGBA"),
        glow
    ).convert("RGB")

    # --------------------------------------------------------
    # الخطوط الهندسية
    # --------------------------------------------------------

    draw = ImageDraw.Draw(image)

    for x in range(
        -400,
        IMAGE_WIDTH + 600,
        160
    ):

        draw.line(
            [
                (x, 0),
                (x - 420, IMAGE_HEIGHT)
            ],
            fill=(
                255,
                255,
                255
            ),
            width=1
        )

    # --------------------------------------------------------
    # طبقة داكنة
    # --------------------------------------------------------

    overlay = Image.new(
        "RGBA",
        (
            IMAGE_WIDTH,
            IMAGE_HEIGHT
        ),
        (
            10,
            12,
            18,
            190
        )
    )

    image = Image.alpha_composite(
        image.convert("RGBA"),
        overlay
    ).convert("RGB")

    return image


# ============================================================
# 8. إيجاد الشعار
# ============================================================

def find_logo_file():

    possible_files = [
        os.path.join(BASE_DIR, "logo.jpg"),
        os.path.join(BASE_DIR, "logo.png"),
        os.path.join(BASE_DIR, "logo.jpeg"),
        os.path.join(BASE_DIR, "logo.webp"),
        os.path.join(BASE_DIR, "LOGO.JPG"),
        os.path.join(BASE_DIR, "LOGO.PNG"),
    ]

    for path in possible_files:

        if os.path.isfile(path):
            return path

    return None


# ============================================================
# 9. تجهيز الشعار كصورة مربعة
# ============================================================

def prepare_logo(size):

    logo_path = find_logo_file()

    if not logo_path:
        return None

    try:

        logo = Image.open(
            logo_path
        ).convert("RGBA")

        logo = ImageOps.contain(
            logo,
            (
                size,
                size
            ),
            method=Image.Resampling.LANCZOS
        )

        return logo

    except Exception as error:

        print(
            f"⚠️ خطأ في تحميل الشعار: {error}"
        )

        return None


# ============================================================
# 10. صورة الخبر الحقيقية
# ============================================================

def load_real_image(
    image_path,
    width,
    height
):

    if not image_path:
        return None

    # إذا كان المسار نسبيًا
    if not os.path.isabs(image_path):

        image_path = os.path.join(
            BASE_DIR,
            image_path
        )

    if not os.path.isfile(image_path):

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
            f"⚠️ خطأ في فتح صورة الخبر: {error}"
        )

        return None


# ============================================================
# 11. مربع الصورة الرئيسي
# ============================================================

def add_main_content_image(
    image,
    image_path=None
):

    x1 = 60
    y1 = 160
    x2 = 1020
    y2 = 640

    width = x2 - x1
    height = y2 - y1

    # ========================================================
    # الحالة الأولى: صورة الخبر موجودة
    # ========================================================

    photo = load_real_image(
        image_path,
        width,
        height
    )

    if photo is not None:

        mask = Image.new(
            "L",
            (
                width,
                height
            ),
            0
        )

        mask_draw = ImageDraw.Draw(
            mask
        )

        mask_draw.rounded_rectangle(
            (
                0,
                0,
                width,
                height
            ),
            radius=28,
            fill=255
        )

        image.paste(
            photo,
            (
                x1,
                y1
            ),
            mask
        )

        draw = ImageDraw.Draw(
            image
        )

        # إطار الصورة
        draw.rounded_rectangle(
            (
                x1,
                y1,
                x2,
                y2
            ),
            radius=28,
            outline=(
                100,
                105,
                120
            ),
            width=2
        )

        # شريط أحمر صغير
        draw.rounded_rectangle(
            (
                x1,
                y1,
                x1 + 155,
                y1 + 8
            ),
            radius=4,
            fill=ACCENT_RED
        )

        print(
            "🖼️ تم استخدام صورة الخبر الأصلية."
        )

        return

    # ========================================================
    # الحالة الثانية: لا توجد صورة
    #
    # نستخدم شعار الصفحة داخل نفس مربع الصورة
    # ========================================================

    print(
        "ℹ️ لا توجد صورة للخبر، سيتم استخدام شعار الصفحة."
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
    # خلفية بسيطة للشعار
    # --------------------------------------------------------

    card_overlay = Image.new(
        "RGBA",
        (
            width,
            height
        ),
        (0, 0, 0, 0)
    )

    overlay_draw = ImageDraw.Draw(
        card_overlay
    )

    overlay_draw.ellipse(
        (
            width // 2 - 250,
            height // 2 - 250,
            width // 2 + 250,
            height // 2 + 250
        ),
        fill=(
            *ACCENT_RED,
            30
        )
    )

    card_overlay = card_overlay.filter(
        ImageFilter.GaussianBlur(80)
    )

    card = Image.alpha_composite(
        card.convert("RGBA"),
        card_overlay
    ).convert("RGB")

    # --------------------------------------------------------
    # الشعار
    # --------------------------------------------------------

    logo = prepare_logo(300)

    if logo is not None:

        logo_x = (
            x1
            +
            (width - logo.width) // 2
        )

        logo_y = (
            y1
            +
            (height - logo.height) // 2
        )

        # ظل خفيف
        shadow = Image.new(
            "RGBA",
            (
                logo.width + 30,
                logo.height + 30
            ),
            (0, 0, 0, 0)
        )

        shadow_blur = Image.new(
            "RGBA",
            shadow.size,
            (0, 0, 0, 0)
        )

        shadow_draw = ImageDraw.Draw(
            shadow_blur
        )

        shadow_draw.rounded_rectangle(
            (
                8,
                8,
                shadow.width - 8,
                shadow.height - 8
            ),
            radius=20,
            fill=(
                0,
                0,
                0,
                120
            )
        )

        shadow_blur = shadow_blur.filter(
            ImageFilter.GaussianBlur(15)
        )

        card.paste(
            shadow_blur,
            (
                logo_x - 15,
                logo_y - 15
            ),
            shadow_blur
        )

        card.paste(
            logo,
            (
                logo_x,
                logo_y
            ),
            logo
        )

    else:

        # ----------------------------------------------------
        # إذا لم يوجد logo.jpg إطلاقًا
        # ----------------------------------------------------

        print(
            "⚠️ لم يتم العثور على logo.jpg"
        )

        font = load_font(42)

        placeholder = fix_arabic(
            PAGE_NAME
        )

        bbox = ImageDraw.Draw(
            card
        ).textbbox(
            (0, 0),
            placeholder,
            font=font
        )

        text_width = (
            bbox[2] - bbox[0]
        )

        text_height = (
            bbox[3] - bbox[1]
        )

        ImageDraw.Draw(
            card
        ).text(
            (
                (width - text_width) // 2,
                (height - text_height) // 2
            ),
            placeholder,
            fill=WHITE,
            font=font
        )

    # --------------------------------------------------------
    # وضع البطاقة داخل التصميم
    # --------------------------------------------------------

    image.paste(
        card,
        (
            x1,
            y1
        )
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
        radius=28,
        outline=(
            80,
            85,
            100
        ),
        width=2
    )

    draw.rounded_rectangle(
        (
            x1,
            y1,
            x1 + 155,
            y1 + 8
        ),
        radius=4,
        fill=ACCENT_GOLD
    )


# ============================================================
# 12. الهيدر والشعار
# ============================================================

def draw_header_and_brand(image):

    draw = ImageDraw.Draw(
        image
    )

    logo_size = 64

    logo_x = 952
    logo_y = 50

    logo_path = find_logo_file()

    # --------------------------------------------------------
    # الشعار الدائري
    # --------------------------------------------------------

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

            mask = Image.new(
                "L",
                (
                    logo_size,
                    logo_size
                ),
                0
            )

            ImageDraw.Draw(
                mask
            ).ellipse(
                (
                    0,
                    0,
                    logo_size,
                    logo_size
                ),
                fill=255
            )

            draw.ellipse(
                (
                    logo_x - 3,
                    logo_y - 3,
                    logo_x + logo_size + 3,
                    logo_y + logo_size + 3
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
                f"⚠️ خطأ في قراءة الشعار: {error}"
            )

    else:

        draw.ellipse(
            (
                logo_x,
                logo_y,
                logo_x + logo_size,
                logo_y + logo_size
            ),
            outline=ACCENT_GOLD,
            width=3
        )

    # --------------------------------------------------------
    # اسم الصفحة
    # --------------------------------------------------------

    page_font = load_font(38)

    draw_rtl_text(
        draw,
        PAGE_NAME,
        930,
        58,
        page_font,
        WHITE
    )

    # --------------------------------------------------------
    # الزخرفة العلوية
    # --------------------------------------------------------

    draw.rounded_rectangle(
        (
            60,
            65,
            180,
            73
        ),
        radius=4,
        fill=ACCENT_RED
    )

    draw.ellipse(
        (
            190,
            61,
            202,
            73
        ),
        fill=ACCENT_GOLD
    )


# ============================================================
# 13. تصنيف الخبر
# ============================================================

def get_category_label(category):

    labels = {

        "transfers":
            "انتقالات",

        "injuries":
            "إصابات",

        "matches":
            "مباريات",

        "breaking":
            "عاجل",

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
    }

    return labels.get(
        category,
        "كرة القدم"
    )


# ============================================================
# 14. تقسيم العنوان العربي
# ============================================================

def split_title_into_lines(
    draw,
    title,
    font,
    max_width,
    max_lines=3
):

    words = str(title).split()

    if not words:
        return []

    lines = []

    current_line = ""

    for word in words:

        test_line = (
            word
            if not current_line
            else
            current_line
            + " "
            + word
        )

        fixed_line = fix_arabic(
            test_line
        )

        bbox = draw.textbbox(
            (0, 0),
            fixed_line,
            font=font
        )

        line_width = (
            bbox[2] - bbox[0]
        )

        if line_width <= max_width:

            current_line = test_line

        else:

            if current_line:
                lines.append(
                    current_line
                )

            current_line = word

    if current_line:
        lines.append(
            current_line
        )

    # --------------------------------------------------------
    # إذا تجاوز 3 أسطر، نختصر السطر الأخير
    # --------------------------------------------------------

    if len(lines) > max_lines:

        lines = lines[:max_lines]

        last = lines[-1].strip()

        if not last.endswith("..."):
            last += "..."

        lines[-1] = last

    return lines


# ============================================================
# 15. جسم الخبر
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

    category_font = load_font(26)

    fixed_category = fix_arabic(
        category_text
    )

    bbox = draw.textbbox(
        (0, 0),
        fixed_category,
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

    badge_x2 = 1020
    badge_x1 = (
        badge_x2
        -
        badge_width
    )

    badge_y1 = 675
    badge_y2 = (
        badge_y1
        +
        badge_height
    )

    draw.rounded_rectangle(
        (
            badge_x1,
            badge_y1,
            badge_x2,
            badge_y2
        ),
        radius=16,
        fill=ACCENT_RED
    )

    draw_rtl_text(
        draw,
        category_text,
        badge_x2 - padding_x,
        badge_y1 + padding_y - 2,
        category_font,
        WHITE
    )

    # --------------------------------------------------------
    # العنوان
    # --------------------------------------------------------

    max_width = 940

    font_sizes = [
        46,
        42,
        38,
        34
    ]

    selected_font = None
    selected_lines = []

    for font_size in font_sizes:

        font = load_font(
            font_size
        )

        lines = split_title_into_lines(
            draw,
            title,
            font,
            max_width,
            max_lines=3
        )

        # نستخدم أول حجم يعطي نتيجة مناسبة
        if len(lines) <= 3:

            selected_font = font
            selected_lines = lines

            break

    if selected_font is None:

        selected_font = load_font(
            34
        )

        selected_lines = split_title_into_lines(
            draw,
            title,
            selected_font,
            max_width,
            max_lines=3
        )

    # --------------------------------------------------------
    # رسم العنوان
    # --------------------------------------------------------

    font_size = selected_font.size

    line_spacing = int(
        font_size * 1.35
    )

    start_y = 755

    for line in selected_lines:

        draw_rtl_text(
            draw,
            line,
            1020,
            start_y,
            selected_font,
            WHITE
        )

        start_y += line_spacing


# ============================================================
# 16. التذييل
# ============================================================

def draw_footer(image):

    draw = ImageDraw.Draw(
        image
    )

    y = 1000

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

    font = load_font(22)

    footer_text = (
        PAGE_NAME
        +
        " • المصدر الرسمي"
    )

    draw_rtl_text(
        draw,
        footer_text,
        1020,
        y + 15,
        font,
        MUTED_TEXT
    )


# ============================================================
# 17. الدالة الرئيسية
# ============================================================

def generate_news_image(
    title,
    category="football",
    image_path=None,
    output_path=None
):

    # --------------------------------------------------------
    # إنشاء الخلفية
    # --------------------------------------------------------

    image = create_modern_background()

    # --------------------------------------------------------
    # الهيدر
    # --------------------------------------------------------

    draw_header_and_brand(
        image
    )

    # --------------------------------------------------------
    # صورة الخبر أو الشعار
    # --------------------------------------------------------

    add_main_content_image(
        image,
        image_path
    )

    # --------------------------------------------------------
    # عنوان وتصنيف الخبر
    # --------------------------------------------------------

    draw_news_body(
        image,
        title,
        category
    )

    # --------------------------------------------------------
    # Footer
    # --------------------------------------------------------

    draw_footer(
        image
    )

    # --------------------------------------------------------
    # إنشاء مجلد الصور
    # --------------------------------------------------------

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    # --------------------------------------------------------
    # اسم الملف
    # --------------------------------------------------------

    if not output_path:

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
    # الحفظ
    # --------------------------------------------------------

    image.save(
        output_path,
        "PNG",
        optimize=True
    )

    print(
        f"✅ تم إنشاء الصورة بنجاح: {output_path}"
    )

    return output_path


# ============================================================
# 18. اختبار مباشر
# ============================================================

if __name__ == "__main__":

    generate_news_image(
        title="ريال مدريد يستعد لمواجهة قوية في الدوري الإسباني",
        category="real_madrid",
        image_path=None
    )

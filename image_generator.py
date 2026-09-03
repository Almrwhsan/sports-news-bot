import os
import re

from PIL import (
    Image,
    ImageDraw,
    ImageFont,
    ImageFilter,
    ImageOps,
    features,
)


# ============================================================
# 1. إعدادات المشروع
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

BACKGROUND_DARK = (7, 9, 15)
BACKGROUND_MID = (17, 21, 30)
BACKGROUND_CARD = (15, 18, 27)

ACCENT_RED = (220, 20, 50)
ACCENT_RED_DARK = (145, 10, 32)

ACCENT_GOLD = (235, 180, 45)

WHITE = (255, 255, 255)
LIGHT_GRAY = (220, 223, 230)
MUTED_TEXT = (145, 150, 165)

BORDER = (70, 76, 92)


# ============================================================
# 3. فحص دعم العربية الحقيقي
# ============================================================

def has_raqm():
    """
    RAQM هو محرك Pillow الخاص بتخطيط النصوص المعقدة
    مثل العربية والاتجاه من اليمين إلى اليسار.
    """

    try:
        return bool(
            features.check("raqm")
        )
    except Exception:
        return False


RAQM_AVAILABLE = has_raqm()

print(
    "🔤 Arabic text engine:",
    "RAQM" if RAQM_AVAILABLE else "Fallback"
)


# ============================================================
# 4. تحميل الخط
# ============================================================

def load_font(size):

    if not os.path.isfile(FONT_FILE):

        print(
            f"❌ لم يتم العثور على الخط: {FONT_FILE}"
        )

        return ImageFont.load_default()

    try:

        return ImageFont.truetype(
            FONT_FILE,
            size
        )

    except Exception as error:

        print(
            f"❌ فشل تحميل Cairo-Bold.ttf: {error}"
        )

        return ImageFont.load_default()


# ============================================================
# 5. تنظيف النص
# ============================================================

def clean_text(text):

    if text is None:
        return ""

    text = str(text)

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
# 6. معرفة هل النص يحتوي على العربية
# ============================================================

def contains_arabic(text):

    if not text:
        return False

    return bool(
        re.search(
            r"[\u0600-\u06FF]",
            text
        )
    )


# ============================================================
# 7. تجهيز النص
# ============================================================

def prepare_text(text):

    text = clean_text(
        text
    )

    if not text:
        return ""

    return text


# ============================================================
# 8. رسم النص
# ============================================================

def draw_text(
    draw,
    position,
    text,
    font,
    fill=WHITE,
    anchor=None
):

    text = prepare_text(
        text
    )

    if not text:
        return

    x, y = position

    # --------------------------------------------------------
    # العربية مع RAQM
    # --------------------------------------------------------

    if contains_arabic(text) and RAQM_AVAILABLE:

        kwargs = {
            "font": font,
            "fill": fill,
            "direction": "rtl",
            "language": "ar",
            "align": "right",
        }

        if anchor is not None:
            kwargs["anchor"] = anchor

        draw.text(
            (x, y),
            text,
            **kwargs
        )

        return

    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    if contains_arabic(text):

        try:

            import arabic_reshaper
            from bidi.algorithm import get_display

            reshaped = (
                arabic_reshaper.reshape(
                    text
                )
            )

            visual_text = get_display(
                reshaped
            )

            draw.text(
                (x, y),
                visual_text,
                font=font,
                fill=fill,
                anchor=anchor
            )

            return

        except Exception as error:

            print(
                f"⚠️ Arabic fallback error: {error}"
            )

    # --------------------------------------------------------
    # النص العادي
    # --------------------------------------------------------

    draw.text(
        (x, y),
        text,
        font=font,
        fill=fill,
        anchor=anchor
    )


# ============================================================
# 9. قياس النص
# ============================================================

def text_width(
    draw,
    text,
    font
):

    text = prepare_text(
        text
    )

    if not text:
        return 0

    try:

        if (
            contains_arabic(text)
            and RAQM_AVAILABLE
        ):

            return int(
                draw.textlength(
                    text,
                    font=font,
                    direction="rtl",
                    language="ar"
                )
            )

        return int(
            draw.textlength(
                text,
                font=font
            )
        )

    except Exception:

        bbox = draw.textbbox(
            (0, 0),
            text,
            font=font
        )

        return (
            bbox[2] - bbox[0]
        )


# ============================================================
# 10. تقسيم العنوان
# ============================================================

def build_title_lines(
    draw,
    title,
    font,
    max_width,
    max_lines=3
):

    title = prepare_text(
        title
    )

    if not title:
        return []

    words = title.split()

    lines = []
    current = ""

    for word in words:

        candidate = (
            word
            if not current
            else current
            + " "
            + word
        )

        width = text_width(
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

    if len(lines) <= max_lines:

        return lines

    result = lines[
        :max_lines - 1
    ]

    remaining_words = lines[
        max_lines - 1:
    ]

    last_text = " ".join(
        remaining_words
    )

    last_line = ""

    for word in last_text.split():

        candidate = (
            word
            if not last_line
            else last_line
            + " "
            + word
        )

        width = text_width(
            draw,
            candidate,
            font
        )

        if width <= max_width:

            last_line = candidate

        else:

            break

    if not last_line:

        last_line = last_text

    if last_line != last_text:

        last_line = (
            last_line.rstrip()
            + "…"
        )

    result.append(
        last_line
    )

    return result


# ============================================================
# 11. اسم ملف آمن
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

        return "news_card"

    return text[:80]


# ============================================================
# 12. الخلفية الحديثة
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
    # Gradient
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
    # الإضاءة الخلفية
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
            -300,
            -300,
            480,
            480
        ),
        fill=(
            *ACCENT_RED,
            48
        )
    )

    glow_draw.ellipse(
        (
            700,
            700,
            1300,
            1300
        ),
        fill=(
            *ACCENT_RED,
            30
        )
    )

    glow_draw.ellipse(
        (
            680,
            -200,
            1200,
            320
        ),
        fill=(
            *ACCENT_GOLD,
            18
        )
    )

    glow = glow.filter(
        ImageFilter.GaussianBlur(
            115
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
        -500,
        IMAGE_WIDTH + 700,
        170
    ):

        draw.line(
            (
                x,
                0,
                x - 430,
                IMAGE_HEIGHT
            ),
            fill=(
                40,
                44,
                55
            ),
            width=1
        )

    # --------------------------------------------------------
    # خط علوي بسيط
    # --------------------------------------------------------

    draw.rectangle(
        (
            0,
            0,
            IMAGE_WIDTH,
            5
        ),
        fill=ACCENT_RED
    )

    return image


# ============================================================
# 13. العثور على الشعار
# ============================================================

def find_logo_file():

    filenames = [
        "logo.jpg",
        "logo.jpeg",
        "logo.png",
        "logo.webp",
        "LOGO.JPG",
        "LOGO.PNG"
    ]

    for filename in filenames:

        path = os.path.join(
            BASE_DIR,
            filename
        )

        if os.path.isfile(path):

            return path

    return None


# ============================================================
# 14. تحميل صورة الخبر
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
            f"⚠️ صورة الخبر غير موجودة: {image_path}"
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
            f"⚠️ خطأ في صورة الخبر: {error}"
        )

        return None


# ============================================================
# 15. تجهيز شعار الصفحة كخلفية كاملة
# ============================================================

def create_logo_fallback(
    width,
    height
):

    logo_path = find_logo_file()

    if not logo_path:

        print(
            "❌ لم يتم العثور على logo.jpg"
        )

        card = Image.new(
            "RGB",
            (
                width,
                height
            ),
            BACKGROUND_CARD
        )

        draw = ImageDraw.Draw(
            card
        )

        fallback_font = load_font(
            52
        )

        draw_text(
            draw,
            (
                width // 2,
                height // 2
            ),
            PAGE_NAME,
            fallback_font,
            WHITE,
            anchor="mm"
        )

        return card

    try:

        logo = Image.open(
            logo_path
        ).convert("RGB")

        # ----------------------------------------------------
        # الصورة تملأ المستطيل بالكامل
        # ----------------------------------------------------

        logo_background = ImageOps.fit(
            logo,
            (
                width,
                height
            ),
            method=Image.Resampling.LANCZOS
        )

        # ----------------------------------------------------
        # تغميق الصورة حتى لا تبدو كصورة عادية
        # بل كخلفية إعلامية
        # ----------------------------------------------------

        dark_layer = Image.new(
            "RGBA",
            (
                width,
                height
            ),
            (
                4,
                6,
                12,
                125
            )
        )

        logo_background = Image.alpha_composite(
            logo_background.convert("RGBA"),
            dark_layer
        )

        # ----------------------------------------------------
        # تدرج علوي وسفلي
        # ----------------------------------------------------

        gradient = Image.new(
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

        gradient_draw = ImageDraw.Draw(
            gradient
        )

        for y in range(
            height
        ):

            if y < height * 0.45:

                alpha = int(
                    70 *
                    (
                        1 -
                        y /
                        (height * 0.45)
                    )
                )

                gradient_draw.line(
                    (
                        0,
                        y,
                        width,
                        y
                    ),
                    fill=(
                        0,
                        0,
                        0,
                        alpha
                    )
                )

            else:

                alpha = int(
                    145 *
                    (
                        (y - height * 0.45)
                        /
                        (height * 0.55)
                    )
                )

                alpha = max(
                    0,
                    min(
                        alpha,
                        145
                    )
                )

                gradient_draw.line(
                    (
                        0,
                        y,
                        width,
                        y
                    ),
                    fill=(
                        3,
                        5,
                        10,
                        alpha
                    )
                )

        logo_background = Image.alpha_composite(
            logo_background,
            gradient
        )

        # ----------------------------------------------------
        # توهج أحمر خفيف
        # ----------------------------------------------------

        red_glow = Image.new(
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

        red_draw = ImageDraw.Draw(
            red_glow
        )

        red_draw.ellipse(
            (
                -180,
                height - 260,
                420,
                height + 220
            ),
            fill=(
                *ACCENT_RED,
                55
            )
        )

        red_glow = red_glow.filter(
            ImageFilter.GaussianBlur(
                80
            )
        )

        logo_background = Image.alpha_composite(
            logo_background,
            red_glow
        )

        # ----------------------------------------------------
        # شريط بصري علوي
        # ----------------------------------------------------

        overlay_draw = ImageDraw.Draw(
            logo_background
        )

        overlay_draw.rectangle(
            (
                0,
                0,
                width,
                9
            ),
            fill=(
                *ACCENT_RED,
                230
            )
        )

        # ----------------------------------------------------
        # إعادة RGB
        # ----------------------------------------------------

        return logo_background.convert(
            "RGB"
        )

    except Exception as error:

        print(
            f"⚠️ خطأ في تحميل logo.jpg: {error}"
        )

        return Image.new(
            "RGB",
            (
                width,
                height
            ),
            BACKGROUND_CARD
        )


# ============================================================
# 16. إضافة الصورة الرئيسية
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
    # صورة الخبر الحقيقية
    # ========================================================

    photo = load_news_image(
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

        ImageDraw.Draw(
            mask
        ).rounded_rectangle(
            (
                0,
                0,
                width,
                height
            ),
            radius=32,
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

        # ----------------------------------------------------
        # طبقة خفيفة أسفل الصورة
        # ----------------------------------------------------

        shadow = Image.new(
            "RGBA",
            image.size,
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

        shadow_draw.rounded_rectangle(
            (
                x1 + 5,
                y1 + 8,
                x2 + 5,
                y2 + 8
            ),
            radius=32,
            fill=(
                0,
                0,
                0,
                100
            )
        )

        shadow = shadow.filter(
            ImageFilter.GaussianBlur(
                12
            )
        )

        # لا نضع الظل فوق الصورة
        # لأن الصورة مرسومة بالفعل

        draw.rounded_rectangle(
            (
                x1,
                y1,
                x2,
                y2
            ),
            radius=32,
            outline=BORDER,
            width=2
        )

        # ----------------------------------------------------
        # شريط الهوية
        # ----------------------------------------------------

        draw.rounded_rectangle(
            (
                x1,
                y1,
                x1 + 190,
                y1 + 8
            ),
            radius=4,
            fill=ACCENT_RED
        )

        draw.rounded_rectangle(
            (
                x2 - 110,
                y2 - 7,
                x2,
                y2
            ),
            radius=4,
            fill=ACCENT_GOLD
        )

        print(
            "🖼️ تم استخدام صورة الخبر."
        )

        return

    # ========================================================
    # لا توجد صورة → شعار الصفحة
    # ========================================================

    print(
        "ℹ️ لا توجد صورة للخبر."
    )

    print(
        "🛡️ سيتم استخدام logo.jpg كخلفية كاملة."
    )

    card = create_logo_fallback(
        width,
        height
    )

    # --------------------------------------------------------
    # قناع الزوايا
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
        radius=32,
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

    # --------------------------------------------------------
    # إطار
    # --------------------------------------------------------

    draw.rounded_rectangle(
        (
            x1,
            y1,
            x2,
            y2
        ),
        radius=32,
        outline=BORDER,
        width=2
    )

    # --------------------------------------------------------
    # شريط الهوية
    # --------------------------------------------------------

    draw.rounded_rectangle(
        (
            x1,
            y1,
            x1 + 190,
            y1 + 8
        ),
        radius=4,
        fill=ACCENT_GOLD
    )

    draw.rounded_rectangle(
        (
            x2 - 110,
            y2 - 7,
            x2,
            y2
        ),
        radius=4,
        fill=ACCENT_RED
    )


# ============================================================
# 17. الهيدر
# ============================================================

def draw_header(
    image
):

    draw = ImageDraw.Draw(
        image
    )

    # --------------------------------------------------------
    # شعار الهيدر
    # --------------------------------------------------------

    logo_size = 68

    logo_x = 944
    logo_y = 40

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

            # ------------------------------------------------
            # حلقة ذهبية خارج الشعار
            # ------------------------------------------------

            draw.ellipse(
                (
                    logo_x - 5,
                    logo_y - 5,
                    logo_x + logo_size + 5,
                    logo_y + logo_size + 5
                ),
                fill=(
                    8,
                    10,
                    16
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

    draw_text(
        draw,
        (
            915,
            73
        ),
        PAGE_NAME,
        page_font,
        WHITE,
        anchor="rm"
    )

    # --------------------------------------------------------
    # خط صغير تحت اسم الصفحة
    # --------------------------------------------------------

    draw.rounded_rectangle(
        (
            690,
            100,
            915,
            105
        ),
        radius=3,
        fill=ACCENT_RED
    )

    draw.ellipse(
        (
            675,
            97,
            684,
            106
        ),
        fill=ACCENT_GOLD
    )

    # --------------------------------------------------------
    # علامة صغيرة أعلى اليسار
    # --------------------------------------------------------

    draw.rounded_rectangle(
        (
            60,
            52,
            180,
            60
        ),
        radius=4,
        fill=ACCENT_RED
    )

    draw.ellipse(
        (
            190,
            49,
            202,
            61
        ),
        fill=ACCENT_GOLD
    )


# ============================================================
# 18. التصنيف
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
# 19. جسم الخبر
# ============================================================

def draw_news_body(
    image,
    title,
    category
):

    draw = ImageDraw.Draw(
        image
    )

    # ========================================================
    # شارة التصنيف
    # ========================================================

    category_text = get_category_label(
        category
    )

    category_font = load_font(
        28
    )

    category_width = text_width(
        draw,
        category_text,
        category_font
    )

    badge_width = (
        category_width
        +
        68
    )

    badge_height = 60

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

    # --------------------------------------------------------
    # ظل الشارة
    # --------------------------------------------------------

    draw.rounded_rectangle(
        (
            badge_left + 4,
            badge_top + 5,
            badge_right + 4,
            badge_bottom + 5
        ),
        radius=17,
        fill=(
            0,
            0,
            0
        )
    )

    # --------------------------------------------------------
    # الشارة
    # --------------------------------------------------------

    draw.rounded_rectangle(
        (
            badge_left,
            badge_top,
            badge_right,
            badge_bottom
        ),
        radius=17,
        fill=ACCENT_RED
    )

    # --------------------------------------------------------
    # خط ذهبي داخلي صغير
    # --------------------------------------------------------

    draw.rounded_rectangle(
        (
            badge_left + 8,
            badge_top + 8,
            badge_left + 13,
            badge_bottom - 8
        ),
        radius=2,
        fill=ACCENT_GOLD
    )

    # --------------------------------------------------------
    # نص التصنيف
    # --------------------------------------------------------

    draw_text(
        draw,
        (
            badge_right - 31,
            badge_top + 30
        ),
        category_text,
        category_font,
        WHITE,
        anchor="rm"
    )

    # ========================================================
    # العنوان
    # ========================================================

    # مساحة أكبر للعنوان
    max_width = 930

    # أكبر قليلًا من النسخة السابقة
    font_sizes = [
        52,
        49,
        46,
        43,
        40,
        37
    ]

    selected_font = None
    selected_lines = []

    for size in font_sizes:

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
            37
        )

        selected_lines = build_title_lines(
            draw,
            title,
            selected_font,
            max_width,
            3
        )

    # --------------------------------------------------------
    # مكان العنوان
    # --------------------------------------------------------

    line_height = int(
        selected_font.size
        *
        1.40
    )

    start_y = 760

    # --------------------------------------------------------
    # حساب عدد الأسطر
    # --------------------------------------------------------

    total_height = (
        len(selected_lines)
        *
        line_height
    )

    # --------------------------------------------------------
    # رسم العنوان
    # --------------------------------------------------------

    current_y = start_y

    for line in selected_lines:

        # ظل بسيط لتحسين القراءة
        if RAQM_AVAILABLE:

            draw.text(
                (
                    1018,
                    current_y + 3
                ),
                line,
                font=selected_font,
                fill=(
                    0,
                    0,
                    0
                ),
                direction="rtl",
                language="ar",
                anchor="ra"
            )

            draw.text(
                (
                    1020,
                    current_y
                ),
                line,
                font=selected_font,
                fill=WHITE,
                direction="rtl",
                language="ar",
                anchor="ra"
            )

        else:

            draw_text(
                draw,
                (
                    1020,
                    current_y
                ),
                line,
                selected_font,
                WHITE,
                anchor="ra"
            )

        current_y += line_height

    # ========================================================
    # زخرفة أسفل العنوان
    # ========================================================

    accent_y = min(
        935,
        start_y + total_height + 18
    )

    draw.rounded_rectangle(
        (
            60,
            accent_y,
            205,
            accent_y + 5
        ),
        radius=3,
        fill=ACCENT_RED
    )

    draw.ellipse(
        (
            215,
            accent_y - 2,
            222,
            accent_y + 5
        ),
        fill=ACCENT_GOLD
    )


# ============================================================
# 20. التذييل
# ============================================================

def draw_footer(
    image
):

    draw = ImageDraw.Draw(
        image
    )

    y = 995

    # --------------------------------------------------------
    # الخط
    # --------------------------------------------------------

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
            185,
            y + 2
        ),
        radius=2,
        fill=ACCENT_RED
    )

    draw.ellipse(
        (
            195,
            y - 3,
            201,
            y + 3
        ),
        fill=ACCENT_GOLD
    )

    # --------------------------------------------------------
    # النص
    # --------------------------------------------------------

    footer_font = load_font(
        21
    )

    footer_text = (
        PAGE_NAME
        +
        " • المصدر الرسمي"
    )

    draw_text(
        draw,
        (
            1020,
            y + 15
        ),
        footer_text,
        footer_font,
        MUTED_TEXT,
        anchor="ra"
    )


# ============================================================
# 21. الدالة الرئيسية
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
    # العنوان
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
    # الحفظ
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
# 22. اختبار مباشر
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("🧪 اختبار مولد صور نبض مدريد")
    print("=" * 60)

    print(
        "RAQM:",
        "متوفر ✅"
        if RAQM_AVAILABLE
        else
        "غير متوفر ⚠️"
    )

    print(
        "Font:",
        FONT_FILE
    )

    print(
        "Logo:",
        find_logo_file()
    )

    print("=" * 60)

    test_title = (
        "ريال مدريد يستعد لمواجهة قوية "
        "في الدوري الإسباني"
    )

    test_output = generate_news_image(
        title=test_title,
        category="real_madrid",
        image_path=None
    )

    print()
    print(
        "📁 نتيجة الاختبار:"
    )

    print(
        test_output
    )

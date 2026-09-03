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

BACKGROUND_DARK = (8, 10, 16)
BACKGROUND_MID = (18, 22, 31)
BACKGROUND_CARD = (19, 23, 33)

ACCENT_RED = (220, 20, 50)
ACCENT_GOLD = (235, 180, 45)

WHITE = (255, 255, 255)
LIGHT_GRAY = (215, 218, 225)
MUTED_TEXT = (145, 150, 165)

BORDER = (75, 80, 95)


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

    # إزالة HTML البسيط
    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

    # تحويل المسافات المتعددة إلى مسافة واحدة
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
# 7. تجهيز النص للرسم
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

    # ========================================================
    # العربية
    # ========================================================

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

    # ========================================================
    # العربية بدون RAQM
    #
    # Fallback فقط.
    # ========================================================

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

    # ========================================================
    # النص الإنجليزي/العادي
    # ========================================================

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
            else
            current
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

    # ========================================================
    # إذا تجاوزنا 3 أسطر
    # ========================================================

    if len(lines) <= max_lines:

        return lines

    result = lines[
        :max_lines - 1
    ]

    last_text = " ".join(
        lines[
            max_lines - 1:
        ]
    )

    # حاول إدخال أكبر عدد ممكن من الكلمات
    last_line = ""

    for word in last_text.split():

        candidate = (
            word
            if not last_line
            else
            last_line
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

    # علامة اختصار
    if last_line != last_text:

        last_line = (
            last_line.rstrip()
            +
            "…"
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
# 12. الخلفية
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
            20
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
    # خطوط هندسية
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
                42,
                46,
                57
            ),
            width=1
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
# 15. إضافة الصورة الرئيسية
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
    # صورة الخبر
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
            radius=30,
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
            fill=ACCENT_RED
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
        "🛡️ سيتم استخدام logo.jpg."
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
    # Glow
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
            width // 2 - 300,
            height // 2 - 300,
            width // 2 + 300,
            height // 2 + 300
        ),
        fill=(
            *ACCENT_RED,
            35
        )
    )

    glow = glow.filter(
        ImageFilter.GaussianBlur(
            85
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

            # شعار كبير وواضح
            target_width = 360
            target_height = 360

            logo = ImageOps.contain(
                logo,
                (
                    target_width,
                    target_height
                ),
                method=Image.Resampling.LANCZOS
            )

            logo_x = (
                width - logo.width
            ) // 2

            logo_y = (
                height - logo.height
            ) // 2

            # ------------------------------------------------
            # خلفية دائرية للشعار
            # ------------------------------------------------

            circle_size = max(
                logo.width,
                logo.height
            ) + 55

            circle = Image.new(
                "RGBA",
                (
                    circle_size,
                    circle_size
                ),
                (
                    0,
                    0,
                    0,
                    0
                )
            )

            circle_draw = ImageDraw.Draw(
                circle
            )

            circle_draw.ellipse(
                (
                    5,
                    5,
                    circle_size - 5,
                    circle_size - 5
                ),
                fill=(
                    8,
                    10,
                    16,
                    210
                ),
                outline=(
                    *ACCENT_GOLD,
                    220
                ),
                width=3
            )

            circle_x = (
                width - circle_size
            ) // 2

            circle_y = (
                height - circle_size
            ) // 2

            card.paste(
                circle,
                (
                    circle_x,
                    circle_y
                ),
                circle
            )

            # ------------------------------------------------
            # وضع الشعار
            # ------------------------------------------------

            logo_x = (
                width - logo.width
            ) // 2

            logo_y = (
                height - logo.height
            ) // 2

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
                f"⚠️ خطأ في تحميل logo.jpg: {error}"
            )

    else:

        # ----------------------------------------------------
        # fallback إذا لم يوجد الشعار
        # ----------------------------------------------------

        print(
            "❌ لم يتم العثور على logo.jpg"
        )

        fallback_font = load_font(
            52
        )

        draw_card = ImageDraw.Draw(
            card
        )

        draw_card.text(
            (
                width // 2,
                height // 2
            ),
            PAGE_NAME,
            font=fallback_font,
            fill=WHITE,
            anchor="mm"
        )

    # --------------------------------------------------------
    # إطار البطاقة
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
# 16. الهيدر
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

    if RAQM_AVAILABLE:

        draw.text(
            (
                930,
                53
            ),
            PAGE_NAME,
            font=page_font,
            fill=WHITE,
            direction="rtl",
            language="ar",
            anchor="ra"
        )

    else:

        draw_text(
            draw,
            (
                930,
                53
            ),
            PAGE_NAME,
            page_font,
            WHITE,
            anchor="ra"
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
# 17. التصنيف
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
# 18. جسم الخبر
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

    category_width = text_width(
        draw,
        category_text,
        category_font
    )

    badge_width = (
        category_width
        +
        52
    )

    badge_height = 54

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

    if RAQM_AVAILABLE:

        draw.text(
            (
                badge_right - 26,
                badge_top + 27
            ),
            category_text,
            font=category_font,
            fill=WHITE,
            direction="rtl",
            language="ar",
            anchor="rm"
        )

    else:

        draw_text(
            draw,
            (
                badge_right - 26,
                badge_top + 8
            ),
            category_text,
            category_font,
            WHITE
        )

    # --------------------------------------------------------
    # العنوان
    # --------------------------------------------------------

    max_width = 920

    font_sizes = [
        46,
        42,
        38,
        35,
        32
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

        if RAQM_AVAILABLE:

            draw.text(
                (
                    1020,
                    start_y
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
                    start_y
                ),
                line,
                selected_font,
                WHITE,
                anchor="ra"
            )

        start_y += line_height


# ============================================================
# 19. التذييل
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

    footer_text = (
        PAGE_NAME
        +
        " • المصدر الرسمي"
    )

    if RAQM_AVAILABLE:

        draw.text(
            (
                1020,
                y + 15
            ),
            footer_text,
            font=footer_font,
            fill=MUTED_TEXT,
            direction="rtl",
            language="ar",
            anchor="ra"
        )

    else:

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
# 20. الدالة الرئيسية
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
# 21. اختبار مباشر
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("🧪 اختبار مولد صور نبض مدريد")
    print("=" * 60)
    print(
        "RAQM:",
        "متوفر ✅" if RAQM_AVAILABLE else "غير متوفر ⚠️"
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

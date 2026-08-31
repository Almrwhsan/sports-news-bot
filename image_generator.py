from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import textwrap
import re


# ============================================================
# إعدادات التصميم
# ============================================================

IMAGE_WIDTH = 1080
IMAGE_HEIGHT = 1080

OUTPUT_DIR = "generated_images"

PAGE_NAME = "نبض مدريد"


# ============================================================
# الألوان
# ============================================================

BACKGROUND = (12, 14, 20)
BACKGROUND_LIGHT = (24, 27, 36)

WHITE = (255, 255, 255)
LIGHT_TEXT = (220, 223, 230)
MUTED_TEXT = (160, 165, 175)

RED = (220, 35, 55)
RED_DARK = (125, 15, 30)

BLACK = (5, 6, 9)


# ============================================================
# الخطوط
# ============================================================

FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


def find_font(bold=False):

    if bold:

        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]

    else:

        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]

    for path in candidates:

        if os.path.exists(path):
            return path

    return None


# ============================================================
# تحميل الخط
# ============================================================

def load_font(size, bold=False):

    font_path = find_font(bold)

    if not font_path:

        return ImageFont.load_default()

    return ImageFont.truetype(
        font_path,
        size
    )


# ============================================================
# خلفية حديثة
# ============================================================

def create_background():

    image = Image.new(
        "RGB",
        (
            IMAGE_WIDTH,
            IMAGE_HEIGHT
        ),
        BACKGROUND
    )

    draw = ImageDraw.Draw(image)

    # --------------------------------------------------------
    # تدرج رأسي بسيط
    # --------------------------------------------------------

    for y in range(IMAGE_HEIGHT):

        ratio = y / IMAGE_HEIGHT

        r = int(
            BACKGROUND[0]
            + (
                BACKGROUND_LIGHT[0]
                - BACKGROUND[0]
            ) * ratio
        )

        g = int(
            BACKGROUND[1]
            + (
                BACKGROUND_LIGHT[1]
                - BACKGROUND[1]
            ) * ratio
        )

        b = int(
            BACKGROUND[2]
            + (
                BACKGROUND_LIGHT[2]
                - BACKGROUND[2]
            ) * ratio
        )

        draw.line(
            [
                (0, y),
                (IMAGE_WIDTH, y)
            ],
            fill=(r, g, b)
        )

    # --------------------------------------------------------
    # دوائر إضاءة خفيفة
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
        (
            -300,
            -250,
            450,
            500
        ),
        fill=(
            RED[0],
            RED[1],
            RED[2],
            55
        )
    )

    glow_draw.ellipse(
        (
            780,
            650,
            1250,
            1150
        ),
        fill=(
            RED[0],
            RED[1],
            RED[2],
            35
        )
    )

    glow = glow.filter(
        ImageFilter.GaussianBlur(100)
    )

    image = Image.alpha_composite(
        image.convert("RGBA"),
        glow
    ).convert("RGB")

    draw = ImageDraw.Draw(image)

    # --------------------------------------------------------
    # خطوط هندسية
    # --------------------------------------------------------

    for x in range(
        -300,
        IMAGE_WIDTH + 400,
        140
    ):

        draw.line(
            [
                (x, 0),
                (x - 500, IMAGE_HEIGHT)
            ],
            fill=(
                255,
                255,
                255
            ),
            width=1
        )

    return image


# ============================================================
# إضافة الصورة الرئيسية
# ============================================================

def add_news_image(
    image,
    image_path=None
):

    draw = ImageDraw.Draw(image)

    x1 = 70
    y1 = 190
    x2 = 1010
    y2 = 650

    width = x2 - x1
    height = y2 - y1

    # --------------------------------------------------------
    # إذا كانت هناك صورة
    # --------------------------------------------------------

    if image_path and os.path.exists(image_path):

        try:

            photo = Image.open(
                image_path
            ).convert("RGB")

            photo.thumbnail(
                (
                    width,
                    height
                )
            )

            photo_width, photo_height = (
                photo.size
            )

            background = Image.new(
                "RGB",
                (
                    width,
                    height
                ),
                BLACK
            )

            paste_x = (
                width - photo_width
            ) // 2

            paste_y = (
                height - photo_height
            ) // 2

            background.paste(
                photo,
                (
                    paste_x,
                    paste_y
                )
            )

            image.paste(
                background,
                (
                    x1,
                    y1
                )
            )

            # ------------------------------------------------
            # طبقة داكنة خفيفة فوق الصورة
            # ------------------------------------------------

            overlay = Image.new(
                "RGBA",
                (
                    width,
                    height
                ),
                (
                    0,
                    0,
                    0,
                    45
                )
            )

            image.paste(
                overlay,
                (
                    x1,
                    y1
                ),
                overlay
            )

        except Exception as error:

            print(
                f"Image loading error: {error}"
            )

            draw.rectangle(
                (
                    x1,
                    y1,
                    x2,
                    y2
                ),
                fill=(
                    25,
                    27,
                    35
                )
            )

    else:

        # ----------------------------------------------------
        # مساحة مؤقتة في حالة عدم وجود صورة
        # ----------------------------------------------------

        draw.rounded_rectangle(
            (
                x1,
                y1,
                x2,
                y2
            ),
            radius=30,
            fill=(
                25,
                27,
                35
            ),
            outline=RED,
            width=3
        )

        font = load_font(
            36,
            bold=True
        )

        placeholder = "FOOTBALL"

        bbox = draw.textbbox(
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

        draw.text(
            (
                x1
                + (
                    width
                    - text_width
                ) / 2,
                y1
                + (
                    height
                    - text_height
                ) / 2
            ),
            placeholder,
            fill=(
                100,
                105,
                115
            ),
            font=font
        )


# ============================================================
# رسم اسم الصفحة
# ============================================================

def draw_page_name(image):

    draw = ImageDraw.Draw(image)

    font = load_font(
        42,
        bold=True
    )

    text = PAGE_NAME

    bbox = draw.textbbox(
        (0, 0),
        text,
        font=font
    )

    text_width = (
        bbox[2] - bbox[0]
    )

    x = (
        IMAGE_WIDTH
        - text_width
    ) // 2

    y = 55

    # خط أحمر صغير

    draw.rounded_rectangle(
        (
            x - 30,
            y + 12,
            x - 5,
            y + 48
        ),
        radius=8,
        fill=RED
    )

    draw.text(
        (
            x,
            y
        ),
        text,
        fill=WHITE,
        font=font
    )


# ============================================================
# التصنيف
# ============================================================

def get_category_label(category):

    labels = {

        "transfers": "انتقالات",

        "injuries": "إصابات",

        "matches": "مباريات",

        "national_teams": "منتخبات",

        "football": "كرة القدم",

    }

    return labels.get(
        category,
        "كرة القدم"
    )


# ============================================================
# رسم التصنيف
# ============================================================

def draw_category(
    image,
    category
):

    draw = ImageDraw.Draw(image)

    label = get_category_label(
        category
    )

    font = load_font(
        28,
        bold=True
    )

    x = 70
    y = 690

    bbox = draw.textbbox(
        (0, 0),
        label,
        font=font
    )

    text_width = (
        bbox[2] - bbox[0]
    )

    text_height = (
        bbox[3] - bbox[1]
    )

    padding_x = 25
    padding_y = 14

    draw.rounded_rectangle(
        (
            x,
            y,
            x
            + text_width
            + padding_x * 2,
            y
            + text_height
            + padding_y * 2
        ),
        radius=18,
        fill=RED
    )

    draw.text(
        (
            x + padding_x,
            y + padding_y - 3
        ),
        label,
        fill=WHITE,
        font=font
    )


# ============================================================
# تقسيم العنوان إلى أسطر
# ============================================================

def wrap_title(
    title,
    font,
    max_width
):

    words = title.split()

    lines = []

    current = ""

    for word in words:

        test = (
            word
            if not current
            else current
            + " "
            + word
        )

        bbox = ImageDraw.Draw(
            Image.new(
                "RGB",
                (1, 1)
            )
        ).textbbox(
            (0, 0),
            test,
            font=font
        )

        width = (
            bbox[2] - bbox[0]
        )

        if width <= max_width:

            current = test

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

    return lines


# ============================================================
# رسم عنوان الخبر
# ============================================================

def draw_title(
    image,
    title
):

    draw = ImageDraw.Draw(image)

    font = load_font(
        48,
        bold=True
    )

    max_width = 940

    lines = wrap_title(
        title,
        font,
        max_width
    )

    # لا نريد عنوانًا طويلًا جدًا
    lines = lines[:4]

    y = 780

    for line in lines:

        bbox = draw.textbbox(
            (0, 0),
            line,
            font=font
        )

        text_width = (
            bbox[2] - bbox[0]
        )

        # محاذاة لليمين
        x = (
            IMAGE_WIDTH
            - 70
            - text_width
        )

        draw.text(
            (
                x,
                y
            ),
            line,
            fill=WHITE,
            font=font
        )

        y += 62


# ============================================================
# الخط السفلي
# ============================================================

def draw_footer(image):

    draw = ImageDraw.Draw(image)

    y = 1020

    draw.line(
        (
            70,
            y,
            1010,
            y
        ),
        fill=(
            70,
            73,
            82
        ),
        width=2
    )

    font = load_font(
        25,
        bold=True
    )

    bbox = draw.textbbox(
        (0, 0),
        PAGE_NAME,
        font=font
    )

    text_width = (
        bbox[2] - bbox[0]
    )

    draw.text(
        (
            IMAGE_WIDTH
            - 70
            - text_width,
            y + 15
        ),
        PAGE_NAME,
        fill=MUTED_TEXT,
        font=font
    )


# ============================================================
# إنشاء صورة الخبر
# ============================================================

def generate_news_image(
    title,
    category="football",
    image_path=None,
    output_path=None
):

    print(
        "Generating news image..."
    )

    image = create_background()

    draw_page_name(
        image
    )

    add_news_image(
        image,
        image_path
    )

    draw_category(
        image,
        category
    )

    draw_title(
        image,
        title
    )

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

    if not output_path:

        safe_title = re_safe_filename(
            title
        )

        output_path = os.path.join(
            OUTPUT_DIR,
            f"{safe_title}.png"
        )

    image.save(
        output_path,
        "PNG",
        optimize=True
    )

    print(
        f"Image created: {output_path}"
    )

    return output_path


# ============================================================
# تنظيف اسم الملف
# ============================================================

def re_safe_filename(text):

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

    # منع اسم طويل جدًا
    text = text[:80]

    if not text:

        text = "football_news"

    return text


# ============================================================
# اختبار مستقل
# ============================================================

if __name__ == "__main__":

    TEST_TITLE = (
        "الأهلي السعودي يستعد لمواجهة جديدة "
        "في بطولة كأس القارات"
    )

    TEST_CATEGORY = "matches"

    generate_news_image(
        title=TEST_TITLE,
        category=TEST_CATEGORY
    )

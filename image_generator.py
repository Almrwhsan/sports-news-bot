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
# 1. إعدادات التصميم الأساسية
# ============================================================

IMAGE_WIDTH = 1080
IMAGE_HEIGHT = 1080

OUTPUT_DIR = "generated_images"

PAGE_NAME = "نبض مدريد"

LOGO_PATH = "logo.jpg"


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

BLACK = (0, 0, 0)


# ============================================================
# 3. الخطوط (استخدام المصفوفات الأصلية)
# ============================================================

FONT_PATHS_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "arialbd.ttf",
    "arial.ttf",
]

FONT_PATHS_NORMAL = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "arial.ttf",
]


def load_font(size, bold=False):

    paths = FONT_PATHS_BOLD if bold else FONT_PATHS_NORMAL

    for path in paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass

    return ImageFont.load_default()


# ============================================================
# 4. معالجة النص العربي
# ============================================================

def fix_arabic(text):

    if not text:
        return ""

    text = str(text)

    try:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except Exception:
        return text


# ============================================================
# 5. تنظيف اسم ملف الصورة
# ============================================================

def safe_filename(text):

    text = str(text)

    text = re.sub(r'[\\/*?:"<>|]', "", text)
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"_+", "_", text)

    text = text[:100]

    if not text:
        text = "football_news"

    return text


# ============================================================
# 6. الخلفية الحديثة (خلفية عصرية احترافية)
# ============================================================

def create_modern_background():

    image = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT), BACKGROUND_DARK)
    draw = ImageDraw.Draw(image)

    # --------------------------------------------------------
    # تدرج رأسي
    # --------------------------------------------------------
    for y in range(IMAGE_HEIGHT):
        ratio = y / (IMAGE_HEIGHT - 1)
        r = int(BACKGROUND_DARK[0] + (BACKGROUND_MID[0] - BACKGROUND_DARK[0]) * ratio)
        g = int(BACKGROUND_DARK[1] + (BACKGROUND_MID[1] - BACKGROUND_DARK[1]) * ratio)
        b = int(BACKGROUND_DARK[2] + (BACKGROUND_MID[2] - BACKGROUND_DARK[2]) * ratio)

        draw.line([(0, y), (IMAGE_WIDTH, y)], fill=(r, g, b))

    # --------------------------------------------------------
    # إضاءة ملونة (Glow Effect)
    # --------------------------------------------------------
    glow = Image.new("RGBA", (IMAGE_WIDTH, IMAGE_HEIGHT), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)

    glow_draw.ellipse((-200, -200, 500, 500), fill=(*ACCENT_RED, 48))
    glow_draw.ellipse((650, 700, 1250, 1300), fill=(*ACCENT_RED, 35))
    glow_draw.ellipse((650, -200, 1200, 300), fill=(*ACCENT_GOLD, 15))

    glow = glow.filter(ImageFilter.GaussianBlur(120))
    image = Image.alpha_composite(image.convert("RGBA"), glow).convert("RGB")

    # --------------------------------------------------------
    # الخطوط الهندسية العصرية
    # --------------------------------------------------------
    draw = ImageDraw.Draw(image)

    for x in range(-400, IMAGE_WIDTH + 600, 160):
        draw.line([(x, 0), (x - 420, IMAGE_HEIGHT)], fill=(255, 255, 255), width=1)

    # --------------------------------------------------------
    # طبقة تعتيم الخطوط
    # --------------------------------------------------------
    overlay = Image.new("RGBA", (IMAGE_WIDTH, IMAGE_HEIGHT), (10, 12, 18, 205))
    image = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")

    return image


# ============================================================
# 7. الصورة الرئيسية والبديل الذكي للشعار
# ============================================================

def add_main_content_image(image, image_path=None):

    x1 = 60
    y1 = 160
    x2 = 1020
    y2 = 640

    width = x2 - x1
    height = y2 - y1

    # ========================================================
    # صورة الخبر موجودة
    # ========================================================
    if image_path and os.path.exists(image_path):
        try:
            photo = Image.open(image_path).convert("RGB")
            photo = ImageOps.fit(
                photo,
                (width, height),
                method=Image.Resampling.LANCZOS,
                centering=(0.5, 0.5)
            )

            mask = Image.new("L", (width, height), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle((0, 0, width, height), radius=28, fill=255)

            image.paste(photo, (x1, y1), mask)

            # طبقة تدرج فوق الصورة
            gradient = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            gradient_draw = ImageDraw.Draw(gradient)

            for gy in range(height):
                ratio = gy / height
                alpha = int(10 + 120 * ratio)
                gradient_draw.line([(0, gy), (width, gy)], fill=(0, 0, 0, alpha))

            gradient_mask = Image.composite(
                gradient, Image.new("RGBA", (width, height), (0, 0, 0, 0)), mask
            )

            image.paste(gradient_mask, (x1, y1), gradient_mask)

            draw = ImageDraw.Draw(image)
            draw.rounded_rectangle((x1, y1, x2, y2), radius=28, outline=(100, 105, 120), width=2)
            draw.rounded_rectangle((x1, y1, x1 + 155, y1 + 8), radius=4, fill=ACCENT_RED)
            return

        except Exception as error:
            print(f"❌ Error loading news image: {error}")

    # ========================================================
    # لا توجد صورة → استخدام الشعار بتنسيق مموه راقي
    # ========================================================
    card_bg = Image.new("RGB", (width, height), BACKGROUND_CARD)

    if os.path.exists(LOGO_PATH):
        try:
            logo = Image.open(LOGO_PATH).convert("RGBA")

            # خلفية مموهة من الشعار
            blurred_bg = ImageOps.fit(logo, (width, height), method=Image.Resampling.LANCZOS)
            blurred_bg = blurred_bg.filter(ImageFilter.GaussianBlur(40))

            dark_layer = Image.new("RGBA", (width, height), (0, 0, 0, 175))
            blurred_bg = Image.alpha_composite(blurred_bg, dark_layer)

            # الشعار الرئيسي في المنتصف
            logo_thumbnail = logo.copy()
            logo_thumbnail.thumbnail((280, 280), Image.Resampling.LANCZOS)

            lx = (width - logo_thumbnail.width) // 2
            ly = (height - logo_thumbnail.height) // 2

            blurred_bg.paste(logo_thumbnail, (lx, ly), logo_thumbnail)
            card_bg = blurred_bg.convert("RGB")

        except Exception as error:
            print(f"❌ Error processing logo: {error}")
    else:
        print(f"⚠️ Logo not found: {LOGO_PATH}")
        draw = ImageDraw.Draw(card_bg)
        placeholder = fix_arabic(PAGE_NAME)
        font = load_font(42, bold=True)
        bbox = draw.textbbox((0, 0), placeholder, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        draw.text(((width - text_width) / 2, (height - text_height) / 2), placeholder, fill=MUTED_TEXT, font=font)

    image.paste(card_bg, (x1, y1))

    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((x1, y1, x2, y2), radius=28, outline=ACCENT_RED, width=2)


# ============================================================
# 8. الهيدر والهوية المصغرة
# ============================================================

def draw_header_and_brand(image):

    draw = ImageDraw.Draw(image)

    # ========================================================
    # الشعار الدائري المصغر
    # ========================================================
    if os.path.exists(LOGO_PATH):
        try:
            logo_size = 64
            logo = Image.open(LOGO_PATH).convert("RGBA")
            logo = ImageOps.fit(logo, (logo_size, logo_size), method=Image.Resampling.LANCZOS)

            mask = Image.new("L", (logo_size, logo_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, logo_size, logo_size), fill=255)

            logo_x = 952
            logo_y = 50

            # إطار ذهبي بارز
            draw.ellipse((logo_x - 3, logo_y - 3, logo_x + logo_size + 3, logo_y + logo_size + 3), outline=ACCENT_GOLD, width=2)
            image.paste(logo, (logo_x, logo_y), mask)

        except Exception as error:
            print(f"❌ Header logo error: {error}")

    # ========================================================
    # اسم الصفحة
    # ========================================================
    font = load_font(38, bold=True)
    page_text = fix_arabic(PAGE_NAME)

    draw.text((925, 65), page_text, fill=WHITE, font=font, anchor="ra")

    # ========================================================
    # الزخرفة الرياضية العليا
    # ========================================================
    draw.rounded_rectangle((60, 65, 180, 73), radius=4, fill=ACCENT_RED)
    draw.ellipse((190, 61, 202, 73), fill=ACCENT_GOLD)


# ============================================================
# 9. قاموس التصنيفات
# ============================================================

def get_category_label(category):

    labels = {
        "transfers": "انتقالات",
        "injuries": "إصابات",
        "matches": "مباريات",
        "breaking": "عاجل",
        "football": "كرة القدم",
        "national_teams": "منتخبات",
        "real_madrid": "ريال مدريد",
        "barcelona": "برشلونة",
        "atletico_madrid": "أتلتيكو مدريد",
        "la_liga": "الدوري الإسباني",
        "champions_league": "دوري الأبطال",
        "world_football": "كرة عالمية",
    }

    return labels.get(category, "كرة القدم")


# ============================================================
# 10. رسم النص والعنوان مع التكيف الديناميكي الذكي
# ============================================================

def draw_news_body(image, title, category):

    draw = ImageDraw.Draw(image)

    # ========================================================
    # التصنيف (Category Badge)
    # ========================================================
    category_text = fix_arabic(get_category_label(category))
    category_font = load_font(26, bold=True)

    bbox = draw.textbbox((0, 0), category_text, font=category_font)
    category_width = bbox[2] - bbox[0]
    category_height = bbox[3] - bbox[1]

    padding_x = 24
    padding_y = 11

    badge_width = category_width + padding_x * 2
    badge_height = category_height + padding_y * 2

    badge_x2 = 1020
    badge_x1 = badge_x2 - badge_width
    badge_y1 = 675
    badge_y2 = badge_y1 + badge_height

    # ظل التاج
    shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((badge_x1 + 5, badge_y1 + 5, badge_x2 + 5, badge_y2 + 5), radius=15, fill=(0, 0, 0, 100))
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))

    image = Image.alpha_composite(image.convert("RGBA"), shadow).convert("RGB")
    draw = ImageDraw.Draw(image)

    # رسم الشارة
    draw.rounded_rectangle((badge_x1, badge_y1, badge_x2, badge_y2), radius=15, fill=ACCENT_RED)
    draw.text((badge_x2 - padding_x, badge_y1 + padding_y - 2), category_text, fill=WHITE, font=category_font, anchor="ra")

    # ========================================================
    # العنوان الديناميكي المتكيف مع طول النص
    # ========================================================
    max_width = 920
    max_height_allowed = 220  # أقصى ارتفاع متاح للعنوان قبل التداخل مع Footer
    words = str(title).split()

    # تحديد حجم الخط المناسب تلقائياً بناءً على عدد الكلمات وحجم النص
    font_sizes = [46, 40, 34, 28]
    selected_font = None
    selected_lines = []
    selected_spacing = 68

    for font_size in font_sizes:
        test_font = load_font(font_size, bold=True)
        test_lines = []
        current_line = ""

        for word in words:
            test_line = word if not current_line else current_line + " " + word
            fixed_test = fix_arabic(test_line)
            bbox = draw.textbbox((0, 0), fixed_test, font=test_font)

            if (bbox[2] - bbox[0]) <= max_width:
                current_line = test_line
            else:
                if current_line:
                    test_lines.append(current_line)
                current_line = word

        if current_line:
            test_lines.append(current_line)

        # حساب الارتفاع الإجمالي للأسطر
        spacing = int(font_size * 1.45)
        total_h = len(test_lines) * spacing

        if total_h <= max_height_allowed or font_size == font_sizes[-1]:
            selected_font = test_font
            selected_lines = test_lines[:4]  # بحد أقصى 4 أسطر
            selected_spacing = spacing
            break

    # رسم العنوان المقسم
    start_y = 755
    for line in selected_lines:
        fixed_line = fix_arabic(line)
        draw.text((1020, start_y), fixed_line, fill=WHITE, font=selected_font, anchor="ra")
        start_y += selected_spacing


# ============================================================
# 11. التذييل (Footer)
# ============================================================

def draw_footer(image):

    draw = ImageDraw.Draw(image)
    y = 1000

    # خط فاصل
    draw.line((60, y, 1020, y), fill=(60, 65, 80), width=1)

    # شريط أحمر جمالي
    draw.rounded_rectangle((60, y - 2, 180, y + 2), radius=2, fill=ACCENT_RED)

    # النص
    font = load_font(22, bold=True)
    footer_text = fix_arabic(f"{PAGE_NAME} • المصدر الرسمي")

    draw.text((1020, y + 18), footer_text, fill=MUTED_TEXT, font=font, anchor="ra")


# ============================================================
# 12. الدالة الرئيسية (للتكامل التام مع bot.py)
# ============================================================

def generate_news_image(
    title,
    category="football",
    image_path=None,
    output_path=None
):

    print("🎨 جاري إنشاء التصميم الاحترافي...")

    image = create_modern_background()
    draw_header_and_brand(image)
    add_main_content_image(image, image_path)
    draw_news_body(image, title, category)
    draw_footer(image)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if not output_path:
        filename = safe_filename(title) + ".png"
        output_path = os.path.join(OUTPUT_DIR, filename)

    image.save(output_path, "PNG", optimize=True)

    print(f"✅ تم حفظ الصورة: {output_path}")

    return output_path
    

import os
import re
import urllib.request
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
FONT_FILE = "Cairo-Bold.ttf"

# تنزيل خط Cairo-Bold تلقائياً في حال عدم وجوده بالمجلد
if not os.path.exists(FONT_FILE):
    try:
        print("📥 جاري تنزيل خط Cairo-Bold الاحترافي...")
        font_url = "https://github.com/google/fonts/raw/main/ofl/cairo/static/Cairo-Bold.ttf"
        urllib.request.urlretrieve(font_url, FONT_FILE)
        print("✅ تم تنزيل الخط بنجاح!")
    except Exception as e:
        print(f"⚠️ تعذر تنزيل الخط تلقائياً: {e}")


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
# 3. تحميل الخطوط
# ============================================================

FONT_PATHS_BOLD = [
    FONT_FILE,
    "Cairo-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "arialbd.ttf",
]

FONT_PATHS_NORMAL = [
    FONT_FILE,
    "Cairo-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "arial.ttf",
]


def load_font(size, bold=True):
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


def safe_filename(text):
    text = str(text)
    text = re.sub(r'[\\/*?:"<>|]', "", text)
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"_+", "_", text)
    text = text[:100]
    return text if text else "news_card"


# ============================================================
# 5. الخلفية الهندسية
# ============================================================

def create_modern_background():
    image = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT), BACKGROUND_DARK)
    draw = ImageDraw.Draw(image)

    # تدرج رأسي
    for y in range(IMAGE_HEIGHT):
        ratio = y / (IMAGE_HEIGHT - 1)
        r = int(BACKGROUND_DARK[0] + (BACKGROUND_MID[0] - BACKGROUND_DARK[0]) * ratio)
        g = int(BACKGROUND_DARK[1] + (BACKGROUND_MID[1] - BACKGROUND_DARK[1]) * ratio)
        b = int(BACKGROUND_DARK[2] + (BACKGROUND_MID[2] - BACKGROUND_DARK[2]) * ratio)
        draw.line([(0, y), (IMAGE_WIDTH, y)], fill=(r, g, b))

    # إضاءة Glow
    glow = Image.new("RGBA", (IMAGE_WIDTH, IMAGE_HEIGHT), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((-200, -200, 500, 500), fill=(*ACCENT_RED, 55))
    glow_draw.ellipse((650, 700, 1250, 1300), fill=(*ACCENT_RED, 40))
    glow_draw.ellipse((650, -200, 1200, 300), fill=(*ACCENT_GOLD, 20))

    glow = glow.filter(ImageFilter.GaussianBlur(110))
    image = Image.alpha_composite(image.convert("RGBA"), glow).convert("RGB")

    # شبكة الخطوط الهندسية
    draw = ImageDraw.Draw(image)
    for x in range(-400, IMAGE_WIDTH + 600, 160):
        draw.line([(x, 0), (x - 420, IMAGE_HEIGHT)], fill=(255, 255, 255), width=1)

    overlay = Image.new("RGBA", (IMAGE_WIDTH, IMAGE_HEIGHT), (10, 12, 18, 200))
    image = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")

    return image


# ============================================================
# 6. بطاقة الصورة الرئيسية
# ============================================================

def add_main_content_image(image, image_path=None):
    x1, y1, x2, y2 = 60, 160, 1020, 640
    width, height = x2 - x1, y2 - y1

    if image_path and os.path.exists(image_path):
        try:
            photo = Image.open(image_path).convert("RGB")
            photo = ImageOps.fit(photo, (width, height), method=Image.Resampling.LANCZOS)

            mask = Image.new("L", (width, height), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle((0, 0, width, height), radius=28, fill=255)

            image.paste(photo, (x1, y1), mask)

            draw = ImageDraw.Draw(image)
            draw.rounded_rectangle((x1, y1, x2, y2), radius=28, outline=(100, 105, 120), width=2)
            draw.rounded_rectangle((x1, y1, x1 + 155, y1 + 8), radius=4, fill=ACCENT_RED)
            return
        except Exception as error:
            print(f"❌ Error loading news image: {error}")

    # البديل في حال عدم وجود صورة
    card_bg = Image.new("RGB", (width, height), BACKGROUND_CARD)
    draw_card = ImageDraw.Draw(card_bg)
    
    placeholder_text = fix_arabic("صورة الخبر")
    font = load_font(52, bold=True)
    
    bbox = draw_card.textbbox((0, 0), placeholder_text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw_card.text(((width - tw) / 2, (height - th) / 2), placeholder_text, fill=WHITE, font=font)

    image.paste(card_bg, (x1, y1))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((x1, y1, x2, y2), radius=28, outline=(80, 85, 100), width=2)


# ============================================================
# 7. الهيدر واللوجو
# ============================================================

def draw_header_and_brand(image):
    draw = ImageDraw.Draw(image)

    # اللوجو الدائري
    logo_size = 64
    logo_x, logo_y = 952, 50

    if os.path.exists(LOGO_PATH):
        try:
            logo = Image.open(LOGO_PATH).convert("RGBA")
            logo = ImageOps.fit(logo, (logo_size, logo_size), method=Image.Resampling.LANCZOS)

            mask = Image.new("L", (logo_size, logo_size), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, logo_size, logo_size), fill=255)

            draw.ellipse((logo_x - 3, logo_y - 3, logo_x + logo_size + 3, logo_y + logo_size + 3), outline=ACCENT_GOLD, width=2)
            image.paste(logo, (logo_x, logo_y), mask)
        except Exception:
            pass
    else:
        # دائرة شعار افتراضية
        draw.ellipse((logo_x, logo_y, logo_x + logo_size, logo_y + logo_size), outline=ACCENT_GOLD, width=3)
        font_logo = load_font(20, bold=True)
        draw.text((logo_x + 12, logo_y + 18), "logo", fill=WHITE, font=font_logo)

    # اسم الصفحة
    font_page = load_font(38, bold=True)
    page_text = fix_arabic(PAGE_NAME)
    draw.text((925, 62), page_text, fill=WHITE, font=font_page, anchor="ra")

    # الزخرفة الأفقية العليا
    draw.rounded_rectangle((60, 65, 180, 73), radius=4, fill=ACCENT_RED)
    draw.ellipse((190, 61, 202, 73), fill=ACCENT_GOLD)


# ============================================================
# 8. شارة التصنيف والعنوان بالتكيف الاحترافي
# ============================================================

def get_category_label(category):
    labels = {
        "transfers": "انتقالات",
        "injuries": "إصابات",
        "matches": "مباريات",
        "breaking": "عاجل",
        "football": "كرة القدم",
        "real_madrid": "ريال مدريد",
    }
    return labels.get(category, "كرة القدم")


def draw_news_body(image, title, category):
    draw = ImageDraw.Draw(image)

    # 1. شارة التصنيف (Category Badge)
    category_text = fix_arabic(get_category_label(category))
    category_font = load_font(26, bold=True)

    bbox = draw.textbbox((0, 0), category_text, font=category_font)
    category_width = bbox[2] - bbox[0]
    category_height = bbox[3] - bbox[1]

    padding_x, padding_y = 26, 10
    badge_width = category_width + padding_x * 2
    badge_height = category_height + padding_y * 2

    badge_x2 = 1020
    badge_x1 = badge_x2 - badge_width
    badge_y1 = 675
    badge_y2 = badge_y1 + badge_height

    # رسم الشارة الحمراء
    draw.rounded_rectangle((badge_x1, badge_y1, badge_x2, badge_y2), radius=16, fill=ACCENT_RED)
    draw.text((badge_x2 - padding_x, badge_y1 + padding_y - 2), category_text, fill=WHITE, font=category_font, anchor="ra")

    # 2. العنوان الرئيسي (Dynamic Title Multiline)
    max_width = 940
    words = str(title).split()

    font_sizes = [48, 42, 36, 30]
    selected_font = None
    selected_lines = []
    selected_spacing = 72

    for font_size in font_sizes:
        test_font = load_font(font_size, bold=True)
        test_lines = []
        current_line = ""

        for word in words:
            test_line = word if not current_line else current_line + " " + word
            bbox = draw.textbbox((0, 0), fix_arabic(test_line), font=test_font)

            if (bbox[2] - bbox[0]) <= max_width:
                current_line = test_line
            else:
                if current_line:
                    test_lines.append(current_line)
                current_line = word

        if current_line:
            test_lines.append(current_line)

        spacing = int(font_size * 1.4)
        if len(test_lines) * spacing <= 220 or font_size == font_sizes[-1]:
            selected_font = test_font
            selected_lines = test_lines
            selected_spacing = spacing
            break

    # رسم أسطر العنوان مع ظل ناعم للمظهر الرياضي
    start_y = 760
    for line in selected_lines:
        fixed_line = fix_arabic(line)
        # ظل النص
        draw.text((1022, start_y + 2), fixed_line, fill=(0, 0, 0, 180), font=selected_font, anchor="ra")
        # النص الأصلي
        draw.text((1020, start_y), fixed_line, fill=WHITE, font=selected_font, anchor="ra")
        start_y += selected_spacing


# ============================================================
# 9. التذييل (Footer)
# ============================================================

def draw_footer(image):
    draw = ImageDraw.Draw(image)
    y = 1000

    draw.line((60, y, 1020, y), fill=(60, 65, 80), width=1)
    draw.rounded_rectangle((60, y - 2, 180, y + 2), radius=2, fill=ACCENT_RED)

    font = load_font(22, bold=True)
    footer_text = fix_arabic(f"{PAGE_NAME} • المصدر الرسمي")

    draw.text((1020, y + 18), footer_text, fill=MUTED_TEXT, font=font, anchor="ra")


# ============================================================
# 10. الدالة الرئيسية لتوليد الصورة
# ============================================================

def generate_news_image(title, category="football", image_path=None, output_path=None):
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
    print(f"✅ تم إنشاء الصورة المطابقة بنجاح: {output_path}")
    return output_path


# تجربة إنشاء صورة اختبارية مباشرة
if __name__ == "__main__":
    generate_news_image(
        title="خبر هام وعاجل: تفاصيل تفاصيل جديدة تظهر اليوم",
        category="football"
    )
    

# ============================================================
# اختبار مسار الصور الكامل
# ============================================================

import os

from image_fetcher import fetch_news_image
from image_generator import generate_news_image


# ============================================================
# إعدادات الاختبار
# ============================================================

TEST_GENERATED_DIR = "generated_images"


# ============================================================
# اختبار 1: جلب صورة حقيقية
# ============================================================

def test_real_image():

    print()
    print("===================================")
    print("TEST 1 - REAL IMAGE")
    print("===================================")

    title = "Real Madrid football"

    try:

        result = fetch_news_image(
            title=title
        )

    except Exception as error:

        print(
            "❌ Image fetch error:",
            error
        )

        return False

    if result:

        print()
        print("✅ REAL IMAGE FOUND")
        print(
            "Image:",
            result.get("image_path", "")
        )

        return True

    print()
    print(
        "⚠️ No real image found."
    )

    return False


# ============================================================
# اختبار 2: التوليد عند عدم وجود صورة
# ============================================================

def test_generated_image():

    print()
    print("===================================")
    print("TEST 2 - GENERATED IMAGE")
    print("===================================")

    title = (
        "اختبار توليد صورة بديلة "
        "عند عدم توفر صورة حقيقية"
    )

    try:

        output_path = generate_news_image(
            title=title,
            category="football",
            image_path=None
        )

    except Exception as error:

        print()
        print(
            "❌ Image generation error:",
            error
        )

        return False

    if output_path and os.path.exists(
        output_path
    ):

        print()
        print(
            "✅ GENERATED IMAGE FOUND"
        )

        print(
            "Image:",
            output_path
        )

        return True

    print()
    print(
        "❌ Generated image was not created."
    )

    return False


# ============================================================
# اختبار 3: المسار النهائي
# ============================================================

def test_final_image_logic():

    print()
    print("===================================")
    print("TEST 3 - FINAL IMAGE LOGIC")
    print("===================================")

    title = (
        "خبر تجريبي لا توجد له "
        "صورة حقيقية"
    )

    real_image_path = None

    print()
    print(
        "Step 1: Checking real image..."
    )

    if real_image_path and os.path.exists(
        real_image_path
    ):

        print(
            "✅ Using real image"
        )

        return True

    print(
        "⚠️ No real image."
    )

    print()
    print(
        "Step 2: Generating fallback image..."
    )

    try:

        generated_path = generate_news_image(
            title=title,
            category="football",
            image_path=None
        )

    except Exception as error:

        print()
        print(
            "❌ Generation failed:",
            error
        )

        print()
        print(
            "➡️ Final result: TEXT ONLY"
        )

        return True

    if generated_path and os.path.exists(
        generated_path
    ):

        print()
        print(
            "✅ Final result: GENERATED IMAGE"
        )

        print(
            "Image:",
            generated_path
        )

        return True

    print()
    print(
        "⚠️ Generation produced no image."
    )

    print(
        "➡️ Final result: TEXT ONLY"
    )

    return True


# ============================================================
# البرنامج الرئيسي
# ============================================================

def main():

    print("===================================")
    print("       IMAGE PIPELINE TEST")
    print("===================================")

    results = []

    results.append(
        test_real_image()
    )

    results.append(
        test_generated_image()
    )

    results.append(
        test_final_image_logic()
    )

    successful = sum(
        1 for result in results
        if result
    )

    print()
    print("===================================")
    print("       PIPELINE SUMMARY")
    print("===================================")

    print()

    print(
        f"Tests passed: "
        f"{successful}/{len(results)}"
    )

    print()

    if successful == len(results):

        print(
            "✅ IMAGE PIPELINE IS READY"
        )

    else:

        print(
            "❌ IMAGE PIPELINE NEEDS FIXING"
        )

        raise SystemExit(1)

    print()
    print("===================================")
    print("      IMAGE PIPELINE TEST END")
    print("===================================")


# ============================================================
# تشغيل
# ============================================================

if __name__ == "__main__":

    main()

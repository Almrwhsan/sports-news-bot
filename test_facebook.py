import os

from facebook_publisher import publish_text_post


# ============================================================
# اختبار Facebook Publisher
# ============================================================

def main():

    print("===================================")
    print("     FACEBOOK PUBLISHER TEST")
    print("===================================")

    enabled = os.getenv(
        "FACEBOOK_ENABLED",
        "false"
    ).lower() == "true"

    print(
        f"Facebook enabled: {enabled}"
    )

    # --------------------------------------------------------
    # إرسال رسالة اختبار
    # --------------------------------------------------------

    message = (
        "اختبار وحدة Facebook من نبض مدريد ⚽️🤖"
    )

    result = publish_text_post(
        message
    )

    # --------------------------------------------------------
    # عرض النتيجة
    # --------------------------------------------------------

    print()
    print("Result:")
    print(result)

    # --------------------------------------------------------
    # التحقق من وضع الإيقاف
    # --------------------------------------------------------

    if not enabled:

        if (
            result.get("success") is False
            and
            result.get("error")
            == "Facebook publishing is disabled."
        ):

            print()
            print(
                "✅ Safety switch works correctly."
            )

            return

        print()
        print(
            "❌ Safety switch test failed."
        )

        raise SystemExit(1)

    # --------------------------------------------------------
    # التحقق من النشر عند التفعيل
    # --------------------------------------------------------

    if result.get("success"):

        print()
        print(
            "✅ Facebook publishing works."
        )

        print(
            f"Post ID: "
            f"{result.get('post_id')}"
        )

        return

    print()
    print(
        "❌ Facebook publishing failed."
    )

    raise SystemExit(1)


# ============================================================
# تشغيل الاختبار
# ============================================================

if __name__ == "__main__":
    main()

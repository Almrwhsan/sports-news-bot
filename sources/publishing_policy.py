
# ============================================================
# Publishing Policy
# سياسة تنظيم نشر أخبار نبض مدريد
# ============================================================

from datetime import datetime, timedelta, timezone


# توقيت عدن: UTC+3
ADEN_TIMEZONE = timezone(
    timedelta(hours=3)
)


# الحد الأقصى للمنشورات يومياً
MAX_DAILY_POSTS = 4


# أقل فاصل بين منشورين بالدقائق
MIN_POST_INTERVAL_MINUTES = 60


def get_current_time():
    """الحصول على الوقت المحلي لعدن."""

    return datetime.now(
        ADEN_TIMEZONE
    )


def get_published_times(news_list):
    """استخراج أوقات النشر المسجلة."""

    published_times = []

    for item in news_list:

        if not item.get(
            "published_to_facebook",
            False
        ):
            continue

        published_at = item.get(
            "published_at"
        )

        if not published_at:
            continue

        try:

            published_time = datetime.fromisoformat(
                published_at
            )

            if published_time.tzinfo is None:
                published_time = published_time.replace(
                    tzinfo=ADEN_TIMEZONE
                )

            published_times.append(
                published_time.astimezone(
                    ADEN_TIMEZONE
                )
            )

        except (ValueError, TypeError):
            continue

    return published_times


def can_publish(news_list):
    """
    التحقق من الحد اليومي والفاصل الزمني.
    """

    now = get_current_time()

    published_times = get_published_times(
        news_list
    )

    today_posts = [
        published_time
        for published_time in published_times
        if published_time.date() == now.date()
    ]

    if len(today_posts) >= MAX_DAILY_POSTS:

        print(
            "⛔ Daily publishing limit reached."
        )

        return False

    if published_times:

        last_published = max(
            published_times
        )

        elapsed = now - last_published

        minimum_interval = timedelta(
            minutes=MIN_POST_INTERVAL_MINUTES
        )

        if elapsed < minimum_interval:

            remaining = (
                minimum_interval - elapsed
            )

            remaining_minutes = int(
                remaining.total_seconds() / 60
            ) + 1

            print(
                "⏳ Publishing interval not reached. "
                f"Wait approximately {remaining_minutes} minutes."
            )

            return False

    return True


def mark_as_published(news):
    """تسجيل وقت نجاح النشر."""

    news["published_at"] = (
        get_current_time().isoformat()
    )

    return news

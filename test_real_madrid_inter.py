# ============================================================
# LIVE TEST — REAL MADRID vs INTER
# اختبار حي لمباراة ريال مدريد ضد إنتر
# ============================================================

import time
import requests

from live_match_manager import (
    LiveMatchManager,
    is_finished,
)

from live_event_manager import LiveEventManager
from live_formatter import format_live_event


# ============================================================
# إعدادات المباراة
# ============================================================

MATCH_SLUG = "inter-milan-vs-real-madrid"

# الفاصل بين الفحوصات أثناء المباراة
POLL_INTERVAL = 65

# الفاصل بين محاولات الاتصال عند 503
RETRY_DELAY = 10


# ============================================================
# جلب بيانات المباراة
# ============================================================

def fetch_match_with_retry(manager):
    """
    يحاول جلب بيانات المباراة باستمرار.

    إذا أعاد SportScore خطأ 503:
    ينتظر 10 ثوانٍ ثم يحاول مرة أخرى.

    لا يوجد حد أقصى للمحاولات لأننا نريد
    أن يستمر الاختبار حتى تتوفر بيانات المباراة.
    """

    attempt = 1

    while True:

        try:

            snapshot = manager.fetch_match()

            if snapshot:

                if attempt > 1:
                    print()
                    print("✅ نجح الاتصال بعد إعادة المحاولة.")

                return snapshot

        except requests.RequestException as error:

            print(
                f"⚠️ محاولة الاتصال #{attempt} فشلت:"
            )

            print(f"   {error}")

        except Exception as error:

            print(
                f"⚠️ خطأ غير متوقع في محاولة الاتصال "
                f"#{attempt}:"
            )

            print(f"   {error}")

        print()

        print(
            f"⏳ إعادة المحاولة بعد "
            f"{RETRY_DELAY} ثانية..."
        )

        time.sleep(RETRY_DELAY)

        attempt += 1


# ============================================================
# عرض بيانات المباراة
# ============================================================

def print_match(snapshot):

    if not snapshot:

        print("❌ لا توجد بيانات للمباراة.")

        return

    teams = snapshot.get("teams", {})

    home = teams.get(
        "home",
        "Unknown"
    )

    away = teams.get(
        "away",
        "Unknown"
    )

    home_score = snapshot.get(
        "home_score"
    )

    away_score = snapshot.get(
        "away_score"
    )

    status = snapshot.get(
        "status"
    )

    status_text = snapshot.get(
        "status_text"
    )

    minute = snapshot.get(
        "live_minute"
    )

    incidents = snapshot.get(
        "incidents",
        []
    )

    print(
        f"🏠 {home}"
    )

    print(
        f"✈️ {away}"
    )

    print(
        f"⚽ Score: "
        f"{home_score} - {away_score}"
    )

    print(
        f"📌 Status: {status}"
    )

    print(
        f"📝 Status text: {status_text}"
    )

    print(
        f"⏱️ Minute: {minute}"
    )

    print(
        f"📋 Incidents: {len(incidents)}"
    )


# ============================================================
# تنسيق الحدث بأمان
# ============================================================

def format_event_safely(event, snapshot):

    try:

        return format_live_event(
            event,
            snapshot
        )

    except TypeError:

        # توافق مع نسخة formatter
        # التي تستقبل event فقط

        try:

            return format_live_event(
                event
            )

        except Exception as error:

            print(
                f"⚠️ فشل تنسيق الحدث: {error}"
            )

            return None

    except Exception as error:

        print(
            f"⚠️ فشل تنسيق الحدث: {error}"
        )

        return None


# ============================================================
# عرض الحدث
# ============================================================

def show_event(event, snapshot):

    print()

    print(
        "=" * 60
    )

    print("🚨 EVENT DETECTED")

    print(
        "=" * 60
    )

    print()

    print(
        f"🆔 Event ID: "
        f"{event.get('id')}"
    )

    print(
        f"📌 Type: "
        f"{event.get('event_type')}"
    )

    print(
        f"⏱️ Minute: "
        f"{event.get('minute')}"
    )

    print()

    # --------------------------------------------------------
    # إنشاء نص Facebook
    # --------------------------------------------------------

    message = format_event_safely(
        event,
        snapshot
    )

    if message:

        print(
            "📘 Facebook Preview:"
        )

        print()

        print(message)

        print()

        print(
            "ℹ️ اختبار فقط — "
            "لم يتم النشر على Facebook."
        )

    else:

        print(
            "⚠️ لم يتم إنشاء نص للحدث."
        )

    print()

    print(
        "=" * 60
    )


# ============================================================
# البرنامج الرئيسي
# ============================================================

def main():

    print(
        "=" * 70
    )

    print(
        "🔴 LIVE TEST — REAL MADRID vs INTER"
    )

    print(
        "=" * 70
    )

    print()

    print(
        f"🎯 Match slug: {MATCH_SLUG}"
    )

    print(
        f"🔄 Poll interval: {POLL_INTERVAL} seconds"
    )

    print(
        f"⚠️ Retry delay: {RETRY_DELAY} seconds"
    )

    print()

    # --------------------------------------------------------
    # إنشاء مدير المباراة
    # --------------------------------------------------------

    manager = LiveMatchManager(
        slug=MATCH_SLUG
    )

    event_manager = LiveEventManager()

    # ========================================================
    # الاتصال الأول
    # ========================================================

    print(
        "🔎 الحصول على بيانات المباراة..."
    )

    print()

    snapshot = fetch_match_with_retry(
        manager
    )

    # --------------------------------------------------------
    # عرض البيانات
    # --------------------------------------------------------

    print()

    print(
        "✅ تم الاتصال بالمباراة"
    )

    print()

    print_match(
        snapshot
    )

    print()

    # ========================================================
    # Bootstrap
    # ========================================================

    event_manager.bootstrap(
        snapshot
    )

    print(
        "✅ Bootstrap مكتمل"
    )

    print(
        "🚫 الأحداث القديمة لن يتم نشرها."
    )

    print()

    # ========================================================
    # إذا كانت المباراة منتهية
    # ========================================================

    if is_finished(snapshot):

        print(
            "🏁 المباراة منتهية بالفعل."
        )

        print()

        print(
            f"🏆 النتيجة النهائية: "
            f"{snapshot.get('home_score')} - "
            f"{snapshot.get('away_score')}"
        )

        return

    # ========================================================
    # المراقبة
    # ========================================================

    check_number = 1

    while True:

        print()

        print(
            "=" * 70
        )

        print(
            f"🔎 CHECK #{check_number}"
        )

        print(
            "=" * 70
        )

        print()

        # ----------------------------------------------------
        # الحصول على أحدث بيانات
        #
        # هذه الدالة لن تنتهي بسبب 503.
        # ستستمر بالمحاولة حتى تنجح.
        # ----------------------------------------------------

        snapshot = fetch_match_with_retry(
            manager
        )

        print()

        print_match(
            snapshot
        )

        print()

        # ----------------------------------------------------
        # اكتشاف الأحداث الجديدة
        # ----------------------------------------------------

        try:

            new_events = event_manager.process_snapshot(
                snapshot
            )

        except Exception as error:

            print(
                f"⚠️ خطأ أثناء تحليل الأحداث: {error}"
            )

            new_events = []

        # ----------------------------------------------------
        # الأحداث الجديدة
        # ----------------------------------------------------

        if new_events:

            print(
                f"🚨 تم اكتشاف "
                f"{len(new_events)} حدث جديد!"
            )

            for event in new_events:

                show_event(
                    event,
                    snapshot
                )

                # تسجيل الحدث كمُعالج
                event_manager.mark_processed(
                    event
                )

        else:

            print(
                "ℹ️ لا توجد أحداث جديدة."
            )

        # ----------------------------------------------------
        # التحقق من نهاية المباراة
        # ----------------------------------------------------

        if is_finished(
            snapshot
        ):

            print()

            print(
                "=" * 70
            )

            print(
                "🏁 انتهت المباراة!"
            )

            print(
                "=" * 70
            )

            print()

            print(
                f"🏆 النتيجة النهائية: "
                f"{snapshot.get('home_score')} - "
                f"{snapshot.get('away_score')}"
            )

            print()

            break

        # ----------------------------------------------------
        # الانتظار للفحص التالي
        # ----------------------------------------------------

        print()

        print(
            f"⏳ الانتظار "
            f"{POLL_INTERVAL} ثانية "
            f"قبل الفحص التالي..."
        )

        time.sleep(
            POLL_INTERVAL
        )

        check_number += 1


# ============================================================
# تشغيل
# ============================================================

if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        print()

        print(
            "🛑 تم إيقاف الاختبار يدويًا."
        )

    except Exception as error:

        print()

        print(
            "❌ حدث خطأ غير متوقع:"
        )

        print(
            error
        )

        raise

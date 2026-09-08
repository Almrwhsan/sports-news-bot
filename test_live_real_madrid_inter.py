# ============================================================
# LIVE TEST — REAL MADRID vs INTER
# اختبار مراقبة مباراة ريال مدريد ضد إنتر
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

POLL_INTERVAL = 65

RETRY_COUNT = 3

RETRY_DELAY = 10


# ============================================================
# جلب بيانات المباراة مع إعادة المحاولة
# ============================================================

def fetch_with_retry(manager):
    """
    جلب بيانات المباراة مع إعادة المحاولة
    في حال حدوث 503 أو أي خطأ في الاتصال.
    """

    last_error = None

    for attempt in range(1, RETRY_COUNT + 1):

        try:

            snapshot = manager.fetch_match()

            if snapshot:
                if attempt > 1:
                    print("✅ نجح الاتصال بعد إعادة المحاولة.")

                return snapshot

        except requests.RequestException as error:

            last_error = error

            print(
                f"⚠️ محاولة {attempt}/{RETRY_COUNT} فشلت: {error}"
            )

            if attempt < RETRY_COUNT:

                print(
                    f"⏳ إعادة المحاولة بعد {RETRY_DELAY} ثانية..."
                )

                time.sleep(RETRY_DELAY)

        except Exception as error:

            last_error = error

            print(
                f"⚠️ خطأ غير متوقع في المحاولة "
                f"{attempt}/{RETRY_COUNT}: {error}"
            )

            if attempt < RETRY_COUNT:

                print(
                    f"⏳ إعادة المحاولة بعد {RETRY_DELAY} ثانية..."
                )

                time.sleep(RETRY_DELAY)

    print("❌ فشل الحصول على بيانات المباراة.")

    if last_error:
        print(f"❌ آخر خطأ: {last_error}")

    return None


# ============================================================
# طباعة معلومات المباراة
# ============================================================

def print_match(snapshot):
    """
    عرض حالة المباراة الحالية.
    """

    if not snapshot:
        print("❌ لا توجد بيانات للمباراة.")
        return

    teams = snapshot.get("teams", {})

    home = teams.get("home", "Unknown")

    away = teams.get("away", "Unknown")

    home_score = snapshot.get("home_score")

    away_score = snapshot.get("away_score")

    status = snapshot.get("status")

    status_text = snapshot.get("status_text")

    minute = snapshot.get("live_minute")

    incidents = snapshot.get("incidents", [])

    print(f"🏠 {home}")

    print(f"✈️ {away}")

    print(
        f"⚽ Score: {home_score} - {away_score}"
    )

    print(f"📌 Status: {status}")

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
# البرنامج الرئيسي
# ============================================================

def main():

    print("=" * 70)

    print("🔴 LIVE TEST — REAL MADRID vs INTER")

    print("=" * 70)

    print()

    # --------------------------------------------------------
    # إنشاء مدير المباراة
    # --------------------------------------------------------

    manager = LiveMatchManager(
        slug=MATCH_SLUG
    )

    event_manager = LiveEventManager()

    # --------------------------------------------------------
    # أول جلب
    # --------------------------------------------------------

    print("🔎 الحصول على بيانات المباراة...")

    snapshot = fetch_with_retry(manager)

    if not snapshot:

        print()

        print("❌ تعذر الحصول على بيانات المباراة.")

        return

    print()

    print("✅ تم الاتصال بالمباراة")

    print_match(snapshot)

    print()

    # --------------------------------------------------------
    # Bootstrap
    #
    # الأحداث الموجودة قبل بدء الاختبار سيتم اعتبارها قديمة
    # ولن يتم نشرها.
    # --------------------------------------------------------

    event_manager.bootstrap(snapshot)

    print("✅ Bootstrap مكتمل")

    print("🚫 الأحداث القديمة لن يتم نشرها.")

    print()

    # --------------------------------------------------------
    # إذا كانت المباراة منتهية بالفعل
    # --------------------------------------------------------

    if is_finished(snapshot):

        print("🏁 المباراة منتهية بالفعل.")

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

        print("=" * 70)

        print(f"🔎 CHECK #{check_number}")

        print("=" * 70)

        print()

        # ----------------------------------------------------
        # جلب أحدث بيانات
        # ----------------------------------------------------

        new_snapshot = fetch_with_retry(manager)

        if not new_snapshot:

            print()

            print(
                "⚠️ تعذر الحصول على تحديث جديد."
            )

            print(
                f"⏳ الانتظار {POLL_INTERVAL} ثانية..."
            )

            time.sleep(POLL_INTERVAL)

            check_number += 1

            continue

        snapshot = new_snapshot

        # ----------------------------------------------------
        # عرض حالة المباراة
        # ----------------------------------------------------

        print_match(snapshot)

        print()

        # ----------------------------------------------------
        # اكتشاف الأحداث الجديدة
        # ----------------------------------------------------

        new_events = event_manager.process_snapshot(
            snapshot
        )

        # ----------------------------------------------------
        # معالجة الأحداث
        # ----------------------------------------------------

        if new_events:

            print()

            print(
                f"🚨 تم اكتشاف "
                f"{len(new_events)} حدث جديد!"
            )

            print()

            for event in new_events:

                print("-" * 60)

                print(
                    f"🆕 Event ID: "
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

                # ------------------------------------------------
                # تنسيق الحدث
                # ------------------------------------------------

                try:

                    message = format_live_event(
                        event,
                        snapshot
                    )

                except TypeError:

                    # توافق مع أي نسخة من formatter
                    # تستخدم event فقط

                    message = format_live_event(
                        event
                    )

                except Exception as error:

                    print(
                        f"⚠️ فشل تنسيق الحدث: {error}"
                    )

                    message = None

                # ------------------------------------------------
                # عرض منشور Facebook فقط
                #
                # لا يوجد نشر حقيقي هنا.
                # ------------------------------------------------

                if message:

                    print()

                    print(
                        "📘 Facebook Preview:"
                    )

                    print()

                    print(message)

                    print()

                    print(
                        "ℹ️ لم يتم النشر على Facebook "
                        "(اختبار فقط)."
                    )

                else:

                    print(
                        "⚠️ لم يتم إنشاء نص للحدث."
                    )

                # ------------------------------------------------
                # تسجيل الحدث كمُعالج
                # ------------------------------------------------

                event_manager.mark_processed(
                    event
                )

                print("-" * 60)

        else:

            print(
                "ℹ️ لا توجد أحداث جديدة."
            )

        print()

        # ----------------------------------------------------
        # التحقق من انتهاء المباراة
        # ----------------------------------------------------

        if is_finished(snapshot):

            print("=" * 70)

            print("🏁 انتهت المباراة!")

            print("=" * 70)

            print()

            print(
                f"🏆 النتيجة النهائية: "
                f"{snapshot.get('home_score')} - "
                f"{snapshot.get('away_score')}"
            )

            print()

            break

        # ----------------------------------------------------
        # الانتظار قبل الفحص التالي
        # ----------------------------------------------------

        print(
            f"⏳ الانتظار "
            f"{POLL_INTERVAL} ثانية قبل الفحص التالي..."
        )

        time.sleep(POLL_INTERVAL)

        check_number += 1


# ============================================================
# تشغيل البرنامج
# ============================================================

if __name__ == "__main__":
    main()

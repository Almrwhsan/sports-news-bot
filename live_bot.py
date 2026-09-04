import time

from live_match_manager import LiveMatchManager
from live_event_manager import (
    LiveEventManager,
    event_label,
    describe_event,
)
from facebook_publisher import publish_post


# ============================================================
# إعدادات المباراة
# ============================================================

MATCH_SLUG = "real-betis-vs-real-madrid"

# SportScore قد يحتفظ بالبيانات مؤقتًا لنحو دقيقة.
POLL_INTERVAL = 65


# ============================================================
# النشر على Facebook
# ============================================================

# True  = النشر الحقيقي
# False = اختبار بدون نشر
PUBLISH_TO_FACEBOOK = True


# ============================================================
# Live Bot
# ============================================================

class LiveBot:

    def __init__(self):

        self.event_manager = LiveEventManager()

        self.match_manager = LiveMatchManager(
            slug=MATCH_SLUG,
            poll_interval=POLL_INTERVAL,
            event_manager=self.event_manager,
        )

    # --------------------------------------------------------
    # إنشاء رسالة الحدث
    # --------------------------------------------------------

    def format_event_message(self, event):

        label = event_label(event)
        description = describe_event(event)

        return (
            f"🚨 {label}\n\n"
            f"{description}\n\n"
            f"نبض مدريد"
        )

    # --------------------------------------------------------
    # نشر الحدث
    # --------------------------------------------------------

    def publish_event(self, event):

        message = self.format_event_message(event)

        print()
        print("=" * 70)
        print("EVENT READY FOR FACEBOOK")
        print("=" * 70)
        print(message)
        print("=" * 70)

        # ----------------------------------------------------
        # وضع الاختبار
        # ----------------------------------------------------

        if not PUBLISH_TO_FACEBOOK:

            print("🧪 DRY RUN")
            print("Facebook publishing is disabled.")
            print("Nothing was published.")

            return {
                "success": False,
                "published": False,
                "post_id": None,
                "error": "Dry run mode.",
            }

        # ----------------------------------------------------
        # النشر الحقيقي
        # ----------------------------------------------------

        print("📤 Publishing event to Facebook...")

        result = publish_post(
            message=message,
            image_path=None,
        )

        if result.get("success"):

            print()
            print("✅ EVENT PUBLISHED SUCCESSFULLY")
            print("Post ID:", result.get("post_id"))

        else:

            print()
            print("❌ EVENT PUBLISHING FAILED")
            print("Facebook error:", result.get("error"))

        return result

    # --------------------------------------------------------
    # تشغيل دورة واحدة
    # --------------------------------------------------------

    def run_once(self):

        print()
        print("=" * 70)
        print("LIVE BOT — CHECK")
        print("=" * 70)

        # ----------------------------------------------------
        # جلب المباراة
        # ----------------------------------------------------

        print()
        print("STEP 1 — FETCH MATCH")

        match = self.match_manager.fetch_match()

        if not match:

            print("❌ Failed to fetch match.")

            return None

        print("✅ Match data received.")

        # ----------------------------------------------------
        # تحليل المباراة
        # ----------------------------------------------------

        print()
        print("STEP 2 — INSPECT MATCH")

        result = self.match_manager.inspect_match(match)

        if not result:

            print("❌ Failed to inspect match.")

            return None

        # ----------------------------------------------------
        # معلومات المباراة
        # ----------------------------------------------------

        print()
        print("STEP 3 — MATCH STATUS")

        print("Home      :", result.get("home"))
        print("Away      :", result.get("away"))

        print(
            "Score     :",
            result.get("home_score"),
            "-",
            result.get("away_score"),
        )

        print("Status    :", result.get("status"))
        print("Minute    :", result.get("minute"))

        # ----------------------------------------------------
        # الأحداث
        # ----------------------------------------------------

        incidents = result.get("incidents", [])

        print("Incidents :", len(incidents))

        if not incidents:

            print()
            print("ℹ️ No incidents found.")

            return result

        # ----------------------------------------------------
        # عرض الأحداث الخام للتشخيص
        # ----------------------------------------------------

        print()
        print("STEP 4 — INCIDENT INSPECTION")

        for index, incident in enumerate(incidents, start=1):

            print()
            print(f"INCIDENT #{index}")
            print("-" * 70)

            if not isinstance(incident, dict):

                print("Invalid incident:", incident)

                continue

            print("Time       :", incident.get("time"))
            print("Type       :", incident.get("type"))
            print("Type ID    :", incident.get("type_id"))
            print("Side       :", incident.get("side"))
            print("Player     :", incident.get("player"))
            print("Is goal    :", incident.get("is_goal"))
            print("Home score :", incident.get("home_score"))
            print("Away score :", incident.get("away_score"))

        # ----------------------------------------------------
        # اكتشاف الأحداث الجديدة
        # ----------------------------------------------------

        print()
        print("STEP 5 — EVENT DETECTION")

        # مهم جدًا:
        # process_snapshot() يحتاج snapshot المباراة
        # وليس قائمة incidents فقط.
        #
        # إرسال incidents مباشرة كان سببًا رئيسيًا في:
        #
        # Incidents: 1
        # New events: 0
        #
        # لأن LiveEventManager يستخرج incidents من الـ snapshot.

        new_events = self.event_manager.process_snapshot(
            result
        )

        print("New events:", len(new_events))

        if not new_events:

            print("ℹ️ No new events.")

            return result

        # ----------------------------------------------------
        # معالجة الأحداث
        # ----------------------------------------------------

        print()
        print("STEP 6 — EVENT PUBLISHING")

        for event in new_events:

            print()
            print("=" * 70)
            print("🆕 NEW EVENT DETECTED")
            print("=" * 70)

            print("Event type :", event.get("event_type"))
            print("Label      :", event_label(event))
            print("Minute     :", event.get("minute"))
            print("Player     :", event.get("player"))
            print(
                "Score      :",
                event.get("home_score"),
                "-",
                event.get("away_score"),
            )

            # ------------------------------------------------
            # محاولة النشر
            # ------------------------------------------------

            publish_result = self.publish_event(event)

            # ------------------------------------------------
            # تسجيل الحدث كمُعالج
            # بعد نجاح النشر فقط
            # ------------------------------------------------

            if publish_result.get("success"):

                self.event_manager.mark_processed(
                    [event]
                )

                print()
                print("✅ Event completed successfully.")
                print("✅ Event marked as processed.")

            else:

                print()
                print(
                    "⚠️ Event was not published successfully."
                )

                print(
                    "⚠️ Event was NOT marked as processed."
                )

                print(
                    "It will be retried on the next check."
                )

        return result

    # --------------------------------------------------------
    # التشغيل المستمر
    # --------------------------------------------------------

    def run(self):

        print("=" * 70)
        print("LIVE FOOTBALL BOT")
        print("=" * 70)

        print("Match:", MATCH_SLUG)
        print("Poll interval:", POLL_INTERVAL)

        print(
            "Facebook publishing:",
            "ENABLED" if PUBLISH_TO_FACEBOOK else "DISABLED",
        )

        print()

        # ----------------------------------------------------
        # تهيئة الأحداث الموجودة قبل بدء المراقبة
        # ----------------------------------------------------

        print("Initializing live event state...")

        self.match_manager.bootstrap()

        print("Bootstrap complete.")

        print()
        print("🚀 LIVE MONITOR STARTED")

        # ----------------------------------------------------
        # المراقبة المستمرة
        # ----------------------------------------------------

        while True:

            try:

                result = self.run_once()

            except Exception as error:

                print()
                print("=" * 70)
                print("❌ LIVE BOT ERROR")
                print("=" * 70)

                print(type(error).__name__)
                print(error)

                print()
                print(
                    f"⏳ Retrying in {POLL_INTERVAL} seconds..."
                )

                time.sleep(POLL_INTERVAL)

                continue

            # ------------------------------------------------
            # فشل جلب البيانات
            # ------------------------------------------------

            if result is None:

                print()
                print(
                    f"⚠️ No valid match data. "
                    f"Retrying in {POLL_INTERVAL} seconds..."
                )

                time.sleep(POLL_INTERVAL)

                continue

            # ------------------------------------------------
            # المباراة انتهت
            # ------------------------------------------------

            if result.get("finished"):

                print()
                print("=" * 70)
                print("🏁 MATCH FINISHED")
                print("=" * 70)

                print(
                    "Final score:",
                    result.get("home_score"),
                    "-",
                    result.get("away_score"),
                )

                break

            # ------------------------------------------------
            # الانتظار قبل الفحص التالي
            # ------------------------------------------------

            print()
            print("=" * 70)
            print(
                f"⏳ Waiting {POLL_INTERVAL} seconds..."
            )
            print("=" * 70)

            time.sleep(POLL_INTERVAL)


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    bot = LiveBot()

    bot.run()

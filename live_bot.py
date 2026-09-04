import time

from live_match_manager import LiveMatchManager
from live_event_manager import LiveEventManager
from facebook_publisher import publish_post


# ============================================================
# إعدادات المباراة
# ============================================================

MATCH_SLUG = "real-betis-vs-real-madrid"

# SportScore قد يحتفظ بالبيانات مؤقتًا لنحو دقيقة.
POLL_INTERVAL = 65

# ============================================================
# وضع الاختبار
# ============================================================

# False = يعرض الأحداث فقط ولا ينشر على Facebook
# True  = ينشر الأحداث المكتشفة على Facebook
PUBLISH_TO_FACEBOOK = False


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
    # إنشاء نص الحدث
    # --------------------------------------------------------

    def format_event_message(self, event):

        label = self.event_manager.event_label(event)
        description = self.event_manager.describe_event(event)

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

        print("=" * 70)
        print("EVENT READY FOR FACEBOOK")
        print("=" * 70)
        print(message)
        print("=" * 70)

        # ----------------------------------------------------
        # Dry Run
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
        # Facebook
        # ----------------------------------------------------

        print("📤 Publishing event to Facebook...")

        result = publish_post(
            message=message,
            image_path=None,
        )

        if result.get("success"):

            print("✅ Event published successfully.")
            print("Post ID:", result.get("post_id"))

        else:

            print("❌ Event publishing failed.")
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

        # جلب المباراة
        match = self.match_manager.fetch_match()

        # تحليل المباراة
        result = self.match_manager.inspect_match(match)

        if not result:

            print("❌ Failed to inspect match.")
            return None

        # ----------------------------------------------------
        # معلومات المباراة
        # ----------------------------------------------------

        print()
        print("MATCH STATUS:")
        print("Home      :", result.get("home"))
        print("Away      :", result.get("away"))
        print("Score     :", result.get("home_score"), "-", result.get("away_score"))
        print("Status    :", result.get("status"))
        print("Minute    :", result.get("minute"))

        # ----------------------------------------------------
        # الأحداث
        # ----------------------------------------------------

        incidents = result.get("incidents", [])

        print("Incidents :", len(incidents))

        if not incidents:

            print("No incidents found.")

            return result

        # ----------------------------------------------------
        # اكتشاف الأحداث الجديدة
        # ----------------------------------------------------

        new_events = self.event_manager.process_snapshot(
            incidents
        )

        print()
        print("NEW EVENTS:", len(new_events))

        # ----------------------------------------------------
        # معالجة الأحداث
        # ----------------------------------------------------

        for event in new_events:

            print()
            print("🆕 NEW EVENT")

            self.publish_event(event)

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
        # Bootstrap
        # ----------------------------------------------------

        print("Initializing live event state...")

        self.match_manager.bootstrap()

        print("Bootstrap complete.")

        print()

        # ----------------------------------------------------
        # مراقبة المباراة
        # ----------------------------------------------------

        while True:

            result = self.run_once()

            if result is None:

                print("⚠️ No match data.")
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

                break

            # ------------------------------------------------
            # الانتظار
            # ------------------------------------------------

            print()
            print(
                f"⏳ Waiting {POLL_INTERVAL} seconds for next update..."
            )

            time.sleep(POLL_INTERVAL)


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    bot = LiveBot()

    bot.run()

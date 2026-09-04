import time

from live_match_manager import LiveMatchManager
from live_event_manager import LiveEventManager
from facebook_publisher import publish_post


# ============================================================
# إعدادات المباراة
# ============================================================

MATCH_SLUG = "real-betis-vs-real-madrid"

POLL_INTERVAL = 65

# مهم جدًا:
# False = اختبار فقط، لا يوجد نشر على Facebook
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
    # إنشاء رسالة الحدث
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

        print()
        print("=" * 70)
        print("EVENT READY FOR FACEBOOK")
        print("=" * 70)
        print(message)
        print("=" * 70)

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
    # اختبار دورة واحدة
    # --------------------------------------------------------

    def run_once(self):

        print()
        print("=" * 70)
        print("LIVE BOT — ONE TIME TEST")
        print("=" * 70)

        print("Match:", MATCH_SLUG)

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
        print("Score     :", result.get("home_score"), "-", result.get("away_score"))
        print("Status    :", result.get("status"))
        print("Minute    :", result.get("minute"))

        # ----------------------------------------------------
        # الأحداث
        # ----------------------------------------------------

        incidents = result.get("incidents", [])

        print("Incidents :", len(incidents))

        # ----------------------------------------------------
        # لا توجد أحداث
        # ----------------------------------------------------

        if not incidents:

            print()
            print("ℹ️ No incidents found.")

            return result

        # ----------------------------------------------------
        # اكتشاف الأحداث الجديدة
        # ----------------------------------------------------

        print()
        print("STEP 4 — EVENT DETECTION")

        new_events = self.event_manager.process_snapshot(
            incidents
        )

        print("New events:", len(new_events))

        # ----------------------------------------------------
        # الأحداث الجديدة
        # ----------------------------------------------------

        if not new_events:

            print("ℹ️ No new events.")

            return result

        # ----------------------------------------------------
        # معالجة الأحداث
        # ----------------------------------------------------

        print()
        print("STEP 5 — EVENT OUTPUT")

        for event in new_events:

            print()
            print("🆕 NEW EVENT")

            self.publish_event(event)

        # ----------------------------------------------------
        # النهاية
        # ----------------------------------------------------

        print()
        print("=" * 70)
        print("ONE TIME TEST COMPLETE")
        print("=" * 70)

        return result


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    bot = LiveBot()

    bot.run_once()

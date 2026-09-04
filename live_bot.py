import os
import time

from live_match_manager import LiveMatchManager
from live_event_manager import LiveEventManager
from facebook_publisher import publish_post


# ============================================================
# إعدادات المباراة
# ============================================================

MATCH_SLUG = "real-betis-vs-real-madrid"

POLL_INTERVAL = 65


# ============================================================
# إعداد النشر
# ============================================================

# False = اختبار بدون نشر
# True  = نشر فعلي على Facebook
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
    # تجهيز رسالة الحدث
    # --------------------------------------------------------

    def format_event_message(self, event):

        label = self.event_manager.event_label(
            event
        )

        description = (
            self.event_manager.describe_event(
                event
            )
        )

        return (
            f"🚨 {label}\n\n"
            f"{description}\n\n"
            f"نبض مدريد"
        )

    # --------------------------------------------------------
    # نشر حدث
    # --------------------------------------------------------

    def publish_event(self, event):

        message = self.format_event_message(
            event
        )

        print()
        print("=" * 70)
        print("EVENT READY FOR FACEBOOK")
        print("=" * 70)

        print(message)

        # ----------------------------------------------------
        # وضع الاختبار
        # ----------------------------------------------------

        if not PUBLISH_TO_FACEBOOK:

            print()
            print(
                "🧪 DRY RUN"
            )

            print(
                "Facebook publishing is disabled."
            )

            print(
                "Nothing was published."
            )

            return {
                "success": False,
                "published": False,
                "post_id": None,
                "error": "Dry run mode."
            }

        # ----------------------------------------------------
        # النشر الحقيقي
        # ----------------------------------------------------

        print()
        print(
            "📤 Publishing event to Facebook..."
        )

        result = publish_post(
            message=message,
            image_path=None,
        )

        if result.get("success"):

            print()
            print(
                "✅ EVENT PUBLISHED SUCCESSFULLY"
            )

            print(
                "Post ID:",
                result.get("post_id")
            )

        else:

            print()
            print(
                "❌ EVENT PUBLISH FAILED"
            )

            print(
                "Error:",
                result.get("error")
            )

        return result

    # --------------------------------------------------------
    # تشغيل Snapshot واحدة
    # --------------------------------------------------------

    def run_once(self):

        print()
        print("=" * 70)
        print("FETCHING SPORTScore MATCH")
        print("=" * 70)

        match = self.match_manager.fetch_match()

        result = self.match_manager.inspect_match(
            match
        )

        # ----------------------------------------------------
        # الأحداث
        # ----------------------------------------------------

        incidents = result.get(
            "incidents",
            []
        )

        if not incidents:

            print()
            print(
                "No incidents found."
            )

            return result

        # ----------------------------------------------------
        # اكتشاف الأحداث الجديدة
        # ----------------------------------------------------

        new_events = (
            self.event_manager.process_snapshot(
                incidents
            )
        )

        print()
        print(
            f"NEW EVENTS: {len(new_events)}"
        )

        # ----------------------------------------------------
        # نشر كل حدث جديد
        # ----------------------------------------------------

        for event in new_events:

            self.publish_event(
                event
            )

        return result

    # --------------------------------------------------------
    # التشغيل الرئيسي
    # --------------------------------------------------------

    def run(self):

        print("=" * 70)
        print("NABD MADRID — LIVE FOOTBALL BOT")
        print("=" * 70)

        print()
        print(
            f"Match: {MATCH_SLUG}"
        )

        print(
            f"Poll interval: {POLL_INTERVAL} seconds"
        )

        print(
            "Facebook:",
            "ENABLED"
            if PUBLISH_TO_FACEBOOK
            else "DRY RUN"
        )

        # ----------------------------------------------------
        # Bootstrap
        # ----------------------------------------------------

        print()
        print("=" * 70)
        print("BOOTSTRAP")
        print("=" * 70)

        try:

            self.match_manager.bootstrap()

        except Exception as exc:

            print()
            print(
                "❌ Bootstrap failed:"
            )

            print(exc)

            return

        print()
        print(
            "Existing incidents will NOT be published."
        )

        # ----------------------------------------------------
        # مراقبة المباراة
        # ----------------------------------------------------

        print()
        print("=" * 70)
        print("LIVE MONITOR STARTED")
        print("=" * 70)

        while True:

            try:

                result = self.run_once()

                if result.get("finished"):

                    print()
                    print(
                        "🏁 MATCH FINISHED"
                    )

                    break

            except Exception as exc:

                print()
                print(
                    "❌ LIVE BOT ERROR:"
                )

                print(exc)

            print()
            print(
                f"⏳ Waiting {POLL_INTERVAL} seconds..."
            )

            time.sleep(
                POLL_INTERVAL
            )


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    bot = LiveBot()

    bot.run()

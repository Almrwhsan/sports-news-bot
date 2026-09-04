import os
import time

from live_match_manager import LiveMatchManager
from facebook_publisher import FacebookPublisher


# ============================================================
# إعدادات المباراة
# ============================================================

MATCH_SLUG = "real-betis-vs-real-madrid"

POLL_INTERVAL = 65

# مهم:
# False = مراقبة فقط بدون نشر
# True  = السماح بالنشر على فيسبوك
PUBLISH_TO_FACEBOOK = False


# ============================================================
# Facebook
# ============================================================

def create_facebook_publisher():
    page_id = os.getenv("FACEBOOK_PAGE_ID")
    access_token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")

    if not page_id or not access_token:
        raise RuntimeError(
            "Facebook credentials are missing."
        )

    return FacebookPublisher(
        page_id=page_id,
        access_token=access_token,
    )


# ============================================================
# نشر الحدث
# ============================================================

def publish_event(publisher, event, event_manager):
    """
    تجهيز نص الحدث ونشره على Facebook.
    """

    label = event_manager.event_label(event)
    description = event_manager.describe_event(event)

    message = f"🚨 {label}\n\n{description}"

    print()
    print("=" * 70)
    print("FACEBOOK EVENT")
    print("=" * 70)
    print(message)

    if not PUBLISH_TO_FACEBOOK:
        print()
        print("PUBLISH_TO_FACEBOOK = False")
        print("DRY RUN — NOTHING WAS PUBLISHED.")

        return False

    try:

        result = publisher.publish_text(message)

        print()
        print("FACEBOOK PUBLISH RESULT:")
        print(result)

        return True

    except Exception as exc:

        print()
        print("FACEBOOK PUBLISH ERROR:")
        print(exc)

        return False


# ============================================================
# Live Bot
# ============================================================

class LiveBot:

    def __init__(self):

        self.event_manager = None
        self.match_manager = None
        self.facebook = None

    # --------------------------------------------------------
    # إنشاء النظام
    # --------------------------------------------------------

    def setup(self):

        print("=" * 70)
        print("NABD MADRID — LIVE BOT")
        print("=" * 70)

        print()
        print(f"Match slug: {MATCH_SLUG}")
        print(f"Poll interval: {POLL_INTERVAL}s")
        print(
            "Facebook publishing:",
            PUBLISH_TO_FACEBOOK
        )

        self.facebook = create_facebook_publisher()

        self.match_manager = LiveMatchManager(
            slug=MATCH_SLUG,
            poll_interval=POLL_INTERVAL,
        )

        self.event_manager = (
            self.match_manager.event_manager
        )

    # --------------------------------------------------------
    # تشغيل Snapshot واحدة
    # --------------------------------------------------------

    def run_once(self):

        print()
        print("=" * 70)
        print("FETCHING LIVE MATCH")
        print("=" * 70)

        match = self.match_manager.fetch_match()

        result = self.match_manager.inspect_match(
            match
        )

        incidents = result["incidents"]

        if not incidents:

            print()
            print("No incidents found.")

            return result

        # ----------------------------------------------------
        # الأحداث الجديدة
        # ----------------------------------------------------

        new_events = (
            self.event_manager.process_snapshot(
                incidents
            )
        )

        print()
        print(
            f"NEW EVENTS FOR PUBLISHING: "
            f"{len(new_events)}"
        )

        for event in new_events:

            publish_event(
                self.facebook,
                event,
                self.event_manager,
            )

        return result

    # --------------------------------------------------------
    # تشغيل
    # --------------------------------------------------------

    def run(self):

        self.setup()

        print()
        print("=" * 70)
        print("LIVE BOT STARTED")
        print("=" * 70)

        # ----------------------------------------------------
        # Bootstrap
        # ----------------------------------------------------

        print()
        print("BOOTSTRAP")

        self.match_manager.bootstrap()

        print()
        print(
            "Existing events will NOT be published."
        )

        # ----------------------------------------------------
        # مراقبة مستمرة
        # ----------------------------------------------------

        while True:

            try:

                result = self.run_once()

                if result["finished"]:

                    print()
                    print(
                        "MATCH FINISHED."
                    )

                    break

            except Exception as exc:

                print()
                print(
                    "LIVE BOT ERROR:"
                )
                print(exc)

            print()
            print(
                f"Waiting {POLL_INTERVAL} seconds..."
            )

            time.sleep(POLL_INTERVAL)


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    bot = LiveBot()

    bot.run()

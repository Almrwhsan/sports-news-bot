import time
import requests

from live_match_manager import LiveMatchManager
from live_event_manager import LiveEventManager
from live_formatter import format_live_event


MATCH_SLUG = "inter-milan-vs-real-madrid"

POLL_INTERVAL = 65
RETRY_COUNT = 3
RETRY_DELAY = 10


def fetch_with_retry(manager):
    for attempt in range(1, RETRY_COUNT + 1):
        try:
            return manager.fetch_match()

        except requests.RequestException as error:
            print(
                f"⚠️ محاولة {attempt}/{RETRY_COUNT} فشلت: {error}"
            )

            if attempt < RETRY_COUNT:
                print(
                    f"⏳ إعادة المحاولة بعد {RETRY_DELAY} ثانية..."
                )
                time.sleep(RETRY_DELAY)

    return None


def print_match(snapshot):
    print(f"🏠 {snapshot.get('home')}")
    print(f"✈️ {snapshot.get('away')}")
    print(
        f"⚽ Score: "
        f"{snapshot.get('home_score')} - "
        f"{snapshot.get('away_score')}"
    )
    print(f"📌 Status: {snapshot.get('status')}")
    print(f"📝 Status text: {snapshot.get('status_text')}")
    print(f"⏱️ Minute: {snapshot.get('live_minute')}")
    print(
        f"📋 Incidents: "
        f"{len(snapshot.get('incidents', []))}"
    )


def main():

    print("=" * 70)
    print("🔴 LIVE TEST — REAL MADRID vs INTER")
    print("=" * 70)

    manager = LiveMatchManager(
        slug=MATCH_SLUG,
        poll_interval=POLL_INTERVAL,
    )

    event_manager = LiveEventManager()

    # =========================================================
    # INITIAL SNAPSHOT
    # =========================================================

    print("\n🔎 الحصول على بيانات المباراة...")

    snapshot = fetch_with_retry(manager)

    if not snapshot:
        print("❌ تعذر الحصول على بيانات المباراة.")
        return

    print("\n✅ تم الاتصال بالمباراة")
    print_match(snapshot)

    # =========================================================
    # BOOTSTRAP
    # =========================================================

    event_manager.bootstrap(snapshot)

    print("\n✅ Bootstrap مكتمل")
    print("🚫 الأحداث القديمة لن يتم نشرها.")

    # =========================================================
    # MONITOR
    # =========================================================

    check_number = 0

    while True:

        check_number += 1

        print("\n" + "=" * 70)
        print(f"🔎 CHECK #{check_number}")
        print("=" * 70)

        snapshot = fetch_with_retry(manager)

        if not snapshot:
            print("⚠️ تعذر الحصول على تحديث.")
            print(f"⏳ الانتظار {POLL_INTERVAL} ثانية...")
            time.sleep(POLL_INTERVAL)
            continue

        print_match(snapshot)

        # =====================================================
        # NEW EVENTS
        # =====================================================

        new_events = event_manager.process_snapshot(snapshot)

        if new_events:

            print("\n🚨 NEW EVENTS")
            print("-" * 70)

            for event in new_events:

                print("\n🔥 EVENT:")
                print(event)

                try:
                    message = format_live_event(event)

                    print("\n📱 FACEBOOK MESSAGE PREVIEW:")
                    print("-" * 70)
                    print(message)
                    print("-" * 70)

                except Exception as error:
                    print(
                        f"⚠️ خطأ في تنسيق الحدث: {error}"
                    )

                event_id = event.get("id")

                if event_id is not None:
                    event_manager.mark_processed(event_id)

        else:
            print("\nℹ️ لا توجد أحداث جديدة.")

        # =====================================================
        # FINISHED
        # =====================================================

        if manager.is_finished(snapshot):

            print("\n" + "=" * 70)
            print("🏁 MATCH FINISHED")
            print("=" * 70)

            home = snapshot.get("home")
            away = snapshot.get("away")
            home_score = snapshot.get("home_score")
            away_score = snapshot.get("away_score")

            print(
                f"🏆 FINAL SCORE: "
                f"{home} {home_score} - "
                f"{away_score} {away}"
            )

            break

        print(
            f"\n⏳ انتظار {POLL_INTERVAL} ثانية..."
        )

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()

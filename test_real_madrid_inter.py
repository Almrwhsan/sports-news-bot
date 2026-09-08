from live_match_manager import LiveMatchManager


MATCH_SLUG = "inter-milan-vs-real-madrid"


def main():
    manager = LiveMatchManager(MATCH_SLUG)

    print("=" * 60)
    print("REAL MADRID vs INTER — SPORTScore TEST")
    print("=" * 60)

    result = manager.fetch_match()

    if not result:
        print("❌ لم يتم الحصول على بيانات المباراة.")
        return

    print("\n✅ تم الحصول على بيانات المباراة")

    print("Home :", result.get("home"))
    print("Away :", result.get("away"))
    print("Score:", result.get("home_score"), "-", result.get("away_score"))
    print("Status:", result.get("status"))
    print("Status text:", result.get("status_text"))
    print("Minute:", result.get("minute"))
    print("Incidents:", len(result.get("incidents", [])))

    print("\n--- Logos ---")
    print("Home logo:", result.get("home_logo"))
    print("Away logo:", result.get("away_logo"))
    print("Competition:", result.get("competition"))
    print("Competition logo:", result.get("competition_logo"))

    print("\n--- Lineups ---")
    lineups = result.get("lineups")

    if lineups:
        print("✅ Lineups موجودة")
    else:
        print("⚠️ لا توجد Lineups")

    print("\n--- Full result keys ---")
    print(result.keys())


if __name__ == "__main__":
    main()

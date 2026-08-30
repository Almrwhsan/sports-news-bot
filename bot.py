from datetime import datetime, timezone
from database import init_database


def main():
    print("===================================")
    print("   SPORTS NEWS BOT")
    print("===================================")

    init_database()

    print("Database initialized successfully!")
    print("Bot is working successfully!")
    print(
        "UTC time:",
        datetime.now(timezone.utc).isoformat()
    )

    print("===================================")


if __name__ == "__main__":
    main()

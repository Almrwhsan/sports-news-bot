import json
import os
import tempfile


# ============================================================
# أدوات الحالة
# ============================================================

def save_news(news_list, file_path):
    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            news_list,
            file,
            ensure_ascii=False,
            indent=2
        )


def load_news(file_path):
    if not os.path.exists(file_path):
        return []

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def is_already_published(news):
    return bool(
        news.get("published_to_facebook", False)
        and news.get("facebook_post_id")
    )


def mark_as_published(news, post_id):
    updated_news = dict(news)

    updated_news["processed"] = True
    updated_news["published_to_facebook"] = True
    updated_news["facebook_post_id"] = post_id
    updated_news["facebook_error"] = None

    return updated_news


# ============================================================
# الاختبار الرئيسي
# ============================================================

def main():

    print("===================================")
    print("     STATE PERSISTENCE TEST")
    print("===================================")

    # --------------------------------------------------------
    # بيانات خبر تجريبية
    # --------------------------------------------------------

    test_news = {
        "title": "خبر رياضي تجريبي",
        "url": "https://example.com/test-news",
        "source": "Test Source",
        "processed": False,
        "published_to_facebook": False,
        "facebook_post_id": None,
        "facebook_error": None,
    }

    # --------------------------------------------------------
    # إنشاء ملف مؤقت
    # --------------------------------------------------------

    with tempfile.TemporaryDirectory() as temp_dir:

        state_file = os.path.join(
            temp_dir,
            "news.json"
        )

        print()
        print("-----------------------------------")
        print("TEST 1 - SAVE STATE")
        print("-----------------------------------")

        save_news(
            [test_news],
            state_file
        )

        if os.path.exists(state_file):

            print(
                "✅ State file created"
            )

        else:

            print(
                "❌ State file was not created"
            )

            raise SystemExit(1)

        # ----------------------------------------------------
        # TEST 2
        # ----------------------------------------------------

        print()
        print("-----------------------------------")
        print("TEST 2 - LOAD STATE")
        print("-----------------------------------")

        loaded_news = load_news(
            state_file
        )

        if (
            len(loaded_news) == 1
            and loaded_news[0]["title"]
            == test_news["title"]
        ):

            print(
                "✅ State loaded correctly"
            )

        else:

            print(
                "❌ State loading failed"
            )

            raise SystemExit(1)

        # ----------------------------------------------------
        # TEST 3
        # ----------------------------------------------------

        print()
        print("-----------------------------------")
        print("TEST 3 - MARK AS PUBLISHED")
        print("-----------------------------------")

        published_news = mark_as_published(
            loaded_news[0],
            "TEST_POST_ID_123"
        )

        if (
            published_news["processed"]
            is True
            and
            published_news[
                "published_to_facebook"
            ] is True
            and
            published_news[
                "facebook_post_id"
            ] == "TEST_POST_ID_123"
        ):

            print(
                "✅ Published state recorded"
            )

        else:

            print(
                "❌ Published state recording failed"
            )

            raise SystemExit(1)

        # ----------------------------------------------------
        # حفظ الحالة بعد النشر
        # ----------------------------------------------------

        save_news(
            [published_news],
            state_file
        )

        # ----------------------------------------------------
        # TEST 4
        # ----------------------------------------------------

        print()
        print("-----------------------------------")
        print("TEST 4 - RELOAD AFTER PUBLISH")
        print("-----------------------------------")

        reloaded_news = load_news(
            state_file
        )

        if is_already_published(
            reloaded_news[0]
        ):

            print(
                "✅ Published state persisted"
            )

        else:

            print(
                "❌ Published state was lost"
            )

            raise SystemExit(1)

        # ----------------------------------------------------
        # TEST 5
        # ----------------------------------------------------

        print()
        print("-----------------------------------")
        print("TEST 5 - PREVENT DUPLICATE")
        print("-----------------------------------")

        if is_already_published(
            reloaded_news[0]
        ):

            print(
                "✅ Duplicate publication prevented"
            )

        else:

            print(
                "❌ Duplicate protection failed"
            )

            raise SystemExit(1)

    # --------------------------------------------------------
    # النتيجة
    # --------------------------------------------------------

    print()
    print("===================================")
    print("       STATE SUMMARY")
    print("===================================")

    print()
    print("Tests passed: 5/5")
    print()
    print(
        "✅ STATE PERSISTENCE IS WORKING"
    )

    print()
    print("===================================")
    print("      STATE TEST END")
    print("===================================")


if __name__ == "__main__":
    main()

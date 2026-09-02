# ============================================================
# مدير المصادر
# ============================================================

import feedparser


# ============================================================
# جلب الأخبار من مصدر واحد
# ============================================================

def fetch_source(source):

    # --------------------------------------------------------
    # التحقق من تفعيل المصدر
    # --------------------------------------------------------

    if not source.get("enabled", True):

        return []


    # --------------------------------------------------------
    # قراءة رابط RSS
    # --------------------------------------------------------

    feed_url = source.get("feed")

    if not feed_url:

        return []


    # --------------------------------------------------------
    # قراءة RSS
    # --------------------------------------------------------

    try:

        feed = feedparser.parse(
            feed_url
        )

    except Exception as error:

        print(
            f"❌ Failed to fetch "
            f"{source.get('name', 'Unknown Source')}: "
            f"{error}"
        )

        return []


    # --------------------------------------------------------
    # تحويل الأخبار إلى صيغة موحدة
    # --------------------------------------------------------

    news = []

    for entry in feed.entries:

        news.append({

            "title": entry.get(
                "title",
                ""
            ),

            "url": entry.get(
                "link",
                ""
            ),

            "summary": entry.get(
                "summary",
                ""
            ),

            "published": entry.get(
                "published",
                ""
            ),

            "source": source.get(
                "name",
                "Unknown"
            ),

            "language": source.get(
                "language",
                ""
            ),

            "type": source.get(
                "type",
                ""
            ),

            "category": source.get(
                "category",
                ""
            ),

            "priority": source.get(
                "priority",
                999
            ),

        })


    return news


# ============================================================
# جلب الأخبار من جميع المصادر
# ============================================================

def fetch_all_sources(sources):

    all_news = []


    # --------------------------------------------------------
    # ترتيب المصادر حسب الأولوية
    # --------------------------------------------------------

    sorted_sources = sorted(
        sources,
        key=lambda source: source.get(
            "priority",
            999
        )
    )


    # --------------------------------------------------------
    # تشغيل المصادر واحدًا تلو الآخر
    # --------------------------------------------------------

    for source in sorted_sources:

        print()
        print(
            f"Fetching: "
            f"{source.get('name', 'Unknown Source')}"
        )

        news = fetch_source(
            source
        )

        print(
            f"Entries received: "
            f"{len(news)}"
        )

        all_news.extend(
            news
        )


    # --------------------------------------------------------
    # إرجاع جميع الأخبار
    # --------------------------------------------------------

    return all_news

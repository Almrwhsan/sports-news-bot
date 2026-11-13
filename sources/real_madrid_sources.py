# ============================================================
# Real Madrid News Sources
# مصادر أخبار نادي ريال مدريد فقط
# ============================================================

REAL_MADRID_SOURCES = [

    {
        "name": "AS Real Madrid",
        "language": "es",
        "type": "club",
        "category": "real_madrid",
        "priority": 1,
        "enabled": True,

        # مصدر مخصص لأخبار ريال مدريد
        "feed": (
            "https://feeds.as.com/"
            "mrss-s/list/as/site/as.com/"
            "tag/real_madrid_a/"
        ),

        # إعدادات خاصة بالمصدر
        "max_entries": 12,
    },

]

# ============================================================
# المصادر العالمية
# ============================================================

GLOBAL_SOURCES = [

    # --------------------------------------------------------
    # AS - كرة القدم
    # --------------------------------------------------------

    {
        "name": "AS Football",
        "language": "es",
        "type": "global",
        "category": "football",
        "priority": 1,
        "enabled": True,
        "feed": (
            "https://feeds.as.com/"
            "mrss-s/pages/as/site/as.com/"
            "section/futbol/portada/"
        ),
    },

    # --------------------------------------------------------
    # AS - Real Madrid
    # --------------------------------------------------------

    {
        "name": "AS Real Madrid",
        "language": "es",
        "type": "club",
        "category": "real_madrid",
        "priority": 1,
        "enabled": True,
        "feed": (
            "https://feeds.as.com/"
            "mrss-s/list/as/site/as.com/"
            "tag/real_madrid_a/"
        ),
    },

    # --------------------------------------------------------
    # AS - Barcelona
    # --------------------------------------------------------

    {
        "name": "AS Barcelona",
        "language": "es",
        "type": "club",
        "category": "barcelona",
        "priority": 1,
        "enabled": True,
        "feed": (
            "https://feeds.as.com/"
            "mrss-s/list/as/site/as.com/"
            "tag/fc_barcelona_a/"
        ),
    },

    # --------------------------------------------------------
    # AS - Atlético Madrid
    # --------------------------------------------------------

    {
        "name": "AS Atlético Madrid",
        "language": "es",
        "type": "club",
        "category": "atletico_madrid",
        "priority": 1,
        "enabled": True,
        "feed": (
            "https://feeds.as.com/"
            "mrss-s/list/as/site/as.com/"
            "tag/atletico_madrid_a/"
        ),
    },

    # --------------------------------------------------------
    # MARCA - كرة القدم
    # --------------------------------------------------------

    {
        "name": "MARCA Football",
        "language": "es",
        "type": "global",
        "category": "football",
        "priority": 1,
        "enabled": True,
        "feed": (
            "https://www.marca.com/"
            "rss/futbol.xml"
        ),
    },

    # --------------------------------------------------------
    # MARCA - Real Madrid
    # --------------------------------------------------------

    {
        "name": "MARCA Real Madrid",
        "language": "es",
        "type": "club",
        "category": "real_madrid",
        "priority": 1,
        "enabled": True,
        "feed": (
            "https://www.marca.com/"
            "rss/real-madrid.xml"
        ),
    },

]

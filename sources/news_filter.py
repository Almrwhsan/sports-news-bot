# ============================================================
# فلترة وتصنيف أخبار كرة القدم
# ============================================================


# ============================================================
# كلمات كرة القدم
# ============================================================

FOOTBALL_KEYWORDS = [

    # English
    "football",
    "soccer",
    "premier league",
    "champions league",
    "europa league",
    "conference league",
    "la liga",
    "laliga",
    "serie a",
    "bundesliga",
    "ligue 1",
    "club world cup",
    "transfer",
    "transfers",

    # Spanish
    "fútbol",
    "futbol",
    "liga",
    "champions",
    "fichajes",
    "fichaje",
    "mercado",
    "real madrid",
    "barcelona",
    "atlético",
    "atletico",

    # Arabic
    "كرة القدم",
    "كرة قدم",
    "الدوري",
    "دوري أبطال أوروبا",
    "الدوري الأوروبي",
    "الدوري الإنجليزي",
    "الدوري الإسباني",
    "الدوري الإيطالي",
    "الدوري الألماني",
    "الدوري الفرنسي",
    "كأس العالم للأندية",
    "انتقال",
    "انتقالات",
    "صفقة",
    "صفقات",
    "ريال مدريد",
    "برشلونة",
    "أتلتيكو مدريد",
    "أتليتكو مدريد",
]


# ============================================================
# كلمات الأخبار غير المرغوبة
# ============================================================

NON_NEWS_KEYWORDS = [

    "podcast",
    "video",
    "watch:",
    "quiz",
    "gallery",
    "opinion",
    "horoscope",

    "بودكاست",
    "فيديو",
    "اختبار",
    "صور",
    "رأي",
]


# ============================================================
# البحث عن الكلمات
# ============================================================

def contains_keyword(text, keywords):

    text = text.lower()

    for keyword in keywords:

        if keyword.lower() in text:

            return True

    return False


# ============================================================
# التأكد من أن الخبر متعلق بكرة القدم
# ============================================================

def is_football_news(news):

    title = news.get(
        "title",
        ""
    )

    summary = news.get(
        "summary",
        ""
    )

    text = (
        f"{title} {summary}"
    )

    return contains_keyword(
        text,
        FOOTBALL_KEYWORDS
    )


# ============================================================
# استبعاد الأخبار غير المناسبة
# ============================================================

def is_excluded_news(news):

    title = news.get(
        "title",
        ""
    )

    return contains_keyword(
        title,
        NON_NEWS_KEYWORDS
    )


# ============================================================
# تصنيف الخبر
# ============================================================

def detect_category(news):

    title = news.get(
        "title",
        ""
    ).lower()

    summary = news.get(
        "summary",
        ""
    ).lower()

    text = (
        f"{title} {summary}"
    )


    # --------------------------------------------------------
    # ريال مدريد
    # --------------------------------------------------------

    if (
        "real madrid" in text
        or "ريال مدريد" in text
    ):

        return "real_madrid"


    # --------------------------------------------------------
    # برشلونة
    # --------------------------------------------------------

    if (
        "barcelona" in text
        or "fc barcelona" in text
        or "برشلونة" in text
    ):

        return "barcelona"


    # --------------------------------------------------------
    # أتلتيكو مدريد
    # --------------------------------------------------------

    if (
        "atletico madrid" in text
        or "atlético madrid" in text
        or "أتلتيكو مدريد" in text
        or "أتليتكو مدريد" in text
    ):

        return "atletico_madrid"


    # --------------------------------------------------------
    # الانتقالات
    # --------------------------------------------------------

    transfer_keywords = [

        "transfer",
        "transfers",
        "fichaje",
        "fichajes",
        "mercado",
        "انتقال",
        "انتقالات",
        "صفقة",
        "صفقات",
        "ضم",
        "تعاقد",
    ]

    if contains_keyword(
        text,
        transfer_keywords
    ):

        return "transfers"


    # --------------------------------------------------------
    # دوري أبطال أوروبا
    # --------------------------------------------------------

    if (
        "champions league" in text
        or "دوري أبطال أوروبا" in text
    ):

        return "champions_league"


    # --------------------------------------------------------
    # الدوري الإسباني
    # --------------------------------------------------------

    if (
        "la liga" in text
        or "laliga" in text
        or "الدوري الإسباني" in text
    ):

        return "la_liga"


    # --------------------------------------------------------
    # الدوري الإنجليزي
    # --------------------------------------------------------

    if (
        "premier league" in text
        or "الدوري الإنجليزي" in text
    ):

        return "premier_league"


    # --------------------------------------------------------
    # الدوري الإيطالي
    # --------------------------------------------------------

    if (
        "serie a" in text
        or "الدوري الإيطالي" in text
    ):

        return "serie_a"


    # --------------------------------------------------------
    # الدوري الألماني
    # --------------------------------------------------------

    if (
        "bundesliga" in text
        or "الدوري الألماني" in text
    ):

        return "bundesliga"


    # --------------------------------------------------------
    # الدوري الفرنسي
    # --------------------------------------------------------

    if (
        "ligue 1" in text
        or "الدوري الفرنسي" in text
    ):

        return "ligue_1"


    # --------------------------------------------------------
    # كرة القدم العامة
    # --------------------------------------------------------

    return "football"


# ============================================================
# معالجة خبر واحد
# ============================================================

def filter_news_item(news):

    if not is_football_news(news):

        return None

    if is_excluded_news(news):

        return None

    filtered_news = dict(
        news
    )

    filtered_news["category"] = (
        detect_category(
            filtered_news
        )
    )

    return filtered_news


# ============================================================
# معالجة مجموعة أخبار
# ============================================================

def filter_news(news_list):

    filtered = []

    for news in news_list:

        result = filter_news_item(
            news
        )

        if result is not None:

            filtered.append(
                result
            )

    return filtered


# ============================================================
# Real Madrid Bot Configuration
# إعداد مصادر بوت أخبار ريال مدريد
# ============================================================

from .real_madrid_sources import REAL_MADRID_SOURCES


# المصادر المعتمدة لهذا الإصدار من البوت
ALL_SOURCES = [
    source
    for source in REAL_MADRID_SOURCES
    if source.get("enabled", True)
]


# إعدادات جلب الأخبار
MAX_NEWS_PER_SOURCE = 8


# إعدادات النشر الأولية
MAX_NEW_NEWS = 3


# الحد الأقصى للأخبار المحفوظة
MAX_NEWS = 500

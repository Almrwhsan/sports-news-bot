# ============================================================
# LIVE FORMATTER
# تنسيق أحداث المباريات المباشرة
# SportScore Football
# ============================================================

from __future__ import annotations

import re
from typing import Any, Dict, Optional


# ============================================================
# أدوات مساعدة
# ============================================================

def safe_text(value: Any, default: str = "") -> str:
    """
    تحويل القيمة إلى نص آمن.
    """
    if value is None:
        return default

    text = str(value).strip()

    if not text:
        return default

    return text


def safe_int(value: Any) -> Optional[int]:
    """
    تحويل القيمة إلى integer بدون التسبب بخطأ.
    """
    if value is None:
        return None

    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def normalize_text(value: Any) -> str:
    """
    تطبيع النص للمقارنة.
    """
    text = safe_text(value)

    text = text.lower()

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# أسماء الفرق
# ============================================================

TEAM_NAMES = {

    # --------------------------------------------------------
    # إسبانيا
    # --------------------------------------------------------

    "real madrid": "ريال مدريد",
    "real madrid cf": "ريال مدريد",
    "realmadrid": "ريال مدريد",

    "real betis": "ريال بيتيس",
    "real betis balompie": "ريال بيتيس",
    "real betis balompié": "ريال بيتيس",

    "barcelona": "برشلونة",
    "fc barcelona": "برشلونة",

    "atletico madrid": "أتلتيكو مدريد",
    "atlético madrid": "أتلتيكو مدريد",
    "atletico de madrid": "أتلتيكو مدريد",

    "sevilla": "إشبيلية",
    "sevilla fc": "إشبيلية",

    # --------------------------------------------------------
    # إنجلترا
    # --------------------------------------------------------

    "manchester city": "مانشستر سيتي",
    "manchester united": "مانشستر يونايتد",

    "liverpool": "ليفربول",
    "liverpool fc": "ليفربول",

    "arsenal": "أرسنال",
    "arsenal fc": "أرسنال",

    "chelsea": "تشيلسي",
    "chelsea fc": "تشيلسي",

    "tottenham": "توتنهام",
    "tottenham hotspur": "توتنهام",

    # --------------------------------------------------------
    # ألمانيا
    # --------------------------------------------------------

    "bayern munich": "بايرن ميونخ",
    "fc bayern munich": "بايرن ميونخ",
    "bayern münchen": "بايرن ميونخ",

    "borussia dortmund": "بوروسيا دورتموند",
    "dortmund": "بوروسيا دورتموند",

    # --------------------------------------------------------
    # إيطاليا
    # --------------------------------------------------------

    "inter": "إنتر ميلان",
    "inter milan": "إنتر ميلان",
    "internazionale": "إنتر ميلان",

    "ac milan": "ميلان",
    "milan": "ميلان",

    "juventus": "يوفنتوس",
    "juventus fc": "يوفنتوس",

    # --------------------------------------------------------
    # فرنسا
    # --------------------------------------------------------

    "paris saint-germain": "باريس سان جيرمان",
    "paris saint germain": "باريس سان جيرمان",
    "psg": "باريس سان جيرمان",
}


# ============================================================
# أسماء اللاعبين
# ============================================================

# ============================================================
# ملاحظة مهمة:
#
# لا نضع أسماء اللاعبين هنا إلا إذا كان لدينا اسم موثوق.
#
# SportScore قد يعيد الاسم بالإنجليزية أو بصيغة مختلفة.
# لذلك إذا لم يوجد اللاعب في هذه القائمة، سيتم استخدام
# الاسم القادم من المصدر كما هو بدل اختراع ترجمة.
# ============================================================

PLAYER_NAMES = {

    # --------------------------------------------------------
    # Real Madrid
    # --------------------------------------------------------

    "kylian mbappe": "كيليان مبابي",
    "kylian mbappé": "كيليان مبابي",

    "arda güler": "أردا غولر",
    "arda guler": "أردا غولر",

    "vinicius junior": "فينيسيوس جونيور",
    "vinicius jr": "فينيسيوس جونيور",
    "vinícius júnior": "فينيسيوس جونيور",

    "rodrygo": "رودريغو",

    "jude bellingham": "جود بيلينغهام",

    "federico valverde": "فيديريكو فالفيردي",

    "aurélien tchouaméni": "أوريلين تشواميني",
    "aurelien tchouameni": "أوريلين تشواميني",

    "eduardo camavinga": "إدواردو كامافينغا",

    "dani carvajal": "داني كارفاخال",

    "antonio rudiger": "أنطونيو روديغر",
    "antonio rüdiger": "أنطونيو روديغر",

    "thibaut courtois": "تيبو كورتوا",

    # --------------------------------------------------------
    # Real Betis
    # --------------------------------------------------------

    "jorge benguché": "خورخي بينغوتشي",
    "jorge benguche": "خورخي بينغوتشي",
}


# ============================================================
# ترجمة اسم الفريق
# ============================================================

def arabic_team_name(team: Any) -> str:
    """
    تحويل اسم الفريق إلى العربية إذا كان معروفًا.

    إذا لم يكن الفريق موجودًا في القائمة، نعيد الاسم الأصلي.
    """

    text = safe_text(team)

    if not text:
        return "الفريق"

    normalized = normalize_text(text)

    return TEAM_NAMES.get(normalized, text)


# ============================================================
# ترجمة اسم اللاعب
# ============================================================

def arabic_player_name(player: Any) -> str:
    """
    تحويل اسم اللاعب إلى العربية إذا كان معروفًا.

    إذا لم يكن موجودًا في القائمة:
    نستخدم الاسم الأصلي القادم من المصدر.
    """

    text = safe_text(player)

    if not text:
        return "اللاعب"

    normalized = normalize_text(text)

    return PLAYER_NAMES.get(normalized, text)


# ============================================================
# تنسيق النتيجة
# ============================================================

def format_score(
    home_score: Any,
    away_score: Any,
) -> str:

    home = safe_int(home_score)
    away = safe_int(away_score)

    if home is None:
        home = 0

    if away is None:
        away = 0

    return f"{home}️⃣-{away}️⃣"


# ============================================================
# سطر المباراة
# ============================================================

def format_match_line(event: Dict[str, Any]) -> str:

    home = arabic_team_name(
        event.get("home_team")
    )

    away = arabic_team_name(
        event.get("away_team")
    )

    score = format_score(
        event.get("home_score"),
        event.get("away_score"),
    )

    return (
        f"🇪🇸 {home} {score} {away} 🇪🇸"
    )


# ============================================================
# الدقيقة
# ============================================================

def format_minute(event: Dict[str, Any]) -> str:

    minute = safe_int(
        event.get("minute")
    )

    if minute is None:
        return ""

    return f"⏱️ الدقيقة {minute}"


# ============================================================
# اللاعب
# ============================================================

def format_player(event: Dict[str, Any]) -> str:

    player = event.get("player")

    if not player:
        return ""

    return (
        f"👤 {arabic_player_name(player)}"
    )


# ============================================================
# تنسيق الهدف
# ============================================================

def format_goal(event: Dict[str, Any]) -> str:

    minute = format_minute(event)

    player = format_player(event)

    match_line = format_match_line(event)

    lines = [
        "🚨⚽️ جــــووووول!",
        "",
        match_line,
    ]

    if player:
        lines.extend([
            "",
            player,
        ])

    if minute:
        lines.extend([
            minute,
        ])

    lines.extend([
        "",
        "🔥 ريال مدريد يتقدم!",
        "",
        "#ريال_مدريد #ريال_بيتيس #نبض_مدريد",
    ])

    return "\n".join(lines)


# ============================================================
# الهدف العكسي
# ============================================================

def format_own_goal(event: Dict[str, Any]) -> str:

    minute = format_minute(event)

    player = format_player(event)

    match_line = format_match_line(event)

    lines = [
        "🚨⚽️ جــــووووول عكسي!",
        "",
        match_line,
    ]

    if player:
        lines.extend([
            "",
            player,
        ])

    if minute:
        lines.append(minute)

    lines.extend([
        "",
        "#ريال_مدريد #ريال_بيتيس #نبض_مدريد",
    ])

    return "\n".join(lines)


# ============================================================
# البطاقة الصفراء
# ============================================================

def format_yellow_card(event: Dict[str, Any]) -> str:

    minute = format_minute(event)

    player = format_player(event)

    match_line = format_match_line(event)

    lines = [
        "🟨 بطاقة صفراء!",
        "",
        match_line,
    ]

    if player:
        lines.extend([
            "",
            player,
        ])

    if minute:
        lines.append(minute)

    lines.extend([
        "",
        "#ريال_مدريد #ريال_بيتيس #نبض_مدريد",
    ])

    return "\n".join(lines)


# ============================================================
# البطاقة الحمراء
# ============================================================

def format_red_card(event: Dict[str, Any]) -> str:

    minute = format_minute(event)

    player = format_player(event)

    match_line = format_match_line(event)

    lines = [
        "🟥 بطاقة حمراء!",
        "",
        match_line,
    ]

    if player:
        lines.extend([
            "",
            player,
        ])

    if minute:
        lines.append(minute)

    lines.extend([
        "",
        "#ريال_مدريد #ريال_بيتيس #نبض_مدريد",
    ])

    return "\n".join(lines)


# ============================================================
# ركلة الجزاء
# ============================================================

def format_penalty(event: Dict[str, Any]) -> str:

    minute = format_minute(event)

    player = format_player(event)

    match_line = format_match_line(event)

    lines = [
        "⚽️ ركلة جزاء!",
        "",
        match_line,
    ]

    if player:
        lines.extend([
            "",
            player,
        ])

    if minute:
        lines.append(minute)

    lines.extend([
        "",
        "#ريال_مدريد #ريال_بيتيس #نبض_مدريد",
    ])

    return "\n".join(lines)


# ============================================================
# الهدف الملغى
# ============================================================

def format_goal_cancelled(event: Dict[str, Any]) -> str:

    minute = format_minute(event)

    player = format_player(event)

    match_line = format_match_line(event)

    lines = [
        "🚫⚽️ هدف ملغى!",
        "",
        match_line,
    ]

    if player:
        lines.extend([
            "",
            player,
        ])

    if minute:
        lines.append(minute)

    lines.extend([
        "",
        "#ريال_مدريد #ريال_بيتيس #نبض_مدريد",
    ])

    return "\n".join(lines)


# ============================================================
# التبديل
# ============================================================

def format_substitution(event: Dict[str, Any]) -> str:

    minute = format_minute(event)

    match_line = format_match_line(event)

    player = safe_text(
        event.get("player")
    )

    player_in = safe_text(
        event.get("player_in")
    )

    player_out = safe_text(
        event.get("player_out")
    )

    lines = [
        "🔄 تبديل",
        "",
        match_line,
    ]

    if minute:
        lines.extend([
            "",
            minute,
        ])

    # --------------------------------------------------------
    # إذا كانت بيانات الدخول والخروج متوفرة
    # --------------------------------------------------------

    if player_out:
        lines.extend([
            "",
            f"⬅️ خروج: {arabic_player_name(player_out)}",
        ])

    if player_in:
        lines.append(
            f"➡️ دخول: {arabic_player_name(player_in)}"
        )

    # --------------------------------------------------------
    # fallback
    #
    # إذا كان المصدر يعيد لاعبًا واحدًا فقط
    # --------------------------------------------------------

    if (
        not player_out
        and not player_in
        and player
    ):
        lines.extend([
            "",
            f"👤 {arabic_player_name(player)}",
        ])

    lines.extend([
        "",
        "#ريال_مدريد #ريال_بيتيس #نبض_مدريد",
    ])

    return "\n".join(lines)


# ============================================================
# حدث غير معروف
# ============================================================

def format_unknown(event: Dict[str, Any]) -> str:

    minute = format_minute(event)

    match_line = format_match_line(event)

    event_type = safe_text(
        event.get("type"),
        "حدث جديد",
    )

    lines = [
        f"📢 {event_type}",
        "",
        match_line,
    ]

    if minute:
        lines.extend([
            "",
            minute,
        ])

    lines.extend([
        "",
        "#ريال_مدريد #ريال_بيتيس #نبض_مدريد",
    ])

    return "\n".join(lines)


# ============================================================
# الدالة الرئيسية
# ============================================================

def format_live_event(event: Dict[str, Any]) -> str:
    """
    تنسيق الحدث حسب نوعه.

    هذه هي الدالة الوحيدة التي يحتاجها live_bot.py.
    """

    if not isinstance(event, dict):
        return ""

    event_type = safe_text(
        event.get("event_type")
    )

    if event_type == "goal":
        return format_goal(event)

    if event_type == "own_goal":
        return format_own_goal(event)

    if event_type == "yellow_card":
        return format_yellow_card(event)

    if event_type == "red_card":
        return format_red_card(event)

    if event_type == "penalty":
        return format_penalty(event)

    if event_type == "goal_cancelled":
        return format_goal_cancelled(event)

    if event_type == "substitution":
        return format_substitution(event)

    return format_unknown(event)


# ============================================================
# SELF TEST
# ============================================================

def self_test():

    print("=" * 70)
    print("LIVE FORMATTER — SELF TEST")
    print("=" * 70)

    # --------------------------------------------------------
    # Goal
    # --------------------------------------------------------

    goal_event = {
        "event_type": "goal",
        "minute": 20,
        "player": "Kylian Mbappe",
        "home_score": 0,
        "away_score": 1,
        "home_team": "Real Betis",
        "away_team": "Real Madrid",
    }

    goal_message = format_live_event(
        goal_event
    )

    print()
    print("TEST 1 — GOAL")
    print("-" * 70)
    print(goal_message)

    assert "جــــووووول" in goal_message
    assert "ريال بيتيس" in goal_message
    assert "ريال مدريد" in goal_message
    assert "كيليان مبابي" in goal_message
    assert "الدقيقة 20" in goal_message

    # --------------------------------------------------------
    # Yellow card
    # --------------------------------------------------------

    yellow_event = {
        "event_type": "yellow_card",
        "minute": 48,
        "player": "Arda Güler",
        "home_score": 0,
        "away_score": 0,
        "home_team": "Real Betis",
        "away_team": "Real Madrid",
    }

    yellow_message = format_live_event(
        yellow_event
    )

    print()
    print("TEST 2 — YELLOW CARD")
    print("-" * 70)
    print(yellow_message)

    assert "🟨 بطاقة صفراء!" in yellow_message
    assert "أردا غولر" in yellow_message
    assert "الدقيقة 48" in yellow_message

    # --------------------------------------------------------
    # Red card
    # --------------------------------------------------------

    red_event = {
        "event_type": "red_card",
        "minute": 74,
        "player": "Arda Güler",
        "home_score": 0,
        "away_score": 1,
        "home_team": "Real Betis",
        "away_team": "Real Madrid",
    }

    red_message = format_live_event(
        red_event
    )

    print()
    print("TEST 3 — RED CARD")
    print("-" * 70)
    print(red_message)

    assert "🟥 بطاقة حمراء!" in red_message

    # --------------------------------------------------------
    # Substitution
    # --------------------------------------------------------

    substitution_event = {
        "event_type": "substitution",
        "minute": 67,
        "player_in": "Rodrygo",
        "player_out": "Vinicius Junior",
        "home_score": 0,
        "away_score": 1,
        "home_team": "Real Betis",
        "away_team": "Real Madrid",
    }

    substitution_message = format_live_event(
        substitution_event
    )

    print()
    print("TEST 4 — SUBSTITUTION")
    print("-" * 70)
    print(substitution_message)

    assert "🔄 تبديل" in substitution_message
    assert "خروج" in substitution_message
    assert "دخول" in substitution_message

    # --------------------------------------------------------
    # Unknown
    # --------------------------------------------------------

    unknown_event = {
        "event_type": "unknown",
        "type": "VAR",
        "minute": 55,
        "home_score": 0,
        "away_score": 1,
        "home_team": "Real Betis",
        "away_team": "Real Madrid",
    }

    unknown_message = format_live_event(
        unknown_event
    )

    print()
    print("TEST 5 — UNKNOWN EVENT")
    print("-" * 70)
    print(unknown_message)

    assert unknown_message

    print()
    print("=" * 70)
    print("✅ LIVE FORMATTER SELF TEST PASSED")
    print("=" * 70)


# ============================================================
# تشغيل الاختبار
# ============================================================

if __name__ == "__main__":
    self_test()

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

    "athletic bilbao": "أتلتيك بلباو",
    "athletic club": "أتلتيك بلباو",

    "villarreal": "فياريال",
    "villarreal cf": "فياريال",

    "valencia": "فالنسيا",
    "valencia cf": "فالنسيا",

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

    "newcastle united": "نيوكاسل يونايتد",
    "newcastle": "نيوكاسل يونايتد",

    "aston villa": "أستون فيلا",
    "west ham": "وست هام",

    "crystal palace": "كريستال بالاس",

    # --------------------------------------------------------
    # ألمانيا
    # --------------------------------------------------------

    "bayern munich": "بايرن ميونخ",
    "fc bayern munich": "بايرن ميونخ",
    "bayern münchen": "بايرن ميونخ",

    "borussia dortmund": "بوروسيا دورتموند",
    "dortmund": "بوروسيا دورتموند",

    "rb leipzig": "لايبزيغ",
    "bayer leverkusen": "باير ليفركوزن",

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

    "napoli": "نابولي",
    "as roma": "روما",
    "roma": "روما",

    # --------------------------------------------------------
    # فرنسا
    # --------------------------------------------------------

    "paris saint-germain": "باريس سان جيرمان",
    "paris saint germain": "باريس سان جيرمان",
    "psg": "باريس سان جيرمان",

    "olympique lyonnais": "ليون",
    "lyon": "ليون",

    "marseille": "مارسيليا",
    "olympique de marseille": "مارسيليا",

    # --------------------------------------------------------
    # هولندا
    # --------------------------------------------------------

    "ajax": "أياكس",
    "psv": "آيندهوفن",
    "psv eindhoven": "آيندهوفن",

    # --------------------------------------------------------
    # البرتغال
    # --------------------------------------------------------

    "benfica": "بنفيكا",
    "fc porto": "بورتو",
    "porto": "بورتو",
    "sporting cp": "سبورتينغ لشبونة",
    "sporting lisbon": "سبورتينغ لشبونة",
}


# ============================================================
# أسماء اللاعبين
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

    إذا لم يكن الفريق موجودًا في القائمة،
    نعيد الاسم الأصلي القادم من المصدر.
    """

    text = safe_text(team)

    if not text:
        return "الفريق"

    normalized = normalize_text(text)

    return TEAM_NAMES.get(
        normalized,
        text,
    )


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

    return PLAYER_NAMES.get(
        normalized,
        text,
    )


# ============================================================
# الحصول على اسم الفريق صاحب الحدث
# ============================================================

def get_event_team(
    event: Dict[str, Any],
) -> str:

    side = normalize_text(
        event.get("side")
    )

    if side in (
        "home",
        "1",
        "left",
    ):
        return arabic_team_name(
            event.get("home_team")
        )

    if side in (
        "away",
        "2",
        "right",
    ):
        return arabic_team_name(
            event.get("away_team")
        )

    return ""


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

def format_match_line(
    event: Dict[str, Any],
) -> str:

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
        f"⚽️ {home} {score} {away}"
    )


# ============================================================
# الدقيقة
# ============================================================

def format_minute(
    event: Dict[str, Any],
) -> str:

    minute = safe_int(
        event.get("minute")
    )

    if minute is None:
        minute = safe_int(
            event.get("time")
        )

    if minute is None:
        return ""

    return f"⏱️ الدقيقة {minute}"


# ============================================================
# اللاعب
# ============================================================

def format_player(
    event: Dict[str, Any],
) -> str:

    player = event.get("player")

    if not player:
        return ""

    return (
        f"👤 {arabic_player_name(player)}"
    )


# ============================================================
# الهاشتاقات
# ============================================================

def format_hashtags(
    event: Dict[str, Any],
) -> str:

    home = arabic_team_name(
        event.get("home_team")
    )

    away = arabic_team_name(
        event.get("away_team")
    )

    hashtags = [
        "#نبض_مدريد",
    ]

    if home and home != "الفريق":
        hashtags.append(
            "#" + home.replace(" ", "_")
        )

    if away and away != "الفريق":
        hashtags.append(
            "#" + away.replace(" ", "_")
        )

    return " ".join(
        dict.fromkeys(hashtags)
    )


# ============================================================
# هل الفريق صاحب الحدث هو ريال مدريد؟
# ============================================================

def is_real_madrid_event(
    event: Dict[str, Any],
) -> bool:

    team = normalize_text(
        get_event_team(event)
    )

    return team in (
        "ريال مدريد",
        "real madrid",
        "real madrid cf",
    )


# ============================================================
# وصف التقدم
# ============================================================

def get_lead_message(
    event: Dict[str, Any],
) -> str:

    home = arabic_team_name(
        event.get("home_team")
    )

    away = arabic_team_name(
        event.get("away_team")
    )

    home_score = safe_int(
        event.get("home_score")
    )

    away_score = safe_int(
        event.get("away_score")
    )

    if home_score is None or away_score is None:
        return ""

    if home_score > away_score:
        return f"🔥 {home} يتقدم!"

    if away_score > home_score:
        return f"🔥 {away} يتقدم!"

    return "⚖️ المباراة تعود إلى التعادل!"


# ============================================================
# تنسيق الهدف
# ============================================================

def format_goal(
    event: Dict[str, Any],
) -> str:

    minute = format_minute(event)

    player = format_player(event)

    match_line = format_match_line(event)

    lead_message = get_lead_message(
        event
    )

    hashtags = format_hashtags(
        event
    )

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
        lines.append(
            minute
        )

    if lead_message:
        lines.extend([
            "",
            lead_message,
        ])

    lines.extend([
        "",
        hashtags,
    ])

    return "\n".join(lines)


# ============================================================
# الهدف العكسي
# ============================================================

def format_own_goal(
    event: Dict[str, Any],
) -> str:

    minute = format_minute(event)

    player = format_player(event)

    match_line = format_match_line(event)

    hashtags = format_hashtags(
        event
    )

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
        lines.append(
            minute
        )

    lines.extend([
        "",
        "⚠️ هدف عن طريق الخطأ في مرماه.",
        "",
        hashtags,
    ])

    return "\n".join(lines)


# ============================================================
# البطاقة الصفراء
# ============================================================

def format_yellow_card(
    event: Dict[str, Any],
) -> str:

    minute = format_minute(event)

    player = format_player(event)

    match_line = format_match_line(event)

    hashtags = format_hashtags(
        event
    )

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
        lines.append(
            minute
        )

    lines.extend([
        "",
        hashtags,
    ])

    return "\n".join(lines)


# ============================================================
# البطاقة الحمراء
# ============================================================

def format_red_card(
    event: Dict[str, Any],
) -> str:

    minute = format_minute(event)

    player = format_player(event)

    match_line = format_match_line(event)

    hashtags = format_hashtags(
        event
    )

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
        lines.append(
            minute
        )

    lines.extend([
        "",
        "⛔️ الفريق سيكمل المباراة بعشرة لاعبين.",
        "",
        hashtags,
    ])

    return "\n".join(lines)


# ============================================================
# ركلة الجزاء
# ============================================================

def format_penalty(
    event: Dict[str, Any],
) -> str:

    minute = format_minute(event)

    player = format_player(event)

    match_line = format_match_line(event)

    hashtags = format_hashtags(
        event
    )

    lines = [
        "⚽️🚨 ركلة جزاء!",
        "",
        match_line,
    ]

    if player:
        lines.extend([
            "",
            player,
        ])

    if minute:
        lines.append(
            minute
        )

    lines.extend([
        "",
        "🔥 فرصة خطيرة أمام المرمى!",
        "",
        hashtags,
    ])

    return "\n".join(lines)


# ============================================================
# ركلة الجزاء الضائعة
# ============================================================

def format_penalty_missed(
    event: Dict[str, Any],
) -> str:

    minute = format_minute(event)

    player = format_player(event)

    match_line = format_match_line(event)

    hashtags = format_hashtags(
        event
    )

    lines = [
        "❌⚽️ ركلة جزاء ضائعة!",
        "",
        match_line,
    ]

    if player:
        lines.extend([
            "",
            player,
        ])

    if minute:
        lines.append(
            minute
        )

    lines.extend([
        "",
        "😱 فرصة ذهبية تضيع!",
        "",
        hashtags,
    ])

    return "\n".join(lines)


# ============================================================
# الهدف الملغى
# ============================================================

def format_goal_cancelled(
    event: Dict[str, Any],
) -> str:

    minute = format_minute(event)

    player = format_player(event)

    match_line = format_match_line(event)

    hashtags = format_hashtags(
        event
    )

    lines = [
        "🚫⚽️ هــــدف ملغى!",
        "",
        match_line,
    ]

    if player:
        lines.extend([
            "",
            player,
        ])

    if minute:
        lines.append(
            minute
        )

    lines.extend([
        "",
        "📺 تم إلغاء الهدف بعد مراجعة الحالة.",
        "",
        hashtags,
    ])

    return "\n".join(lines)


# ============================================================
# VAR
# ============================================================

def format_var(
    event: Dict[str, Any],
) -> str:

    minute = format_minute(event)

    player = format_player(event)

    match_line = format_match_line(event)

    hashtags = format_hashtags(
        event
    )

    lines = [
        "📺 VAR",
        "",
        match_line,
    ]

    if player:
        lines.extend([
            "",
            player,
        ])

    if minute:
        lines.append(
            minute
        )

    lines.extend([
        "",
        "🔎 مراجعة من حكم الفيديو المساعد.",
        "",
        hashtags,
    ])

    return "\n".join(lines)


# ============================================================
# التبديل
# ============================================================

def format_substitution(
    event: Dict[str, Any],
) -> str:

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

    hashtags = format_hashtags(
        event
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

    if player_out:
        lines.append(
            f"⬅️ خروج: {arabic_player_name(player_out)}"
        )

    if player_in:
        lines.append(
            f"➡️ دخول: {arabic_player_name(player_in)}"
        )

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
        hashtags,
    ])

    return "\n".join(lines)


# ============================================================
# حدث غير معروف
# ============================================================

def format_unknown(
    event: Dict[str, Any],
) -> str:

    minute = format_minute(event)

    match_line = format_match_line(event)

    event_type = safe_text(
        event.get("type"),
        "حدث جديد",
    )

    hashtags = format_hashtags(
        event
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
        hashtags,
    ])

    return "\n".join(lines)


# ============================================================
# الدالة الرئيسية
# ============================================================

def format_live_event(
    event: Dict[str, Any],
) -> str:
    """
    تنسيق الحدث حسب نوعه.

    هذه هي الدالة التي يستخدمها live_bot.py.
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

    if event_type == "penalty_missed":
        return format_penalty_missed(event)

    if event_type == "goal_cancelled":
        return format_goal_cancelled(event)

    if event_type == "var":
        return format_var(event)

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
        "side": "away",
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
    assert "يتقدم" in goal_message

    print("PASS: Goal formatter.")

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
        "side": "away",
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

    print("PASS: Yellow card formatter.")

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
        "side": "away",
    }

    red_message = format_live_event(
        red_event
    )

    print()
    print("TEST 3 — RED CARD")
    print("-" * 70)
    print(red_message)

    assert "🟥 بطاقة حمراء!" in red_message

    print("PASS: Red card formatter.")

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
        "side": "away",
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
    assert "رودريغو" in substitution_message
    assert "فينيسيوس جونيور" in substitution_message

    print("PASS: Substitution formatter.")

    # --------------------------------------------------------
    # Penalty missed
    # --------------------------------------------------------

    penalty_missed_event = {
        "event_type": "penalty_missed",
        "minute": 94,
        "player": "Kylian Mbappe",
        "home_score": 1,
        "away_score": 0,
        "home_team": "Real Betis",
        "away_team": "Real Madrid",
        "side": "away",
    }

    penalty_missed_message = format_live_event(
        penalty_missed_event
    )

    print()
    print("TEST 5 — PENALTY MISSED")
    print("-" * 70)
    print(penalty_missed_message)

    assert "ركلة جزاء ضائعة" in penalty_missed_message
    assert "كيليان مبابي" in penalty_missed_message
    assert "الدقيقة 94" in penalty_missed_message

    print("PASS: Penalty missed formatter.")

    # --------------------------------------------------------
    # VAR
    # --------------------------------------------------------

    var_event = {
        "event_type": "var",
        "minute": 89,
        "player": "Carlos Espí",
        "home_score": 1,
        "away_score": 0,
        "home_team": "Real Betis",
        "away_team": "Real Madrid",
        "side": "away",
    }

    var_message = format_live_event(
        var_event
    )

    print()
    print("TEST 6 — VAR")
    print("-" * 70)
    print(var_message)

    assert "VAR" in var_message
    assert "مراجعة" in var_message
    assert "Carlos Espí" in var_message
    assert "الدقيقة 89" in var_message

    print("PASS: VAR formatter.")

    # --------------------------------------------------------
    # Goal cancelled
    # --------------------------------------------------------

    cancelled_event = {
        "event_type": "goal_cancelled",
        "minute": 50,
        "player": "Kylian Mbappe",
        "home_score": 0,
        "away_score": 0,
        "home_team": "Real Betis",
        "away_team": "Real Madrid",
        "side": "away",
    }

    cancelled_message = format_live_event(
        cancelled_event
    )

    print()
    print("TEST 7 — GOAL CANCELLED")
    print("-" * 70)
    print(cancelled_message)

    # كلمة "هدف" تحتوي على أحرف تطويل في التنسيق:
    # هــــدف
    # لذلك نتحقق من "ملغى" بدل المطابقة الحرفية لعبارة "هدف ملغى".
    assert "ملغى" in cancelled_message
    assert "مراجعة" in cancelled_message

    print("PASS: Goal cancelled formatter.")

    # --------------------------------------------------------
    # Own goal
    # --------------------------------------------------------

    own_goal_event = {
        "event_type": "own_goal",
        "minute": 55,
        "player": "Test Player",
        "home_score": 1,
        "away_score": 0,
        "home_team": "Real Betis",
        "away_team": "Real Madrid",
        "side": "home",
    }

    own_goal_message = format_live_event(
        own_goal_event
    )

    print()
    print("TEST 8 — OWN GOAL")
    print("-" * 70)
    print(own_goal_message)

    assert "جــــووووول عكسي" in own_goal_message

    print("PASS: Own goal formatter.")

    # --------------------------------------------------------
    # Unknown event
    # --------------------------------------------------------

    unknown_event = {
        "event_type": "unknown",
        "type": "Corner",
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
    print("TEST 9 — UNKNOWN EVENT")
    print("-" * 70)
    print(unknown_message)

    assert unknown_message

    print("PASS: Unknown event formatter.")

    # --------------------------------------------------------
    # Generic teams test
    # --------------------------------------------------------

    generic_event = {
        "event_type": "goal",
        "minute": 12,
        "player": "Test Player",
        "home_score": 1,
        "away_score": 0,
        "home_team": "Barcelona",
        "away_team": "Manchester City",
        "side": "home",
    }

    generic_message = format_live_event(
        generic_event
    )

    print()
    print("TEST 10 — GENERIC TEAMS")
    print("-" * 70)
    print(generic_message)

    assert "برشلونة" in generic_message
    assert "مانشستر سيتي" in generic_message
    assert "يتقدم" in generic_message

    print("PASS: Generic teams formatter.")

    # --------------------------------------------------------
    # Final
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("ALL LIVE FORMATTER SELF TESTS PASSED")
    print("=" * 70)


# ============================================================
# التشغيل
# ============================================================

if __name__ == "__main__":
    self_test()

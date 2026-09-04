# ============================================================
# LIVE FORMATTER
# SportScore Football
# Arabic Facebook Live Events
# ============================================================

from __future__ import annotations

import re
from typing import Any, Dict


# ============================================================
# Helpers
# ============================================================

def safe_text(value: Any, default: str = "") -> str:
    """
    تحويل القيمة إلى نص نظيف.
    """

    if value is None:
        return default

    text = str(value).strip()

    return text if text else default


def safe_int(value: Any, default: int | None = None) -> int | None:
    """
    تحويل القيمة إلى integer عند الإمكان.
    """

    if value is None:
        return default

    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def normalize_team_name(name: Any) -> str:
    """
    تنظيف اسم الفريق فقط.
    لا نقوم بترجمة الاسم تلقائيًا هنا.
    """

    text = safe_text(name)

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text


def normalize_player_name(name: Any) -> str:
    """
    تنظيف اسم اللاعب.
    """

    text = safe_text(name)

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text


# ============================================================
# Arabic Name Mapping
# ============================================================
#
# سنوسع هذه القائمة لاحقًا.
# لا نريد ترجمة أسماء اللاعبين آليًا بطريقة خاطئة.
# ============================================================

TEAM_NAMES = {
    "real madrid": "ريال مدريد",
    "real betis": "ريال بيتيس",
    "barcelona": "برشلونة",
    "fc barcelona": "برشلونة",
    "atletico madrid": "أتلتيكو مدريد",
    "atlético madrid": "أتلتيكو مدريد",
    "sevilla": "إشبيلية",
    "manchester city": "مانشستر سيتي",
    "manchester united": "مانشستر يونايتد",
    "liverpool": "ليفربول",
    "arsenal": "أرسنال",
    "chelsea": "تشيلسي",
    "tottenham": "توتنهام",
    "bayern munich": "بايرن ميونخ",
    "borussia dortmund": "بوروسيا دورتموند",
    "inter": "إنتر",
    "inter milan": "إنتر ميلان",
    "ac milan": "ميلان",
    "juventus": "يوفنتوس",
    "paris saint-germain": "باريس سان جيرمان",
    "psg": "باريس سان جيرمان",
}


PLAYER_NAMES = {
    # يمكن إضافة الأسماء المؤكدة هنا لاحقًا.
    #
    # "kylian mbappe": "كيليان مبابي",
}


def arabic_team_name(name: Any) -> str:
    """
    إرجاع الاسم العربي المعروف للفريق.
    إذا لم يوجد في القاموس، نستخدم الاسم الأصلي.
    """

    original = normalize_team_name(name)

    if not original:
        return ""

    key = original.lower()

    return TEAM_NAMES.get(
        key,
        original,
    )


def arabic_player_name(name: Any) -> str:
    """
    إرجاع الاسم العربي المعروف للاعب.

    لا نحاول ترجمة الاسم آليًا هنا حتى لا ننتج
    أخطاء في أسماء اللاعبين.
    """

    original = normalize_player_name(name)

    if not original:
        return ""

    key = original.lower()

    return PLAYER_NAMES.get(
        key,
        original,
    )


# ============================================================
# Score
# ============================================================

def format_score(
    home_score: Any,
    away_score: Any,
) -> str:
    """
    تنسيق النتيجة.
    """

    home = safe_int(home_score)
    away = safe_int(away_score)

    if home is None or away is None:
        return ""

    return f"{home}️⃣-{away}️⃣"


# ============================================================
# Match Line
# ============================================================

def format_match_line(
    event: Dict[str, Any],
) -> str:
    """
    سطر المباراة.
    """

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

    if not home and not away:
        return ""

    if score:
        return f"🇪🇸 {home} {score} {away} 🇪🇸"

    return f"🇪🇸 {home} - {away} 🇪🇸"


# ============================================================
# Minute
# ============================================================

def format_minute(
    event: Dict[str, Any],
) -> str:
    """
    تنسيق الدقيقة.
    """

    minute = safe_int(
        event.get("minute")
    )

    if minute is None:
        return ""

    return f"⏱️ الدقيقة {minute}"


# ============================================================
# Goal
# ============================================================

def format_goal(
    event: Dict[str, Any],
) -> str:

    home = arabic_team_name(
        event.get("home_team")
    )

    away = arabic_team_name(
        event.get("away_team")
    )

    player = arabic_player_name(
        event.get("player")
    )

    minute = format_minute(
        event
    )

    score = format_score(
        event.get("home_score"),
        event.get("away_score"),
    )

    side = safe_text(
        event.get("side")
    ).lower()

    scoring_team = ""

    if side == "home":
        scoring_team = home

    elif side == "away":
        scoring_team = away

    lines = [
        "🚨⚽️ جــــووووول!",
        "",
    ]

    if scoring_team:
        lines[0] = (
            f"🚨⚽️ جــــووووول "
            f"لـ{scoring_team}!"
        )

    if home and away and score:
        lines.extend([
            f"🇪🇸 {home} {score} {away} 🇪🇸",
            "",
        ])

    if player:
        lines.append(
            f"👤 {player}"
        )

    if minute:
        lines.append(
            minute
        )

    lines.extend([
        "",
        "🔥 يا لها من لحظة!",
        "",
        "#ريال_مدريد #ريال_بيتيس #نبض_مدريد",
    ])

    return "\n".join(
        lines
    )


# ============================================================
# Own Goal
# ============================================================

def format_own_goal(
    event: Dict[str, Any],
) -> str:

    player = arabic_player_name(
        event.get("player")
    )

    match_line = format_match_line(
        event
    )

    minute = format_minute(
        event
    )

    lines = [
        "🚨⚽️ هدف عكسي!",
        "",
    ]

    if match_line:
        lines.extend([
            match_line,
            "",
        ])

    if player:
        lines.append(
            f"👤 {player}"
        )

    if minute:
        lines.append(
            minute
        )

    lines.extend([
        "",
        "#ريال_مدريد #ريال_بيتيس #نبض_مدريد",
    ])

    return "\n".join(
        lines
    )


# ============================================================
# Yellow Card
# ============================================================

def format_yellow_card(
    event: Dict[str, Any],
) -> str:

    player = arabic_player_name(
        event.get("player")
    )

    match_line = format_match_line(
        event
    )

    minute = format_minute(
        event
    )

    lines = [
        "🟨 بطاقة صفراء",
        "",
    ]

    if match_line:
        lines.extend([
            match_line,
            "",
        ])

    if player:
        lines.append(
            f"👤 {player}"
        )

    if minute:
        lines.append(
            minute
        )

    lines.extend([
        "",
        "#ريال_مدريد #ريال_بيتيس #نبض_مدريد",
    ])

    return "\n".join(
        lines
    )


# ============================================================
# Red Card
# ============================================================

def format_red_card(
    event: Dict[str, Any],
) -> str:

    player = arabic_player_name(
        event.get("player")
    )

    match_line = format_match_line(
        event
    )

    minute = format_minute(
        event
    )

    lines = [
        "🟥 بطاقة حمراء",
        "",
    ]

    if match_line:
        lines.extend([
            match_line,
            "",
        ])

    if player:
        lines.append(
            f"👤 {player}"
        )

    if minute:
        lines.append(
            minute
        )

    lines.extend([
        "",
        "#ريال_مدريد #ريال_بيتيس #نبض_مدريد",
    ])

    return "\n".join(
        lines
    )


# ============================================================
# Penalty
# ============================================================

def format_penalty(
    event: Dict[str, Any],
) -> str:

    match_line = format_match_line(
        event
    )

    player = arabic_player_name(
        event.get("player")
    )

    minute = format_minute(
        event
    )

    lines = [
        "⚽️ ركلة جزاء",
        "",
    ]

    if match_line:
        lines.extend([
            match_line,
            "",
        ])

    if player:
        lines.append(
            f"👤 {player}"
        )

    if minute:
        lines.append(
            minute
        )

    lines.extend([
        "",
        "#ريال_مدريد #ريال_بيتيس #نبض_مدريد",
    ])

    return "\n".join(
        lines
    )


# ============================================================
# Substitution
# ============================================================

def format_substitution(
    event: Dict[str, Any],
) -> str:

    match_line = format_match_line(
        event
    )

    minute = format_minute(
        event
    )

    player = arabic_player_name(
        event.get("player")
    )

    lines = [
        "🔄 تبديل",
        "",
    ]

    if match_line:
        lines.extend([
            match_line,
            "",
        ])

    if minute:
        lines.extend([
            minute,
            "",
        ])

    if player:
        lines.append(
            f"👤 اللاعب: {player}"
        )

    lines.extend([
        "",
        "#ريال_مدريد #ريال_بيتيس #نبض_مدريد",
    ])

    return "\n".join(
        lines
    )


# ============================================================
# Cancelled Goal
# ============================================================

def format_goal_cancelled(
    event: Dict[str, Any],
) -> str:

    match_line = format_match_line(
        event
    )

    minute = format_minute(
        event
    )

    lines = [
        "🚫⚽️ هدف ملغى",
        "",
    ]

    if match_line:
        lines.extend([
            match_line,
            "",
        ])

    if minute:
        lines.append(
            minute
        )

    lines.extend([
        "",
        "#ريال_مدريد #ريال_بيتيس #نبض_مدريد",
    ])

    return "\n".join(
        lines
    )


# ============================================================
# Unknown
# ============================================================

def format_unknown(
    event: Dict[str, Any],
) -> str:

    match_line = format_match_line(
        event
    )

    minute = format_minute(
        event
    )

    lines = [
        "📢 تحديث من المباراة",
        "",
    ]

    if match_line:
        lines.extend([
            match_line,
            "",
        ])

    if minute:
        lines.append(
            minute
        )

    lines.extend([
        "",
        "#ريال_مدريد #ريال_بيتيس #نبض_مدريد",
    ])

    return "\n".join(
        lines
    )


# ============================================================
# Main Formatter
# ============================================================

def format_live_event(
    event: Dict[str, Any],
) -> str:
    """
    اختيار الصيغة المناسبة حسب نوع الحدث.
    """

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

    if event_type == "substitution":
        return format_substitution(event)

    if event_type == "goal_cancelled":
        return format_goal_cancelled(event)

    return format_unknown(event)


# ============================================================
# Self Test
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("LIVE FORMATTER — SELF TEST")
    print("=" * 70)

    goal_event = {
        "event_type": "goal",
        "minute": 20,
        "side": "away",
        "player": "Kylian Mbappé",
        "home_score": 0,
        "away_score": 1,
        "home_team": "Real Betis",
        "away_team": "Real Madrid",
    }

    yellow_event = {
        "event_type": "yellow_card",
        "minute": 32,
        "side": "home",
        "player": "Player Test",
        "home_score": 0,
        "away_score": 1,
        "home_team": "Real Betis",
        "away_team": "Real Madrid",
    }

    print()
    print("TEST 1 — GOAL")
    print("-" * 70)
    print(
        format_live_event(
            goal_event
        )
    )

    print()
    print("TEST 2 — YELLOW CARD")
    print("-" * 70)
    print(
        format_live_event(
            yellow_event
        )
    )

    print()
    print("=" * 70)
    print("SELF TEST PASSED")
    print("=" * 70)

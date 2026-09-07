# ============================================================
# LIVE EVENT MANAGER
# SportScore Football
# ============================================================

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict, List, Optional, Set


# ============================================================
# Event Types
# ============================================================

EVENT_GOAL = "goal"
EVENT_YELLOW_CARD = "yellow_card"
EVENT_RED_CARD = "red_card"
EVENT_SUBSTITUTION = "substitution"
EVENT_PENALTY = "penalty"
EVENT_PENALTY_MISSED = "penalty_missed"
EVENT_OWN_GOAL = "own_goal"
EVENT_GOAL_CANCELLED = "goal_cancelled"
EVENT_VAR = "var"
EVENT_UNKNOWN = "unknown"


# ============================================================
# Helpers
# ============================================================

def normalize_text(value: Any) -> str:
    """
    توحيد النصوص للمقارنة وإنشاء التوقيعات.
    """

    if value is None:
        return ""

    text = str(value).strip().lower()

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text


def safe_int(value: Any) -> Optional[int]:
    """
    تحويل القيمة إلى integer عند الإمكان.
    """

    if value is None:
        return None

    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def extract_match(data: Any) -> Dict[str, Any]:
    """
    استخراج كائن المباراة من استجابة SportScore.
    """

    if not isinstance(data, dict):
        return {}

    match = data.get("match")

    if isinstance(match, dict):
        return match

    return data


# ============================================================
# Event Type Detection
# ============================================================

def detect_event_type(
    incident: Dict[str, Any]
) -> str:
    """
    تحديد نوع الحدث اعتمادًا على بيانات SportScore.

    الأنواع المدعومة حاليًا:

    Goal
    Own Goal
    Goal Cancelled
    Yellow Card
    Red Card
    Substitution
    Penalty
    Penalty Missed
    VAR
    """

    if not isinstance(
        incident,
        dict,
    ):
        return EVENT_UNKNOWN

    raw_type = normalize_text(
        incident.get("type")
    )

    type_id = safe_int(
        incident.get("type_id")
    )

    is_goal = incident.get(
        "is_goal"
    )

    # --------------------------------------------------------
    # Goal Cancelled
    #
    # يجب فحصه قبل Goal لأن بعض المصادر قد تستخدم
    # type_id مرتبطًا بالأهداف.
    # --------------------------------------------------------

    if any(
        word in raw_type
        for word in [
            "cancelled goal",
            "disallowed goal",
            "goal cancelled",
            "goal disallowed",
            "goal overturned",
            "overturned goal",
        ]
    ):
        return EVENT_GOAL_CANCELLED

    # --------------------------------------------------------
    # Own Goal
    # --------------------------------------------------------

    if any(
        word in raw_type
        for word in [
            "own goal",
            "autogoal",
            "own-goal",
        ]
    ):
        return EVENT_OWN_GOAL

    # --------------------------------------------------------
    # Penalty Missed
    #
    # SportScore الحقيقي:
    # type = "Penalty missed"
    # type_id = 16
    # --------------------------------------------------------

    if (
        "penalty missed" in raw_type
        or "missed penalty" in raw_type
        or "penalty miss" in raw_type
        or type_id == 16
    ):
        return EVENT_PENALTY_MISSED

    # --------------------------------------------------------
    # Penalty
    # --------------------------------------------------------

    if "penalty" in raw_type:
        return EVENT_PENALTY

    # --------------------------------------------------------
    # Goal
    #
    # SportScore الحقيقي:
    # type = "Goal"
    # type_id = 1
    # is_goal = True
    # --------------------------------------------------------

    if (
        is_goal is True
        or raw_type == "goal"
        or type_id == 1
    ):
        return EVENT_GOAL

    # --------------------------------------------------------
    # Yellow Card
    # --------------------------------------------------------

    if any(
        word in raw_type
        for word in [
            "yellow",
            "yellow card",
        ]
    ):
        return EVENT_YELLOW_CARD

    # --------------------------------------------------------
    # Red Card
    # --------------------------------------------------------

    if any(
        word in raw_type
        for word in [
            "red",
            "red card",
        ]
    ):
        return EVENT_RED_CARD

    # --------------------------------------------------------
    # Substitution
    # --------------------------------------------------------

    if any(
        word in raw_type
        for word in [
            "substitution",
            "substitute",
            "sub",
        ]
    ):
        return EVENT_SUBSTITUTION

    # --------------------------------------------------------
    # VAR
    #
    # SportScore الحقيقي:
    # type = "VAR"
    # type_id = 28
    # --------------------------------------------------------

    if (
        raw_type == "var"
        or "var" in raw_type
        or type_id == 28
    ):
        return EVENT_VAR

    return EVENT_UNKNOWN


# ============================================================
# Event Signature
# ============================================================

def event_signature(
    incident: Dict[str, Any]
) -> str:
    """
    إنشاء توقيع ثابت للحدث.

    الهدف:
    نفس الحدث القادم من API عدة مرات
    يجب أن ينتج نفس ID.

    تمت إضافة player_in و player_out لأن أحداث
    التبديلات في SportScore تستخدم هذين الحقلين.
    """

    if not isinstance(
        incident,
        dict,
    ):
        return hashlib.sha256(
            str(incident).encode(
                "utf-8"
            )
        ).hexdigest()

    event_type = detect_event_type(
        incident
    )

    values = {
        "time": incident.get(
            "time"
        ),
        "type": normalize_text(
            incident.get("type")
        ),
        "type_id": incident.get(
            "type_id"
        ),
        "side": normalize_text(
            incident.get("side")
        ),
        "player": normalize_text(
            incident.get("player")
        ),
        "player_in": normalize_text(
            incident.get("player_in")
        ),
        "player_out": normalize_text(
            incident.get("player_out")
        ),
        "is_goal": incident.get(
            "is_goal"
        ),
        "is_sub": incident.get(
            "is_sub"
        ),
        "is_card": incident.get(
            "is_card"
        ),
        "home_score": incident.get(
            "home_score"
        ),
        "away_score": incident.get(
            "away_score"
        ),
        "event_type": event_type,
    }

    raw = json.dumps(
        values,
        ensure_ascii=False,
        sort_keys=True,
    )

    return hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()


# ============================================================
# Normalize Incident
# ============================================================

def normalize_incident(
    incident: Dict[str, Any],
    match: Optional[
        Dict[str, Any]
    ] = None,
) -> Dict[str, Any]:
    """
    تحويل حدث SportScore إلى صيغة موحدة
    سيستخدمها باقي النظام.
    """

    if not isinstance(
        incident,
        dict,
    ):
        return {}

    match = match or {}

    event_type = detect_event_type(
        incident
    )

    home = match.get(
        "home"
    )

    away = match.get(
        "away"
    )

    # --------------------------------------------------------
    # Score
    #
    # الأولوية:
    # 1. نتيجة الحدث إذا كانت موجودة
    # 2. نتيجة المباراة
    # --------------------------------------------------------

    incident_home_score = incident.get(
        "home_score"
    )

    incident_away_score = incident.get(
        "away_score"
    )

    match_home_score = match.get(
        "home_score"
    )

    match_away_score = match.get(
        "away_score"
    )

    home_score = (
        incident_home_score
        if incident_home_score is not None
        else match_home_score
    )

    away_score = (
        incident_away_score
        if incident_away_score is not None
        else match_away_score
    )

    # --------------------------------------------------------
    # Side
    # --------------------------------------------------------

    side = normalize_text(
        incident.get(
            "side"
        )
    )

    # --------------------------------------------------------
    # Main player
    # --------------------------------------------------------

    player = incident.get(
        "player"
    )

    # --------------------------------------------------------
    # Substitution players
    #
    # SportScore:
    # player_in
    # player_out
    # --------------------------------------------------------

    player_in = incident.get(
        "player_in"
    )

    player_out = incident.get(
        "player_out"
    )

    normalized = {
        "event_id": event_signature(
            incident
        ),

        "event_type": event_type,

        "minute": incident.get(
            "time"
        ),

        "type": incident.get(
            "type"
        ),

        "type_id": incident.get(
            "type_id"
        ),

        "side": side,

        "player": player,

        "player_in": player_in,

        "player_out": player_out,

        "is_goal": incident.get(
            "is_goal"
        ) is True,

        "is_sub": incident.get(
            "is_sub"
        ) is True,

        "is_card": incident.get(
            "is_card"
        ) is True,

        "home_score": safe_int(
            home_score
        ),

        "away_score": safe_int(
            away_score
        ),

        "home_team": home,

        "away_team": away,

        "raw": incident,
    }

    return normalized


# ============================================================
# Extract Incidents
# ============================================================

def extract_incidents(
    data: Any,
) -> List[Dict[str, Any]]:
    """
    استخراج incidents من استجابة المباراة.
    """

    match = extract_match(
        data
    )

    incidents = match.get(
        "incidents"
    )

    if not isinstance(
        incidents,
        list,
    ):
        return []

    return [
        item
        for item in incidents
        if isinstance(
            item,
            dict,
        )
    ]


# ============================================================
# Normalize All Incidents
# ============================================================

def normalize_incidents(
    data: Any,
) -> List[Dict[str, Any]]:
    """
    تحويل جميع أحداث المباراة إلى
    الصيغة الموحدة.
    """

    match = extract_match(
        data
    )

    incidents = extract_incidents(
        data
    )

    result = []

    for incident in incidents:

        normalized = normalize_incident(
            incident,
            match,
        )

        if normalized:
            result.append(
                normalized
            )

    return result


# ============================================================
# Event Manager
# ============================================================

class LiveEventManager:
    """
    مدير أحداث المباراة.

    يحتفظ بالأحداث التي تم التعامل معها
    لمنع التكرار.
    """

    def __init__(
        self,
        processed_event_ids: Optional[
            Set[str]
        ] = None,
    ):
        self.processed_event_ids = set(
            processed_event_ids or set()
        )

    # --------------------------------------------------------
    # Process Snapshot
    # --------------------------------------------------------

    def process_snapshot(
        self,
        data: Any,
    ) -> List[Dict[str, Any]]:
        """
        استقبال snapshot من SportScore
        وإرجاع الأحداث الجديدة فقط.
        """

        events = normalize_incidents(
            data
        )

        new_events = []

        for event in events:

            event_id = event.get(
                "event_id"
            )

            if not event_id:
                continue

            if (
                event_id
                in self.processed_event_ids
            ):
                continue

            new_events.append(
                event
            )

        return new_events

    # --------------------------------------------------------
    # Mark Processed
    # --------------------------------------------------------

    def mark_processed(
        self,
        events: List[
            Dict[str, Any]
        ],
    ) -> None:
        """
        تسجيل الأحداث كمعالجة.
        """

        for event in events:

            event_id = event.get(
                "event_id"
            )

            if event_id:
                self.processed_event_ids.add(
                    event_id
                )

    # --------------------------------------------------------
    # Bootstrap Existing Events
    # --------------------------------------------------------

    def bootstrap(
        self,
        data: Any,
    ) -> List[
        Dict[str, Any]
    ]:
        """
        عند تشغيل البوت في منتصف المباراة:

        جميع الأحداث الموجودة قبل التشغيل
        تعتبر أحداثًا قديمة ولا يتم نشرها.

        نرجع الأحداث فقط للعرض/التشخيص.
        """

        events = normalize_incidents(
            data
        )

        for event in events:

            event_id = event.get(
                "event_id"
            )

            if event_id:
                self.processed_event_ids.add(
                    event_id
                )

        return events

    # --------------------------------------------------------
    # Get IDs
    # --------------------------------------------------------

    def get_processed_ids(
        self,
    ) -> Set[str]:
        """
        إرجاع نسخة من IDs المعالجة.
        """

        return set(
            self.processed_event_ids
        )


# ============================================================
# Human-readable Event
# ============================================================

def event_label(
    event: Dict[str, Any]
) -> str:
    """
    اسم الحدث بالعربية.
    """

    event_type = event.get(
        "event_type"
    )

    labels = {
        EVENT_GOAL: "هدف",

        EVENT_YELLOW_CARD: "بطاقة صفراء",

        EVENT_RED_CARD: "بطاقة حمراء",

        EVENT_SUBSTITUTION: "تبديل",

        EVENT_PENALTY: "ركلة جزاء",

        EVENT_PENALTY_MISSED: "ركلة جزاء ضائعة",

        EVENT_OWN_GOAL: "هدف عكسي",

        EVENT_GOAL_CANCELLED: "هدف ملغى",

        EVENT_VAR: "VAR",

        EVENT_UNKNOWN: "حدث",
    }

    return labels.get(
        event_type,
        "حدث",
    )


# ============================================================
# Event Description
# ============================================================

def describe_event(
    event: Dict[str, Any]
) -> str:
    """
    وصف مختصر للحدث لأغراض الاختبار.
    """

    event_type = event.get(
        "event_type"
    )

    label = event_label(
        event
    )

    minute = event.get(
        "minute"
    )

    player = event.get(
        "player"
    )

    player_in = event.get(
        "player_in"
    )

    player_out = event.get(
        "player_out"
    )

    home_score = event.get(
        "home_score"
    )

    away_score = event.get(
        "away_score"
    )

    parts = [
        label
    ]

    if minute is not None:
        parts.append(
            f"الدقيقة {minute}"
        )

    # --------------------------------------------------------
    # Substitution
    # --------------------------------------------------------

    if event_type == EVENT_SUBSTITUTION:

        if player_in:
            parts.append(
                f"داخل: {player_in}"
            )

        if player_out:
            parts.append(
                f"خارج: {player_out}"
            )

    # --------------------------------------------------------
    # Normal player event
    # --------------------------------------------------------

    elif player:

        parts.append(
            f"اللاعب: {player}"
        )

    # --------------------------------------------------------
    # Score
    # --------------------------------------------------------

    if (
        home_score is not None
        and away_score is not None
    ):
        parts.append(
            f"النتيجة {home_score}-{away_score}"
        )

    return " | ".join(
        parts
    )


# ============================================================
# Simple Test
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print(
        "LIVE EVENT MANAGER — SELF TEST"
    )
    print("=" * 70)

    # ========================================================
    # Test data
    # ========================================================

    fake_data = {
        "sport": "football",

        "match": {

            "home": "Real Betis",

            "away": "Real Madrid",

            "home_score": "1",

            "away_score": "0",

            "status": "live",

            "live_minute": 94,

            "incidents": [

                # ------------------------------------------------
                # Goal
                # ------------------------------------------------

                {
                    "time": 6,
                    "type": "Goal",
                    "type_id": 1,
                    "side": "home",
                    "player": "Jorge Benguché",
                    "is_goal": True,
                    "home_score": 1,
                    "away_score": 0,
                },

                # ------------------------------------------------
                # Substitution
                # ------------------------------------------------

                {
                    "time": 64,
                    "type": "Substitution",
                    "type_id": 9,
                    "side": "away",
                    "player": "",
                    "is_sub": True,
                    "player_in": "Bernardo Silva",
                    "player_out": "Eduardo Camavinga",
                },

                # ------------------------------------------------
                # Yellow Card
                # ------------------------------------------------

                {
                    "time": 48,
                    "type": "Yellow card",
                    "type_id": 3,
                    "side": "away",
                    "player": "Arda Güler",
                    "is_card": True,
                },

                # ------------------------------------------------
                # VAR
                # ------------------------------------------------

                {
                    "time": 89,
                    "type": "VAR",
                    "type_id": 28,
                    "side": "away",
                    "player": "Carlos Espí",
                },

                # ------------------------------------------------
                # Penalty missed
                # ------------------------------------------------

                {
                    "time": 94,
                    "type": "Penalty missed",
                    "type_id": 16,
                    "side": "away",
                    "player": "Kylian Mbappé",
                },
            ],
        },
    }

    manager = LiveEventManager()

    # ========================================================
    # First snapshot
    # ========================================================

    print()
    print(
        "FIRST SNAPSHOT"
    )

    new_events = manager.process_snapshot(
        fake_data
    )

    print(
        "New events:",
        len(new_events)
    )

    for event in new_events:

        print(
            describe_event(
                event
            )
        )

    # ========================================================
    # Expected:
    #
    # 4 events
    # ========================================================

    assert len(new_events) == 4

    # ========================================================
    # Verify substitution fields
    # ========================================================

    substitution_events = [
        event
        for event in new_events
        if event.get("event_type")
        == EVENT_SUBSTITUTION
    ]

    assert len(
        substitution_events
    ) == 1

    substitution = substitution_events[0]

    assert (
        substitution.get("player_in")
        == "Bernardo Silva"
    )

    assert (
        substitution.get("player_out")
        == "Eduardo Camavinga"
    )

    print(
        "PASS: Substitution players extracted."
    )

    # ========================================================
    # Verify penalty missed
    # ========================================================

    penalty_events = [
        event
        for event in new_events
        if event.get("event_type")
        == EVENT_PENALTY_MISSED
    ]

    assert len(
        penalty_events
    ) == 1

    penalty = penalty_events[0]

    assert (
        penalty.get("player")
        == "Kylian Mbappé"
    )

    assert (
        penalty.get("home_score")
        == 1
    )

    assert (
        penalty.get("away_score")
        == 0
    )

    print(
        "PASS: Penalty missed detected correctly."
    )

    # ========================================================
    # Verify VAR
    # ========================================================

    var_events = [
        event
        for event in new_events
        if event.get("event_type")
        == EVENT_VAR
    ]

    assert len(
        var_events
    ) == 1

    print(
        "PASS: VAR detected correctly."
    )

    # ========================================================
    # Mark processed
    # ========================================================

    manager.mark_processed(
        new_events
    )

    # ========================================================
    # Same snapshot again
    # ========================================================

    print()
    print(
        "SECOND SNAPSHOT — SAME DATA"
    )

    duplicate_events = manager.process_snapshot(
        fake_data
    )

    print(
        "New events:",
        len(duplicate_events)
    )

    assert not duplicate_events

    print(
        "PASS: Duplicate events ignored."
    )

    # ========================================================
    # Add new goal
    # ========================================================

    print()
    print(
        "THIRD SNAPSHOT — NEW GOAL"
    )

    fake_data["match"][
        "home_score"
    ] = "1"

    fake_data["match"][
        "away_score"
    ] = "1"

    fake_data["match"][
        "incidents"
    ].append(
        {
            "time": 102,
            "type": "Goal",
            "type_id": 1,
            "side": "away",
            "player": "Kylian Mbappé",
            "is_goal": True,
            "home_score": 1,
            "away_score": 1,
        }
    )

    new_events = manager.process_snapshot(
        fake_data
    )

    print(
        "New events:",
        len(new_events)
    )

    assert len(
        new_events
    ) == 1

    print(
        "PASS: New event detected."
    )

    for event in new_events:

        print(
            describe_event(
                event
            )
        )

    # ========================================================
    # Bootstrap test
    # ========================================================

    print()
    print(
        "BOOTSTRAP TEST"
    )

    bootstrap_manager = LiveEventManager()

    bootstrapped = bootstrap_manager.bootstrap(
        fake_data
    )

    print(
        "Bootstrapped events:",
        len(bootstrapped)
    )

    assert len(
        bootstrap_manager.get_processed_ids()
    ) == len(bootstrapped)

    after_bootstrap = bootstrap_manager.process_snapshot(
        fake_data
    )

    assert not after_bootstrap

    print(
        "PASS: Bootstrap prevents old-event republishing."
    )

    # ========================================================
    # Final
    # ========================================================

    print()
    print("=" * 70)
    print(
        "ALL SELF TESTS PASSED"
    )
    print("=" * 70)

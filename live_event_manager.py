# ============================================================
# LIVE EVENT MANAGER
# ============================================================
# إدارة أحداث المباريات المباشرة:
# - الأهداف
# - الأهداف العكسية
# - إلغاء الأهداف
# - البطاقات الصفراء
# - البطاقات الحمراء
# - التبديلات
# - ركلات الجزاء
# - ركلات الجزاء الضائعة
# - VAR
# - منع تكرار الأحداث
# - Bootstrap للأحداث القديمة
# ============================================================

from __future__ import annotations

from typing import Any, Dict, List, Optional
import hashlib
import json


# ============================================================
# Event types
# ============================================================

EVENT_GOAL = "goal"
EVENT_OWN_GOAL = "own_goal"
EVENT_GOAL_CANCELLED = "goal_cancelled"

EVENT_YELLOW_CARD = "yellow_card"
EVENT_RED_CARD = "red_card"

EVENT_SUBSTITUTION = "substitution"

EVENT_PENALTY = "penalty"
EVENT_PENALTY_MISSED = "penalty_missed"

EVENT_VAR = "var"

EVENT_UNKNOWN = "unknown"


# ============================================================
# Helpers
# ============================================================

def safe_int(value: Any, default: Optional[int] = None) -> Optional[int]:
    """
    تحويل القيمة إلى integer بأمان.
    """
    if value is None:
        return default

    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_text(value: Any, default: str = "") -> str:
    """
    تحويل القيمة إلى نص بأمان.
    """
    if value is None:
        return default

    return str(value).strip()


def normalize_text(value: Any) -> str:
    """
    تنظيف النص للمقارنة.
    """
    return " ".join(safe_text(value).lower().split())


# ============================================================
# Event type detection
# ============================================================

def detect_event_type(incident: Dict[str, Any]) -> str:
    """
    تحديد نوع الحدث من بيانات SportScore.

    ترتيب الفحص مهم جدًا:
    1. إلغاء الهدف
    2. الهدف العكسي
    3. ركلة الجزاء الضائعة
    4. VAR
    5. البطاقات
    6. التبديل
    7. ركلة الجزاء
    8. الهدف العادي
    """

    if not isinstance(incident, dict):
        return EVENT_UNKNOWN

    event_type = normalize_text(
        incident.get("type")
        or incident.get("event_type")
        or incident.get("name")
    )

    type_id = safe_int(incident.get("type_id"))

    # --------------------------------------------------------
    # Goal cancelled
    # --------------------------------------------------------

    cancelled_keywords = (
        "goal cancelled",
        "goal canceled",
        "cancelled goal",
        "canceled goal",
        "disallowed goal",
        "goal disallowed",
        "goal ruled out",
        "cancelled",
        "canceled",
    )

    if any(keyword in event_type for keyword in cancelled_keywords):
        return EVENT_GOAL_CANCELLED

    if type_id in (2, 3) and "goal" in event_type:
        return EVENT_GOAL_CANCELLED

    # --------------------------------------------------------
    # Own goal
    # --------------------------------------------------------

    own_goal_keywords = (
        "own goal",
        "own-goal",
        "autogol",
    )

    if any(keyword in event_type for keyword in own_goal_keywords):
        return EVENT_OWN_GOAL

    # --------------------------------------------------------
    # Penalty missed
    # --------------------------------------------------------

    penalty_missed_keywords = (
        "penalty missed",
        "missed penalty",
        "penalty miss",
        "penalty failed",
        "missed",
    )

    if any(keyword in event_type for keyword in penalty_missed_keywords):
        if "penalty" in event_type or type_id == 16:
            return EVENT_PENALTY_MISSED

    # SportScore observed type_id = 16
    if type_id == 16:
        return EVENT_PENALTY_MISSED

    # --------------------------------------------------------
    # VAR
    # --------------------------------------------------------

    var_keywords = (
        "var",
        "video assistant referee",
        "video assistant",
    )

    if any(keyword == event_type or keyword in event_type for keyword in var_keywords):
        return EVENT_VAR

    # SportScore observed type_id = 28
    if type_id == 28:
        return EVENT_VAR

    # --------------------------------------------------------
    # Red card
    # --------------------------------------------------------

    red_card_keywords = (
        "red card",
        "second yellow",
        "second yellow card",
        "red",
    )

    if any(keyword in event_type for keyword in red_card_keywords):
        return EVENT_RED_CARD

    # --------------------------------------------------------
    # Yellow card
    # --------------------------------------------------------

    yellow_card_keywords = (
        "yellow card",
        "yellow",
        "booking",
    )

    if any(keyword in event_type for keyword in yellow_card_keywords):
        return EVENT_YELLOW_CARD

    # --------------------------------------------------------
    # Substitution
    # --------------------------------------------------------

    substitution_keywords = (
        "substitution",
        "substitute",
        "substituted",
    )

    if any(keyword in event_type for keyword in substitution_keywords):
        return EVENT_SUBSTITUTION

    if incident.get("is_sub") is True:
        return EVENT_SUBSTITUTION

    if incident.get("player_in") or incident.get("player_out"):
        return EVENT_SUBSTITUTION

    # --------------------------------------------------------
    # Penalty
    # --------------------------------------------------------

    if "penalty" in event_type:
        return EVENT_PENALTY

    # --------------------------------------------------------
    # Goal
    # --------------------------------------------------------

    if "goal" in event_type:
        return EVENT_GOAL

    if incident.get("is_goal") is True:
        return EVENT_GOAL

    # --------------------------------------------------------
    # Unknown
    # --------------------------------------------------------

    return EVENT_UNKNOWN


# ============================================================
# Event signature
# ============================================================

def event_signature(
    incident: Dict[str, Any],
    event_type: Optional[str] = None,
) -> str:
    """
    إنشاء بصمة ثابتة للحدث لمنع التكرار.

    لا نعتمد على رقم الحدث فقط لأن بعض APIs
    قد لا توفر ID ثابتًا.
    """

    if not isinstance(incident, dict):
        incident = {}

    if event_type is None:
        event_type = detect_event_type(incident)

    data = {
        "time": safe_int(incident.get("time")),
        "type": safe_text(incident.get("type")),
        "type_id": safe_int(incident.get("type_id")),
        "side": safe_text(incident.get("side")),
        "player": safe_text(incident.get("player")),
        "player_in": safe_text(incident.get("player_in")),
        "player_out": safe_text(incident.get("player_out")),
        "is_goal": bool(incident.get("is_goal")),
        "is_sub": bool(incident.get("is_sub")),
        "is_card": bool(incident.get("is_card")),
        "home_score": safe_int(incident.get("home_score")),
        "away_score": safe_int(incident.get("away_score")),
        "event_type": event_type,
    }

    raw = json.dumps(
        data,
        ensure_ascii=False,
        sort_keys=True,
    )

    return hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()


# ============================================================
# Normalize incident
# ============================================================

def normalize_incident(
    incident: Dict[str, Any],
) -> Dict[str, Any]:
    """
    توحيد بيانات الحدث في شكل ثابت.
    """

    if not isinstance(incident, dict):
        incident = {}

    event_type = detect_event_type(incident)

    normalized = {
        "id": safe_text(incident.get("id")),
        "time": safe_int(incident.get("time")),
        "type": safe_text(incident.get("type")),
        "type_id": safe_int(incident.get("type_id")),
        "side": safe_text(incident.get("side")),

        "player": safe_text(incident.get("player")),

        "player_in": safe_text(
            incident.get("player_in")
        ),

        "player_out": safe_text(
            incident.get("player_out")
        ),

        "is_goal": bool(
            incident.get("is_goal")
        ),

        "is_sub": bool(
            incident.get("is_sub")
        ),

        "is_card": bool(
            incident.get("is_card")
        ),

        "home_score": safe_int(
            incident.get("home_score")
        ),

        "away_score": safe_int(
            incident.get("away_score")
        ),

        "event_type": event_type,
    }

    normalized["signature"] = event_signature(
        incident,
        event_type,
    )

    return normalized


# ============================================================
# Event label
# ============================================================

def event_label(event_type: str) -> str:
    """
    اسم الحدث بالعربية.
    """

    labels = {
        EVENT_GOAL: "هدف",
        EVENT_OWN_GOAL: "هدف عكسي",
        EVENT_GOAL_CANCELLED: "هدف ملغى",

        EVENT_YELLOW_CARD: "بطاقة صفراء",
        EVENT_RED_CARD: "بطاقة حمراء",

        EVENT_SUBSTITUTION: "تبديل",

        EVENT_PENALTY: "ركلة جزاء",

        EVENT_PENALTY_MISSED: "ركلة جزاء ضائعة",

        EVENT_VAR: "VAR",

        EVENT_UNKNOWN: "حدث",
    }

    return labels.get(
        event_type,
        "حدث",
    )


# ============================================================
# Describe event
# ============================================================

def describe_event(
    event: Dict[str, Any],
) -> str:
    """
    وصف مختصر للحدث للاستخدام في السجلات والاختبارات.
    """

    if not isinstance(event, dict):
        return "حدث غير معروف"

    event_type = event.get(
        "event_type",
        EVENT_UNKNOWN,
    )

    label = event_label(event_type)

    minute = event.get("time")

    player = safe_text(
        event.get("player")
    )

    player_in = safe_text(
        event.get("player_in")
    )

    player_out = safe_text(
        event.get("player_out")
    )

    home_score = event.get(
        "home_score"
    )

    away_score = event.get(
        "away_score"
    )

    parts = [label]

    if minute is not None:
        parts.append(
            f"الدقيقة {minute}"
        )

    if event_type == EVENT_SUBSTITUTION:

        if player_in:
            parts.append(
                f"داخل: {player_in}"
            )

        if player_out:
            parts.append(
                f"خارج: {player_out}"
            )

        if not player_in and not player_out and player:
            parts.append(
                f"اللاعب: {player}"
            )

    elif player:
        parts.append(
            f"اللاعب: {player}"
        )

    if (
        home_score is not None
        and away_score is not None
    ):
        parts.append(
            f"النتيجة {home_score}-{away_score}"
        )

    return " | ".join(parts)


# ============================================================
# Live Event Manager
# ============================================================

class LiveEventManager:
    """
    مدير أحداث المباراة المباشرة.

    المسؤوليات:
    - اكتشاف الأحداث الجديدة
    - منع التكرار
    - Bootstrap للأحداث الموجودة عند البداية
    - الاحتفاظ بالأحداث التي تمت معالجتها
    """

    def __init__(self) -> None:

        self.processed_event_ids = set()

    # --------------------------------------------------------
    # Create event ID
    # --------------------------------------------------------

    def get_event_id(
        self,
        incident: Dict[str, Any],
    ) -> str:
        """
        الحصول على معرف ثابت للحدث.
        """

        if not isinstance(incident, dict):
            incident = {}

        incident_id = safe_text(
            incident.get("id")
        )

        if incident_id:
            return incident_id

        normalized = normalize_incident(
            incident
        )

        return normalized["signature"]

    # --------------------------------------------------------
    # Process snapshot
    # --------------------------------------------------------

    def process_snapshot(
        self,
        snapshot: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        معالجة Snapshot للمباراة.

        يعيد الأحداث الجديدة فقط.
        """

        if not isinstance(snapshot, dict):
            return []

        incidents = snapshot.get(
            "incidents",
            []
        )

        if not isinstance(incidents, list):
            return []

        new_events: List[Dict[str, Any]] = []

        for incident in incidents:

            if not isinstance(
                incident,
                dict,
            ):
                continue

            event_id = self.get_event_id(
                incident
            )

            if event_id in self.processed_event_ids:
                continue

            normalized = normalize_incident(
                incident
            )

            normalized["event_id"] = event_id

            new_events.append(
                normalized
            )

        return new_events

    # --------------------------------------------------------
    # Mark processed
    # --------------------------------------------------------

    def mark_processed(
        self,
        event: Dict[str, Any],
    ) -> None:
        """
        تسجيل الحدث على أنه تمت معالجته.
        """

        if not isinstance(event, dict):
            return

        event_id = safe_text(
            event.get("event_id")
        )

        if not event_id:
            event_id = safe_text(
                event.get("id")
            )

        if not event_id:

            event_id = safe_text(
                event.get("signature")
            )

        if event_id:
            self.processed_event_ids.add(
                event_id
            )

    # --------------------------------------------------------
    # Bootstrap
    # --------------------------------------------------------

    def bootstrap(
        self,
        snapshot: Dict[str, Any],
    ) -> None:
        """
        تسجيل جميع الأحداث الموجودة مسبقًا
        على أنها قديمة.

        مهم جدًا عند إعادة تشغيل البوت:
        الأحداث القديمة لا يجب إعادة نشرها.
        """

        if not isinstance(snapshot, dict):
            return

        incidents = snapshot.get(
            "incidents",
            []
        )

        if not isinstance(incidents, list):
            return

        for incident in incidents:

            if not isinstance(
                incident,
                dict,
            ):
                continue

            event_id = self.get_event_id(
                incident
            )

            if event_id:
                self.processed_event_ids.add(
                    event_id
                )

    # --------------------------------------------------------
    # Get processed IDs
    # --------------------------------------------------------

    def get_processed_ids(self) -> set:
        """
        إرجاع نسخة من معرفات الأحداث التي تمت معالجتها.
        """

        return set(
            self.processed_event_ids
        )


# ============================================================
# Self Test
# ============================================================

def run_self_test() -> None:

    print("=" * 70)
    print("LIVE EVENT MANAGER — SELF TEST")
    print("=" * 70)

    manager = LiveEventManager()

    # --------------------------------------------------------
    # First snapshot
    # --------------------------------------------------------

    first_snapshot = {
        "incidents": [

            {
                "id": "goal-1",
                "time": 6,
                "type": "Goal",
                "type_id": 1,
                "side": "home",
                "player": "Jorge Benguché",
                "is_goal": True,
                "home_score": 1,
                "away_score": 0,
            },

            {
                "id": "sub-1",
                "time": 64,
                "type": "Substitution",
                "type_id": 9,
                "side": "away",
                "player": "",
                "is_sub": True,
                "player_in": "Bernardo Silva",
                "player_out": "Eduardo Camavinga",
                "home_score": 1,
                "away_score": 0,
            },

            {
                "id": "yellow-1",
                "time": 48,
                "type": "Yellow Card",
                "type_id": 3,
                "side": "away",
                "player": "Arda Güler",
                "is_card": True,
                "home_score": 1,
                "away_score": 0,
            },

            {
                "id": "var-1",
                "time": 89,
                "type": "VAR",
                "type_id": 28,
                "side": "away",
                "player": "Carlos Espí",
                "home_score": 1,
                "away_score": 0,
            },

            {
                "id": "penalty-missed-1",
                "time": 94,
                "type": "Penalty missed",
                "type_id": 16,
                "side": "away",
                "player": "Kylian Mbappé",
                "home_score": 1,
                "away_score": 0,
            },
        ]
    }

    new_events = manager.process_snapshot(
        first_snapshot
    )

    print()
    print("FIRST SNAPSHOT")
    print(
        f"New events: {len(new_events)}"
    )

    for event in new_events:
        print(
            describe_event(event)
        )

    # --------------------------------------------------------
    # FIX:
    # We now have 5 test events:
    # goal
    # substitution
    # yellow card
    # VAR
    # penalty missed
    # --------------------------------------------------------

    assert len(new_events) == 5

    print(
        "PASS: First snapshot contains 5 events."
    )

    # --------------------------------------------------------
    # Test individual event types
    # --------------------------------------------------------

    event_types = {
        EVENT_GOAL: False,
        EVENT_SUBSTITUTION: False,
        EVENT_YELLOW_CARD: False,
        EVENT_VAR: False,
        EVENT_PENALTY_MISSED: False,
    }

    for event in new_events:

        event_type = event.get(
            "event_type"
        )

        if event_type in event_types:
            event_types[event_type] = True

    assert event_types[EVENT_GOAL]

    print(
        "PASS: Goal detected correctly."
    )

    assert event_types[
        EVENT_SUBSTITUTION
    ]

    substitution = next(
        event
        for event in new_events
        if event.get("event_type")
        == EVENT_SUBSTITUTION
    )

    assert substitution[
        "player_in"
    ] == "Bernardo Silva"

    assert substitution[
        "player_out"
    ] == "Eduardo Camavinga"

    print(
        "PASS: Substitution players extracted."
    )

    assert event_types[
        EVENT_YELLOW_CARD
    ]

    print(
        "PASS: Yellow card detected correctly."
    )

    assert event_types[
        EVENT_VAR
    ]

    print(
        "PASS: VAR detected correctly."
    )

    assert event_types[
        EVENT_PENALTY_MISSED
    ]

    penalty_event = next(
        event
        for event in new_events
        if event.get("event_type")
        == EVENT_PENALTY_MISSED
    )

    assert penalty_event[
        "player"
    ] == "Kylian Mbappé"

    print(
        "PASS: Penalty missed detected correctly."
    )

    # --------------------------------------------------------
    # Mark all first events as processed
    # --------------------------------------------------------

    for event in new_events:
        manager.mark_processed(
            event
        )

    # --------------------------------------------------------
    # Duplicate snapshot
    # --------------------------------------------------------

    duplicate_events = (
        manager.process_snapshot(
            first_snapshot
        )
    )

    assert len(
        duplicate_events
    ) == 0

    print(
        "PASS: Duplicate events ignored."
    )

    # --------------------------------------------------------
    # New event
    # --------------------------------------------------------

    second_snapshot = {
        "incidents":
            first_snapshot[
                "incidents"
            ] + [

                {
                    "id": "goal-2",
                    "time": 95,
                    "type": "Goal",
                    "type_id": 1,
                    "side": "away",
                    "player": "Vinícius Junior",
                    "is_goal": True,
                    "home_score": 1,
                    "away_score": 1,
                }
            ]
    }

    second_events = (
        manager.process_snapshot(
            second_snapshot
        )
    )

    assert len(
        second_events
    ) == 1

    assert second_events[0][
        "event_type"
    ] == EVENT_GOAL

    assert second_events[0][
        "player"
    ] == "Vinícius Junior"

    print(
        "PASS: New event detected."
    )

    # --------------------------------------------------------
    # Bootstrap test
    # --------------------------------------------------------

    bootstrap_manager = (
        LiveEventManager()
    )

    bootstrap_manager.bootstrap(
        first_snapshot
    )

    bootstrap_events = (
        bootstrap_manager.process_snapshot(
            first_snapshot
        )
    )

    assert len(
        bootstrap_events
    ) == 0

    print(
        "PASS: Bootstrap prevents old-event republishing."
    )

    # --------------------------------------------------------
    # Goal cancelled
    # --------------------------------------------------------

    cancelled_incident = {
        "id": "cancelled-1",
        "time": 50,
        "type": "Goal cancelled",
        "type_id": 2,
        "side": "home",
        "player": "Test Player",
    }

    cancelled_type = detect_event_type(
        cancelled_incident
    )

    assert cancelled_type == (
        EVENT_GOAL_CANCELLED
    )

    print(
        "PASS: Goal cancelled detected correctly."
    )

    # --------------------------------------------------------
    # Own goal
    # --------------------------------------------------------

    own_goal_incident = {
        "id": "own-goal-1",
        "time": 55,
        "type": "Own Goal",
        "type_id": 1,
        "side": "home",
        "player": "Test Player",
    }

    own_goal_type = detect_event_type(
        own_goal_incident
    )

    assert own_goal_type == (
        EVENT_OWN_GOAL
    )

    print(
        "PASS: Own goal detected correctly."
    )

    # --------------------------------------------------------
    # Red card
    # --------------------------------------------------------

    red_card_incident = {
        "id": "red-1",
        "time": 70,
        "type": "Red Card",
        "type_id": 5,
        "side": "away",
        "player": "Test Player",
    }

    red_card_type = detect_event_type(
        red_card_incident
    )

    assert red_card_type == (
        EVENT_RED_CARD
    )

    print(
        "PASS: Red card detected correctly."
    )

    # --------------------------------------------------------
    # Finished
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("ALL SELF TESTS PASSED")
    print("=" * 70)


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    run_self_test()

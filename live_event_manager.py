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
EVENT_OWN_GOAL = "own_goal"
EVENT_GOAL_CANCELLED = "goal_cancelled"
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

def detect_event_type(incident: Dict[str, Any]) -> str:
    """
    تحديد نوع الحدث اعتمادًا على بيانات SportScore.
    """

    if not isinstance(incident, dict):
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
    # Goal
    # --------------------------------------------------------

    if (
        is_goal is True
        or raw_type == "goal"
        or type_id == 1
    ):
        return EVENT_GOAL

    # --------------------------------------------------------
    # Own goal
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
    # Yellow card
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
    # Red card
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
    # Penalty
    # --------------------------------------------------------

    if "penalty" in raw_type:
        return EVENT_PENALTY

    # --------------------------------------------------------
    # Cancelled goal
    # --------------------------------------------------------

    if any(
        word in raw_type
        for word in [
            "cancelled goal",
            "disallowed goal",
            "goal cancelled",
            "goal disallowed",
        ]
    ):
        return EVENT_GOAL_CANCELLED

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
        "is_goal": incident.get(
            "is_goal"
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

    home_score = (
        incident.get(
            "home_score"
        )
        if incident.get(
            "home_score"
        ) is not None
        else match.get(
            "home_score"
        )
    )

    away_score = (
        incident.get(
            "away_score"
        )
        if incident.get(
            "away_score"
        ) is not None
        else match.get(
            "away_score"
        )
    )

    side = normalize_text(
        incident.get(
            "side"
        )
    )

    player = incident.get(
        "player"
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
        "is_goal": incident.get(
            "is_goal"
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
        EVENT_OWN_GOAL: "هدف عكسي",
        EVENT_GOAL_CANCELLED: "هدف ملغى",
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

    label = event_label(
        event
    )

    minute = event.get(
        "minute"
    )

    player = event.get(
        "player"
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

    if player:
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

    fake_data = {
        "sport": "football",
        "match": {
            "home": "Real Betis",
            "away": "Real Madrid",
            "home_score": "1",
            "away_score": "0",
            "status": "live",
            "live_minute": 27,
            "incidents": [
                {
                    "time": 6,
                    "type": "Goal",
                    "type_id": 1,
                    "side": "home",
                    "player": "Jorge Benguché",
                    "is_goal": True,
                    "home_score": 1,
                    "away_score": 0,
                }
            ],
        },
    }

    manager = LiveEventManager()

    # --------------------------------------------------------
    # First snapshot
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Mark processed
    # --------------------------------------------------------

    manager.mark_processed(
        new_events
    )

    # --------------------------------------------------------
    # Same snapshot again
    # --------------------------------------------------------

    print()
    print(
        "SECOND SNAPSHOT — SAME DATA"
    )

    new_events = manager.process_snapshot(
        fake_data
    )

    print(
        "New events:",
        len(new_events)
    )

    if not new_events:
        print(
            "PASS: Duplicate event ignored."
        )

    # --------------------------------------------------------
    # New goal
    # --------------------------------------------------------

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
            "time": 42,
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

    for event in new_events:

        print(
            describe_event(
                event
            )
        )

    # --------------------------------------------------------
    # Final
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print(
        "SELF TEST COMPLETE"
    )
    print("=" * 70)

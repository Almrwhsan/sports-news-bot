import time
import requests

from live_event_manager import LiveEventManager


# ============================================================
# إعدادات SportScore
# ============================================================

SPORTSCORE_MATCH_URL = (
    "https://sportscore.com/api/widget/match/"
)

DEFAULT_TIMEOUT = 20
DEFAULT_POLL_INTERVAL = 65


# ============================================================
# أدوات مساعدة
# ============================================================

def safe_int(value):

    try:

        if value is None:
            return None

        return int(value)

    except (TypeError, ValueError):

        return None


def normalize_status(value):

    if value is None:
        return ""

    return str(value).strip().lower()


def extract_match(data):

    if not isinstance(data, dict):
        return None

    match = data.get("match")

    if isinstance(match, dict):
        return match

    return None


def get_match_teams(match):

    if not isinstance(match, dict):
        return None, None

    home = match.get("home")
    away = match.get("away")

    home_name = None
    away_name = None

    if isinstance(home, dict):

        home_name = (
            home.get("name")
            or home.get("title")
            or home.get("short_name")
        )

    elif isinstance(home, str):

        home_name = home

    if isinstance(away, dict):

        away_name = (
            away.get("name")
            or away.get("title")
            or away.get("short_name")
        )

    elif isinstance(away, str):

        away_name = away

    return home_name, away_name


def get_score(match):

    if not isinstance(match, dict):
        return None, None

    home_score = (
        match.get("home_score")
        if match.get("home_score") is not None
        else match.get("homeScore")
    )

    away_score = (
        match.get("away_score")
        if match.get("away_score") is not None
        else match.get("awayScore")
    )

    return (
        safe_int(home_score),
        safe_int(away_score),
    )


def get_status(match):

    if not isinstance(match, dict):
        return ""

    status = match.get("status")

    if isinstance(status, dict):

        status = (
            status.get("type")
            or status.get("name")
            or status.get("status")
            or ""
        )

    return normalize_status(status)


def get_status_text(match):

    if not isinstance(match, dict):
        return ""

    value = match.get("status_text")

    if value is None:
        value = match.get("statusText")

    if value is None:
        value = match.get("status")

    if isinstance(value, dict):

        value = (
            value.get("text")
            or value.get("name")
            or value.get("type")
            or ""
        )

    return str(value).strip()


def is_finished(match):

    status = get_status(match)
    text = get_status_text(match).lower()

    finished_values = {
        "finished",
        "complete",
        "completed",
        "ended",
        "ft",
        "after",
    }

    if status in finished_values:
        return True

    finished_words = (
        "finished",
        "completed",
        "ended",
        "full time",
        "match ended",
    )

    return any(
        word in text
        for word in finished_words
    )


def is_not_started(match):

    status = get_status(match)
    text = get_status_text(match).lower()

    not_started_values = {
        "upcoming",
        "scheduled",
        "not_started",
        "not-started",
        "pre",
    }

    if status in not_started_values:
        return True

    not_started_words = (
        "not started",
        "scheduled",
        "upcoming",
        "starts at",
    )

    return any(
        word in text
        for word in not_started_words
    )


def is_live(match):

    if is_finished(match):
        return False

    if is_not_started(match):
        return False

    status = get_status(match)
    text = get_status_text(match).lower()

    live_values = {
        "live",
        "inplay",
        "in-play",
        "playing",
        "started",
        "halftime",
        "half-time",
    }

    if status in live_values:
        return True

    live_words = (
        "live",
        "in play",
        "in-play",
        "playing",
        "halftime",
        "half time",
    )

    if any(
        word in text
        for word in live_words
    ):
        return True

    minute = (
        match.get("live_minute")
        if match.get("live_minute") is not None
        else match.get("minute")
    )

    if minute is not None:

        try:
            return int(minute) > 0

        except (TypeError, ValueError):
            pass

    return False


def get_live_minute(match):

    if not isinstance(match, dict):
        return None

    possible_values = (
        match.get("live_minute"),
        match.get("liveMinute"),
        match.get("minute"),
    )

    for value in possible_values:

        if value is None:
            continue

        try:
            return int(value)

        except (TypeError, ValueError):
            continue

    return None


def get_incidents(match):

    if not isinstance(match, dict):
        return []

    incidents = match.get("incidents")

    if isinstance(incidents, list):
        return incidents

    return []


# ============================================================
# Live Match Manager
# ============================================================

class LiveMatchManager:

    def __init__(
        self,
        slug,
        poll_interval=DEFAULT_POLL_INTERVAL,
        timeout=DEFAULT_TIMEOUT,
        event_manager=None,
    ):

        self.slug = slug
        self.poll_interval = poll_interval
        self.timeout = timeout

        # يحتفظ به للتوافق مع النظام الحالي.
        # معالجة الأحداث الفعلية تتم في live_bot.py.
        self.event_manager = (
            event_manager
            or LiveEventManager()
        )

        self.session = requests.Session()

        self.session.headers.update({

            "User-Agent": (
                "Mozilla/5.0 "
                "(compatible; NabdMadridLiveBot/1.0)"
            ),

            "Accept": "application/json",
        })

        self.previous_score = None

        self.match_started = False

        self.match_finished = False

    # ========================================================
    # جلب المباراة
    # ========================================================

    def fetch_match(self):

        params = {
            "sport": "football",
            "slug": self.slug,
            "src": "nabd-madrid",
        }

        response = self.session.get(
            SPORTSCORE_MATCH_URL,
            params=params,
            timeout=self.timeout,
        )

        response.raise_for_status()

        data = response.json()

        match = extract_match(data)

        if match is None:

            raise ValueError(
                "SportScore response does not contain "
                "match object."
            )

        return match

    # ========================================================
    # تحليل Snapshot
    # ========================================================

    def inspect_match(self, match):

        home, away = get_match_teams(match)

        home_score, away_score = get_score(match)

        status = get_status(match)

        status_text = get_status_text(match)

        minute = get_live_minute(match)

        live = is_live(match)

        not_started = is_not_started(match)

        finished = is_finished(match)

        incidents = get_incidents(match)

        print()
        print("=" * 70)
        print("LIVE MATCH SNAPSHOT")
        print("=" * 70)

        print(f"Home       : {home}")
        print(f"Away       : {away}")
        print(
            f"Score      : "
            f"{home_score} - {away_score}"
        )

        print(f"Status     : {status}")

        print(
            f"Status text: "
            f"{status_text}"
        )

        print(
            f"Minute     : "
            f"{minute}"
        )

        print(
            f"Incidents  : "
            f"{len(incidents)}"
        )

        print()
        print("STATUS ANALYSIS")

        print(
            f"Not started: "
            f"{not_started}"
        )

        print(
            f"Live       : "
            f"{live}"
        )

        print(
            f"Finished   : "
            f"{finished}"
        )

        # ----------------------------------------------------
        # تحديث حالة المباراة فقط
        # ----------------------------------------------------

        if live:

            self.match_started = True

        if finished:

            self.match_finished = True

        # ----------------------------------------------------
        # مراقبة تغير النتيجة فقط
        # ----------------------------------------------------

        current_score = (
            home_score,
            away_score,
        )

        if current_score != self.previous_score:

            if self.previous_score is not None:

                print()

                print(
                    "SCORE CHANGED: "
                    f"{self.previous_score} "
                    f"-> "
                    f"{current_score}"
                )

            self.previous_score = current_score

        # ----------------------------------------------------
        # ملاحظة الأحداث بدون معالجتها
        # ----------------------------------------------------

        if incidents:

            print()
            print(
                "Incident data available:"
                f" {len(incidents)}"
            )

            print(
                "Event processing is handled "
                "by live_bot.py."
            )

        else:

            print()
            print("No incidents.")

        return {
            "home": home,
            "away": away,

            "home_score": home_score,
            "away_score": away_score,

            "status": status,
            "status_text": status_text,

            "minute": minute,

            "live": live,
            "not_started": not_started,
            "finished": finished,

            "incidents": incidents,
        }

    # ========================================================
    # Bootstrap
    # ========================================================

    def bootstrap(self):

        print()
        print("=" * 70)
        print("LIVE MATCH MANAGER — BOOTSTRAP")
        print("=" * 70)

        match = self.fetch_match()

        incidents = get_incidents(match)

        live = is_live(match)

        print(
            f"Current incidents: "
            f"{len(incidents)}"
        )

        print(
            f"Match live       : "
            f"{live}"
        )

        # ----------------------------------------------------
        # الأحداث القديمة
        # ----------------------------------------------------

        if incidents:

            self.event_manager.bootstrap(
                incidents
            )

            print(
                f"Bootstrapped "
                f"{len(incidents)} "
                f"existing incidents."
            )

        # ----------------------------------------------------
        # حفظ النتيجة الحالية
        # ----------------------------------------------------

        home_score, away_score = get_score(
            match
        )

        self.previous_score = (
            home_score,
            away_score,
        )

        if live:

            self.match_started = True

        if is_finished(match):

            self.match_finished = True

        print()
        print(
            "BOOTSTRAP COMPLETE"
        )

        return match

    # ========================================================
    # مراقبة اختيارية
    # ========================================================

    def monitor(self, max_polls=None):

        self.bootstrap()

        poll_count = 0

        print()
        print("=" * 70)
        print("LIVE MATCH MONITOR")
        print("=" * 70)

        while True:

            poll_count += 1

            try:

                match = self.fetch_match()

                result = self.inspect_match(
                    match
                )

                if result["finished"]:

                    print()
                    print(
                        "MATCH FINISHED."
                    )

                    break

            except Exception as exc:

                print()
                print(
                    f"ERROR while monitoring: "
                    f"{exc}"
                )

            if max_polls is not None:

                if poll_count >= max_polls:

                    print()
                    print(
                        "MAX POLLS REACHED."
                    )

                    break

            print()
            print(
                f"Waiting "
                f"{self.poll_interval} "
                f"seconds..."
            )

            time.sleep(
                self.poll_interval
            )


# ============================================================
# Self Test
# ============================================================

def self_test():

    print("=" * 70)
    print("LIVE MATCH MANAGER — SELF TEST")
    print("=" * 70)

    manager = LiveMatchManager(
        slug="real-betis-vs-real-madrid",
        poll_interval=1,
    )

    # ========================================================
    # TEST 1
    # ========================================================

    snapshot_1 = {

        "home": {
            "name": "Real Betis"
        },

        "away": {
            "name": "Real Madrid"
        },

        "home_score": 0,
        "away_score": 0,

        "status": "upcoming",

        "status_text": "Not started",

        "incidents": [],
    }

    print()
    print(
        "TEST 1 — NOT STARTED"
    )

    print(
        "is_not_started:",
        is_not_started(snapshot_1)
    )

    print(
        "is_live:",
        is_live(snapshot_1)
    )

    assert (
        is_not_started(snapshot_1)
        is True
    )

    assert (
        is_live(snapshot_1)
        is False
    )

    # ========================================================
    # TEST 2
    # ========================================================

    snapshot_2 = {

        "home": {
            "name": "Real Betis"
        },

        "away": {
            "name": "Real Madrid"
        },

        "home_score": 1,
        "away_score": 0,

        "status": "live",

        "status_text": "Live",

        "live_minute": 6,

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
    }

    print()
    print(
        "TEST 2 — LIVE MATCH"
    )

    print(
        "is_not_started:",
        is_not_started(snapshot_2)
    )

    print(
        "is_live:",
        is_live(snapshot_2)
    )

    print(
        "is_finished:",
        is_finished(snapshot_2)
    )

    assert (
        is_not_started(snapshot_2)
        is False
    )

    assert (
        is_live(snapshot_2)
        is True
    )

    assert (
        is_finished(snapshot_2)
        is False
    )

    result = manager.inspect_match(
        snapshot_2
    )

    assert result["live"] is True

    assert (
        result["home_score"]
        == 1
    )

    assert (
        result["away_score"]
        == 0
    )

    assert (
        len(result["incidents"])
        == 1
    )

    # ========================================================
    # TEST 3
    # ========================================================

    snapshot_3 = {

        "home": {
            "name": "Real Betis"
        },

        "away": {
            "name": "Real Madrid"
        },

        "home_score": 1,
        "away_score": 0,

        "status": "finished",

        "status_text": "Finished",

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
    }

    print()
    print(
        "TEST 3 — FINISHED"
    )

    print(
        "is_finished:",
        is_finished(snapshot_3)
    )

    print(
        "is_live:",
        is_live(snapshot_3)
    )

    assert (
        is_finished(snapshot_3)
        is True
    )

    assert (
        is_live(snapshot_3)
        is False
    )

    # ========================================================
    # النتيجة
    # ========================================================

    print()
    print("=" * 70)
    print(
        "SELF TEST PASSED"
    )
    print("=" * 70)


# ============================================================
# تشغيل الاختبار
# ============================================================

if __name__ == "__main__":

    self_test()

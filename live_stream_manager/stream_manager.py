import json
import logging
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests


BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "config.json"


# ============================================================
# CONFIGURATION
# ============================================================

def load_config():
    """Load application configuration."""

    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {CONFIG_FILE}"
        )

    with CONFIG_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


# ============================================================
# LOGGING
# ============================================================

def setup_logging(config):
    """Configure application logging."""

    output_config = config.get(
        "output",
        {}
    )

    log_directory = output_config.get(
        "log_directory",
        "logs"
    )

    log_file = output_config.get(
        "log_file",
        "stream_manager.log"
    )

    log_path = BASE_DIR / log_directory

    log_path.mkdir(
        parents=True,
        exist_ok=True
    )

    log_file_path = log_path / log_file

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(message)s"
        ),
        handlers=[
            logging.FileHandler(
                log_file_path,
                encoding="utf-8"
            ),
            logging.StreamHandler()
        ]
    )

    return logging.getLogger(
        "LiveStreamManager"
    )


# ============================================================
# HTTP HEADERS
# ============================================================

def build_headers(config):
    """Build HTTP headers from configuration."""

    header_config = config.get(
        "headers",
        {}
    )

    headers = {}

    user_agent = header_config.get(
        "User-Agent",
        ""
    ).strip()

    referer = header_config.get(
        "Referer",
        ""
    ).strip()

    if user_agent:
        headers["User-Agent"] = user_agent

    if referer:
        headers["Referer"] = referer

    return headers


# ============================================================
# URL VALIDATION
# ============================================================

def validate_stream_url(stream_url):
    """Validate basic HLS URL structure."""

    parsed = urlparse(
        stream_url
    )

    if parsed.scheme not in (
        "http",
        "https"
    ):
        return False

    if not parsed.netloc:
        return False

    if not parsed.path.lower().endswith(
        ".m3u8"
    ):
        return False

    return True


# ============================================================
# HTTP REQUEST
# ============================================================

def request_url(
    url,
    headers,
    timeout
):
    """Request a URL safely."""

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=timeout,
            allow_redirects=True
        )

        return response

    except requests.RequestException as error:

        logging.error(
            "Request failed: %s",
            error
        )

        return None


# ============================================================
# PLAYLIST URL EXTRACTION
# ============================================================

def extract_urls(
    playlist_text,
    base_url
):
    """
    Extract all non-comment URLs from an M3U8 playlist.
    """

    urls = []

    for line in playlist_text.splitlines():

        line = line.strip()

        if not line:
            continue

        if line.startswith("#"):
            continue

        urls.append(
            urljoin(
                base_url,
                line
            )
        )

    return urls


# ============================================================
# M3U8 VARIANT EXTRACTION
# ============================================================

def extract_variant_urls(
    playlist_text,
    base_url
):
    """
    Extract variant playlist URLs.

    A real master playlist normally contains:

        #EXT-X-STREAM-INF
        variant.m3u8

    This function only treats URLs following
    #EXT-X-STREAM-INF as variant playlists.
    """

    variants = []

    lines = [
        line.strip()
        for line in playlist_text.splitlines()
    ]

    for index, line in enumerate(lines):

        if not line:
            continue

        if not line.startswith(
            "#EXT-X-STREAM-INF"
        ):
            continue

        next_index = index + 1

        while next_index < len(lines):

            next_line = lines[
                next_index
            ].strip()

            if not next_line:

                next_index += 1
                continue

            if next_line.startswith("#"):

                next_index += 1
                continue

            variants.append(
                urljoin(
                    base_url,
                    next_line
                )
            )

            break

    return variants


# ============================================================
# MEDIA SEGMENT EXTRACTION
# ============================================================

def extract_segments(
    playlist_text,
    base_url
):
    """Extract media segment URLs."""

    segments = []

    for line in playlist_text.splitlines():

        line = line.strip()

        if not line:
            continue

        if line.startswith("#"):
            continue

        url = urljoin(
            base_url,
            line
        )

        lower_url = url.lower()

        if (
            lower_url.endswith(".ts")
            or ".ts?" in lower_url
            or lower_url.endswith(".m4s")
            or ".m4s?" in lower_url
        ):

            segments.append(
                url
            )

    return segments


# ============================================================
# MASTER PLAYLIST
# ============================================================

def get_master_playlist(
    stream,
    headers,
    timeout,
    logger
):
    """Download and validate the master playlist."""

    stream_id = stream["id"]
    stream_url = stream["stream_url"]

    logger.info(
        "[%s] Checking master playlist: %s",
        stream_id,
        stream_url
    )

    response = request_url(
        stream_url,
        headers,
        timeout
    )

    if response is None:

        logger.error(
            "[%s] Master request failed.",
            stream_id
        )

        return None

    logger.info(
        "[%s] Master HTTP status: %s",
        stream_id,
        response.status_code
    )

    content_type = response.headers.get(
        "Content-Type",
        "Unknown"
    )

    logger.info(
        "[%s] Master Content-Type: %s",
        stream_id,
        content_type
    )

    if response.status_code != 200:

        logger.error(
            "[%s] Master playlist unavailable.",
            stream_id
        )

        return None

    if "#EXTM3U" not in response.text:

        logger.error(
            "[%s] Response is not a valid M3U8 playlist.",
            stream_id
        )

        return None

    logger.info(
        "[%s] Master playlist OK.",
        stream_id
    )

    return response


# ============================================================
# VARIANT PLAYLIST
# ============================================================

def get_variant_playlist(
    stream,
    master_response,
    headers,
    timeout,
    logger
):
    """
    Select and download a real variant playlist.

    Some HLS sources use a non-standard structure where
    the master URL directly lists .ts media files.

    In that case this function returns None and the caller
    handles the direct media-segment playlist separately.
    """

    stream_id = stream["id"]

    variant_urls = extract_variant_urls(
        master_response.text,
        master_response.url
    )

    # --------------------------------------------------------
    # No EXT-X-STREAM-INF variants
    # --------------------------------------------------------

    if not variant_urls:

        logger.info(
            "[%s] No standard M3U8 variant playlists found.",
            stream_id
        )

        logger.info(
            "[%s] Checking whether the master directly "
            "contains media segments.",
            stream_id
        )

        direct_segments = extract_segments(
            master_response.text,
            master_response.url
        )

        if direct_segments:

            logger.info(
                "[%s] Direct media-segment playlist detected: "
                "%s segments.",
                stream_id,
                len(direct_segments)
            )

            return master_response

        logger.error(
            "[%s] No variant playlists or media segments found.",
            stream_id
        )

        return None

    # --------------------------------------------------------
    # Select preferred variant
    # --------------------------------------------------------

    preferred_variant = stream.get(
        "preferred_variant",
        1
    )

    try:

        index = int(
            preferred_variant
        ) - 1

    except (
        TypeError,
        ValueError
    ):

        index = 0

    if index < 0:
        index = 0

    if index >= len(variant_urls):
        index = 0

    variant_url = variant_urls[index]

    logger.info(
        "[%s] Selected variant %s/%s: %s",
        stream_id,
        index + 1,
        len(variant_urls),
        variant_url
    )

    response = request_url(
        variant_url,
        headers,
        timeout
    )

    if response is None:

        logger.error(
            "[%s] Variant request failed.",
            stream_id
        )

        return None

    logger.info(
        "[%s] Variant HTTP status: %s",
        stream_id,
        response.status_code
    )

    if response.status_code != 200:

        logger.error(
            "[%s] Variant playlist unavailable.",
            stream_id
        )

        return None

    if "#EXTM3U" not in response.text:

        logger.error(
            "[%s] Variant response is not a valid M3U8.",
            stream_id
        )

        return None

    logger.info(
        "[%s] Variant playlist OK.",
        stream_id
    )

    return response


# ============================================================
# MEDIA SEGMENT TEST
# ============================================================

def test_media_segments(
    stream,
    variant_response,
    headers,
    timeout,
    segment_count,
    delay,
    logger
):
    """Test actual media segments."""

    stream_id = stream["id"]

    segments = extract_segments(
        variant_response.text,
        variant_response.url
    )

    if not segments:

        logger.error(
            "[%s] No media segments found.",
            stream_id
        )

        return False

    logger.info(
        "[%s] Media segments found: %s",
        stream_id,
        len(segments)
    )

    test_segments = segments[
        :segment_count
    ]

    successful = 0

    for index, segment_url in enumerate(
        test_segments,
        start=1
    ):

        logger.info(
            "[%s] Testing segment %s/%s",
            stream_id,
            index,
            len(test_segments)
        )

        response = request_url(
            segment_url,
            headers,
            timeout
        )

        if response is None:

            logger.error(
                "[%s] Segment request failed.",
                stream_id
            )

            continue

        size = len(
            response.content
        )

        content_type = response.headers.get(
            "Content-Type",
            "Unknown"
        )

        logger.info(
            "[%s] Segment HTTP: %s | "
            "Type: %s | Bytes: %s",
            stream_id,
            response.status_code,
            content_type,
            size
        )

        if (
            response.status_code == 200
            and size > 0
        ):

            successful += 1

        if index < len(test_segments):

            time.sleep(
                delay
            )

    logger.info(
        "[%s] Successful segments: %s/%s",
        stream_id,
        successful,
        len(test_segments)
    )

    return (
        successful == len(test_segments)
    )


# ============================================================
# STREAM CHECK
# ============================================================

def check_stream(
    stream,
    headers,
    monitoring_config,
    logger
):
    """Perform a complete health check."""

    stream_id = stream["id"]

    stream_name = stream["name"]

    stream_url = stream["stream_url"]

    timeout = monitoring_config.get(
        "timeout",
        15
    )

    segment_count = monitoring_config.get(
        "segment_test_count",
        3
    )

    segment_delay = monitoring_config.get(
        "segment_test_delay",
        2
    )

    logger.info(
        "--------------------------------------------------"
    )

    logger.info(
        "Checking stream: %s",
        stream_name
    )

    logger.info(
        "Stream ID: %s",
        stream_id
    )

    logger.info(
        "Stream URL: %s",
        stream_url
    )

    # --------------------------------------------------------
    # Validate URL
    # --------------------------------------------------------

    if not validate_stream_url(
        stream_url
    ):

        logger.error(
            "[%s] Invalid HLS URL.",
            stream_id
        )

        return False

    # --------------------------------------------------------
    # Download master
    # --------------------------------------------------------

    master_response = get_master_playlist(
        stream,
        headers,
        timeout,
        logger
    )

    if master_response is None:

        logger.error(
            "[%s] STREAM OFFLINE - master failed.",
            stream_id
        )

        return False

    # --------------------------------------------------------
    # Get variant
    #
    # This function can return:
    #
    # 1. A normal variant M3U8
    #
    # OR
    #
    # 2. The original master response when the source
    #    directly contains .ts segments.
    # --------------------------------------------------------

    variant_response = get_variant_playlist(
        stream,
        master_response,
        headers,
        timeout,
        logger
    )

    if variant_response is None:

        logger.error(
            "[%s] STREAM OFFLINE - variant/media failed.",
            stream_id
        )

        return False

    # --------------------------------------------------------
    # Test media segments
    # --------------------------------------------------------

    media_ok = test_media_segments(
        stream,
        variant_response,
        headers,
        timeout,
        segment_count,
        segment_delay,
        logger
    )

    if not media_ok:

        logger.error(
            "[%s] STREAM DEGRADED - media failed.",
            stream_id
        )

        return False

    logger.info(
        "[%s] STREAM ONLINE AND HEALTHY.",
        stream_id
    )

    return True


# ============================================================
# M3U PLAYLIST
# ============================================================

def create_m3u_playlist(
    config,
    enabled_streams,
    logger
):
    """Create an M3U playlist containing healthy streams."""

    output_config = config.get(
        "output",
        {}
    )

    playlist_name = output_config.get(
        "playlist_file",
        "live_playlist.m3u"
    )

    playlist_path = BASE_DIR / playlist_name

    lines = [
        "#EXTM3U"
    ]

    header_config = config.get(
        "headers",
        {}
    )

    user_agent = header_config.get(
        "User-Agent",
        ""
    ).strip()

    referer = header_config.get(
        "Referer",
        ""
    ).strip()

    if user_agent:

        lines.append(
            f"#EXTVLCOPT:http-user-agent={user_agent}"
        )

    if referer:

        lines.append(
            f"#EXTVLCOPT:http-referrer={referer}"
        )

    for stream in enabled_streams:

        title = stream.get(
            "event_title",
            stream.get(
                "name",
                "Live Stream"
            )
        )

        stream_url = stream.get(
            "stream_url",
            ""
        ).strip()

        if not stream_url:
            continue

        lines.append(
            f"#EXTINF:-1,{title}"
        )

        lines.append(
            stream_url
        )

    playlist_path.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8"
    )

    logger.info(
        "M3U playlist created: %s",
        playlist_path
    )


# ============================================================
# SINGLE MONITORING CYCLE
# ============================================================

def monitoring_cycle(
    config,
    streams,
    headers,
    monitoring_config,
    logger,
    stream_states
):
    """Run one complete monitoring cycle."""

    healthy_streams = []

    logger.info(
        "=================================================="
    )

    logger.info(
        "STARTING MONITORING CYCLE"
    )

    logger.info(
        "Configured streams: %s",
        len(streams)
    )

    for stream in streams:

        stream_id = stream.get(
            "id",
            "unknown"
        )

        if not stream.get(
            "enabled",
            False
        ):

            logger.info(
                "[%s] Stream disabled.",
                stream_id
            )

            continue

        previous_state = stream_states.get(
            stream_id,
            {
                "status": "UNKNOWN",
                "consecutive_failures": 0
            }
        )

        start_time = time.time()

        is_healthy = check_stream(
            stream,
            headers,
            monitoring_config,
            logger
        )

        duration = time.time() - start_time

        if is_healthy:

            healthy_streams.append(
                stream
            )

            stream_states[stream_id] = {
                "status": "ONLINE",
                "consecutive_failures": 0
            }

            if previous_state["status"] != "ONLINE":

                logger.info(
                    "[%s] STATUS CHANGED: %s -> ONLINE",
                    stream_id,
                    previous_state["status"]
                )

        else:

            failures = (
                previous_state[
                    "consecutive_failures"
                ] + 1
            )

            max_failures = monitoring_config.get(
                "max_consecutive_failures",
                3
            )

            if failures >= max_failures:

                current_status = "OFFLINE"

            else:

                current_status = "DEGRADED"

            stream_states[stream_id] = {
                "status": current_status,
                "consecutive_failures": failures
            }

            logger.warning(
                "[%s] STATUS: %s | "
                "Consecutive failures: %s/%s",
                stream_id,
                current_status,
                failures,
                max_failures
            )

            if previous_state["status"] != current_status:

                logger.warning(
                    "[%s] STATUS CHANGED: %s -> %s",
                    stream_id,
                    previous_state["status"],
                    current_status
                )

        logger.info(
            "[%s] Check duration: %.2f seconds",
            stream_id,
            duration
        )

    create_m3u_playlist(
        config,
        healthy_streams,
        logger
    )

    logger.info(
        "MONITORING CYCLE FINISHED"
    )

    logger.info(
        "Healthy streams: %s/%s",
        len(healthy_streams),
        len(streams)
    )

    return healthy_streams


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("LIVE STREAM MANAGER")
    print("Version 1.3.1")
    print("=" * 70)

    try:

        config = load_config()

    except (
        FileNotFoundError,
        json.JSONDecodeError
    ) as error:

        print(
            f"\nConfiguration error: {error}"
        )

        return

    logger = setup_logging(
        config
    )

    streams = config.get(
        "streams",
        []
    )

    headers = build_headers(
        config
    )

    monitoring_config = config.get(
        "monitoring",
        {}
    )

    monitoring_enabled = monitoring_config.get(
        "enabled",
        False
    )

    if not streams:

        logger.error(
            "No streams configured."
        )

        return

    if not monitoring_enabled:

        logger.info(
            "Monitoring is disabled."
        )

        monitoring_cycle(
            config,
            streams,
            headers,
            monitoring_config,
            logger,
            {}
        )

        return

    interval_seconds = monitoring_config.get(
        "interval_seconds",
        30
    )

    logger.info(
        "Continuous monitoring enabled."
    )

    logger.info(
        "Monitoring interval: %s seconds",
        interval_seconds
    )

    stream_states = {}

    # --------------------------------------------------------
    # CI TEST MODE
    # --------------------------------------------------------

    test_cycles = 3

    logger.info(
        "CI test mode: %s monitoring cycles.",
        test_cycles
    )

    for cycle_number in range(
        1,
        test_cycles + 1
    ):

        print(
            f"\nMonitoring cycle "
            f"{cycle_number}/{test_cycles}"
        )

        logger.info(
            "MONITORING CYCLE %s/%s",
            cycle_number,
            test_cycles
        )

        monitoring_cycle(
            config,
            streams,
            headers,
            monitoring_config,
            logger,
            stream_states
        )

        if cycle_number < test_cycles:

            logger.info(
                "Waiting %s seconds before next cycle.",
                interval_seconds
            )

            time.sleep(
                interval_seconds
            )

    print("\n")
    print("=" * 70)
    print("MONITORING TEST FINISHED")
    print("=" * 70)

    print(
        f"\nMonitoring cycles completed: {test_cycles}"
    )

    print(
        "\nFinal stream states:"
    )

    for stream_id, state in stream_states.items():

        print(
            f"- {stream_id}: "
            f"{state['status']} "
            f"(failures: "
            f"{state['consecutive_failures']})"
        )

    print(
        "\nLive Stream Manager finished."
    )


if __name__ == "__main__":
    main()

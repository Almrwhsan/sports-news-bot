import json
import logging
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
    """Extract non-comment URLs from an M3U8 playlist."""

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
    timeout
):
    """Download and validate the master playlist."""

    stream_id = stream["id"]
    stream_name = stream["name"]
    stream_url = stream["stream_url"]

    logging.info(
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

        logging.error(
            "[%s] Master request failed.",
            stream_id
        )

        return None

    logging.info(
        "[%s] Master HTTP status: %s",
        stream_id,
        response.status_code
    )

    if response.status_code != 200:

        logging.error(
            "[%s] Master playlist unavailable.",
            stream_id
        )

        return None

    content_type = response.headers.get(
        "Content-Type",
        "Unknown"
    )

    logging.info(
        "[%s] Master Content-Type: %s",
        stream_id,
        content_type
    )

    if "#EXTM3U" not in response.text:

        logging.error(
            "[%s] Response is not a valid M3U8 playlist.",
            stream_id
        )

        return None

    logging.info(
        "[%s] Master playlist OK.",
        stream_name
    )

    return response


# ============================================================
# VARIANT PLAYLIST
# ============================================================

def get_variant_playlist(
    stream,
    master_response,
    headers,
    timeout
):
    """Select and download a variant playlist."""

    stream_id = stream["id"]

    variant_urls = extract_urls(
        master_response.text,
        master_response.url
    )

    if not variant_urls:

        logging.error(
            "[%s] No variant playlists found.",
            stream_id
        )

        return None

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

    logging.info(
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

        logging.error(
            "[%s] Variant request failed.",
            stream_id
        )

        return None

    logging.info(
        "[%s] Variant HTTP status: %s",
        stream_id,
        response.status_code
    )

    if response.status_code != 200:

        logging.error(
            "[%s] Variant playlist unavailable.",
            stream_id
        )

        return None

    if "#EXTM3U" not in response.text:

        logging.error(
            "[%s] Variant is not a valid M3U8.",
            stream_id
        )

        return None

    logging.info(
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
    delay
):
    """Test actual media segments."""

    stream_id = stream["id"]

    segments = extract_segments(
        variant_response.text,
        variant_response.url
    )

    if not segments:

        logging.error(
            "[%s] No media segments found.",
            stream_id
        )

        return False

    logging.info(
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

        logging.info(
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

            logging.error(
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

        logging.info(
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

            import time

            time.sleep(
                delay
            )

    logging.info(
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
        "=================================================="
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

    if not validate_stream_url(
        stream_url
    ):

        logger.error(
            "[%s] Invalid HLS URL.",
            stream_id
        )

        return False

    master_response = get_master_playlist(
        stream,
        headers,
        timeout
    )

    if master_response is None:

        logger.error(
            "[%s] STREAM OFFLINE - master failed.",
            stream_id
        )

        return False

    variant_response = get_variant_playlist(
        stream,
        master_response,
        headers,
        timeout
    )

    if variant_response is None:

        logger.error(
            "[%s] STREAM OFFLINE - variant failed.",
            stream_id
        )

        return False

    media_ok = test_media_segments(
        stream,
        variant_response,
        headers,
        timeout,
        segment_count,
        segment_delay
    )

    if not media_ok:

        logger.error(
            "[%s] STREAM UNHEALTHY - media failed.",
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
    enabled_streams
):
    """Create an M3U playlist containing enabled streams."""

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

    logging.info(
        "M3U playlist created: %s",
        playlist_path
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("LIVE STREAM MANAGER")
    print("Version 1.0.0")
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

    if not streams:

        logger.error(
            "No streams configured."
        )

        return

    logger.info(
        "Configured streams: %s",
        len(streams)
    )

    healthy_streams = []

    for stream in streams:

        if not stream.get(
            "enabled",
            False
        ):

            logger.info(
                "[%s] Stream disabled.",
                stream.get(
                    "id",
                    "unknown"
                )
            )

            continue

        is_healthy = check_stream(
            stream,
            headers,
            monitoring_config,
            logger
        )

        if is_healthy:

            healthy_streams.append(
                stream
            )

    create_m3u_playlist(
        config,
        healthy_streams
    )

    print("\n")
    print("=" * 70)
    print("FINAL RESULT")
    print("=" * 70)

    print(
        f"\nConfigured streams: {len(streams)}"
    )

    print(
        f"Healthy streams: {len(healthy_streams)}"
    )

    if healthy_streams:

        print(
            "\nONLINE:"
        )

        for stream in healthy_streams:

            print(
                f"- {stream['name']}"
            )

        print(
            "\nLive playlist has been generated."
        )

    else:

        print(
            "\nNo healthy streams found."
        )

        print(
            "The generated playlist contains no "
            "healthy stream."
        )

    print(
        "\nLive Stream Manager finished."
    )


if __name__ == "__main__":
    main()

import json
import time
from pathlib import Path
from urllib.parse import urlparse, urljoin

import requests


BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "config.json"


def load_config():
    """Load configuration from config.json."""
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {CONFIG_FILE}"
        )

    with CONFIG_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def validate_stream_url(stream_url):
    """Validate the basic structure of the HLS URL."""
    parsed = urlparse(stream_url)

    if parsed.scheme not in ("http", "https"):
        return False

    if not parsed.netloc:
        return False

    if not parsed.path.lower().endswith(".m3u8"):
        return False

    return True


def build_headers(config):
    """Build HTTP headers from config.json."""
    header_config = config.get("headers", {})

    headers = {}

    user_agent = header_config.get("User-Agent", "").strip()
    referer = header_config.get("Referer", "").strip()

    if user_agent:
        headers["User-Agent"] = user_agent

    if referer:
        headers["Referer"] = referer

    return headers


def extract_playlist_urls(playlist_text, base_url):
    """
    Extract URLs from an HLS playlist.

    This function ignores comments and returns
    absolute URLs.
    """
    urls = []

    for line in playlist_text.splitlines():
        line = line.strip()

        if not line:
            continue

        if line.startswith("#"):
            continue

        full_url = urljoin(base_url, line)

        urls.append(full_url)

    return urls


def extract_segment_urls(playlist_text, base_url):
    """
    Extract media segment URLs from a media playlist.

    Only URLs ending with common media segment extensions
    are returned.
    """
    segments = []

    for line in playlist_text.splitlines():
        line = line.strip()

        if not line:
            continue

        if line.startswith("#"):
            continue

        full_url = urljoin(base_url, line)

        lower_url = full_url.lower()

        if (
            lower_url.endswith(".ts")
            or ".ts?" in lower_url
            or lower_url.endswith(".m4s")
            or ".m4s?" in lower_url
        ):
            segments.append(full_url)

    return segments


def print_response_info(name, response):
    """Print useful HTTP response information."""
    print(f"\n{name} HTTP Status: {response.status_code}")

    print(
        f"{name} Content-Type: "
        f"{response.headers.get('Content-Type', 'Unknown')}"
    )

    print(
        f"{name} Content-Length: "
        f"{response.headers.get('Content-Length', 'Unknown')}"
    )

    print(
        f"{name} Final URL: "
        f"{response.url}"
    )


def request_url(url, headers):
    """Perform a GET request safely."""
    try:
        return requests.get(
            url,
            headers=headers,
            timeout=15,
            allow_redirects=True
        )

    except requests.RequestException as error:
        print(f"\nRequest error:")
        print(error)

        return None


def test_master_playlist(stream_url, headers):
    """Test the main/master HLS playlist."""

    print("\n")
    print("=" * 70)
    print("STEP 1 - MASTER PLAYLIST")
    print("=" * 70)

    print("\nMaster URL:")
    print(stream_url)

    response = request_url(
        stream_url,
        headers
    )

    if response is None:
        return None

    print_response_info(
        "Master",
        response
    )

    if response.status_code != 200:
        print(
            "\nMaster Playlist FAILED."
        )

        return None

    print(
        "\nMaster Playlist: SUCCESS"
    )

    print("\nMaster content:")

    for line in response.text.splitlines():
        line = line.strip()

        if line:
            print(line)

    return response


def test_variant_playlist(master_response, headers):
    """Find and test the first variant playlist."""

    print("\n")
    print("=" * 70)
    print("STEP 2 - VARIANT PLAYLIST")
    print("=" * 70)

    variant_urls = extract_playlist_urls(
        master_response.text,
        master_response.url
    )

    print(
        f"\nVariant playlists found: "
        f"{len(variant_urls)}"
    )

    if not variant_urls:
        print(
            "\nNo variant playlist was found."
        )

        return None

    for index, url in enumerate(
        variant_urls,
        start=1
    ):
        print(
            f"{index}. {url}"
        )

    variant_url = variant_urls[0]

    print("\nTesting first variant:")
    print(variant_url)

    response = request_url(
        variant_url,
        headers
    )

    if response is None:
        return None

    print_response_info(
        "Variant",
        response
    )

    if response.status_code != 200:
        print(
            "\nVariant Playlist FAILED."
        )

        return None

    print(
        "\nVariant Playlist: SUCCESS"
    )

    print("\nVariant content:")

    for line in response.text.splitlines():
        line = line.strip()

        if line:
            print(line)

    return response


def test_media_segments(variant_response, headers):
    """
    Extract media segments from the variant playlist
    and test actual media segment downloads.
    """

    print("\n")
    print("=" * 70)
    print("STEP 3 - MEDIA SEGMENTS")
    print("=" * 70)

    segment_urls = extract_segment_urls(
        variant_response.text,
        variant_response.url
    )

    print(
        f"\nMedia segments found: "
        f"{len(segment_urls)}"
    )

    if not segment_urls:
        print(
            "\nNo .ts or .m4s media segments were found."
        )

        return False

    print("\nFirst available segments:")

    for index, url in enumerate(
        segment_urls[:5],
        start=1
    ):
        print(
            f"{index}. {url}"
        )

    print("\nTesting first media segment...")

    first_segment = segment_urls[0]

    print("\nSegment URL:")
    print(first_segment)

    response = request_url(
        first_segment,
        headers
    )

    if response is None:
        return False

    print_response_info(
        "Segment",
        response
    )

    content_length = len(response.content)

    print(
        f"Segment downloaded bytes: "
        f"{content_length}"
    )

    if response.status_code != 200:
        print(
            "\nMedia Segment FAILED."
        )

        return False

    if content_length == 0:
        print(
            "\nMedia Segment returned zero bytes."
        )

        return False

    print(
        "\nMedia Segment: SUCCESS"
    )

    print(
        "Actual media data was successfully downloaded."
    )

    return True


def test_multiple_segments(
    variant_response,
    headers
):
    """
    Test several media segments to verify that the
    stream is continuously accessible.
    """

    print("\n")
    print("=" * 70)
    print("STEP 4 - MULTIPLE SEGMENT TEST")
    print("=" * 70)

    segment_urls = extract_segment_urls(
        variant_response.text,
        variant_response.url
    )

    if len(segment_urls) < 3:
        print(
            "\nNot enough segments for the multiple-segment test."
        )

        return

    test_segments = segment_urls[:3]

    successful = 0

    for index, segment_url in enumerate(
        test_segments,
        start=1
    ):
        print("\n")
        print(
            f"Testing segment {index}/3..."
        )

        print(segment_url)

        response = request_url(
            segment_url,
            headers
        )

        if response is None:
            print(
                "Segment request failed."
            )

            continue

        print(
            f"HTTP Status: "
            f"{response.status_code}"
        )

        print(
            f"Content-Type: "
            f"{response.headers.get('Content-Type', 'Unknown')}"
        )

        size = len(response.content)

        print(
            f"Downloaded bytes: {size}"
        )

        if response.status_code == 200 and size > 0:
            print(
                "Segment: SUCCESS"
            )

            successful += 1

        else:
            print(
                "Segment: FAILED"
            )

        if index < len(test_segments):
            print(
                "\nWaiting 2 seconds..."
            )

            time.sleep(2)

    print("\n")
    print(
        f"Successful segments: "
        f"{successful}/{len(test_segments)}"
    )

    if successful == len(test_segments):
        print(
            "Multiple media segments are accessible."
        )

    else:
        print(
            "One or more media segments failed."
        )


def create_m3u_playlist(config):
    """Create the generated M3U playlist."""

    stream_config = config.get(
        "stream",
        {}
    )

    output_config = config.get(
        "output",
        {}
    )

    header_config = config.get(
        "headers",
        {}
    )

    stream_url = stream_config.get(
        "stream_url",
        ""
    ).strip()

    event_title = stream_config.get(
        "event_title",
        "Live Stream"
    ).strip()

    playlist_name = output_config.get(
        "playlist_file",
        "live_playlist.m3u"
    ).strip()

    playlist_path = BASE_DIR / playlist_name

    user_agent = header_config.get(
        "User-Agent",
        ""
    ).strip()

    referer = header_config.get(
        "Referer",
        ""
    ).strip()

    lines = [
        "#EXTM3U"
    ]

    if user_agent:
        lines.append(
            f"#EXTVLCOPT:http-user-agent={user_agent}"
        )

    if referer:
        lines.append(
            f"#EXTVLCOPT:http-referrer={referer}"
        )

    lines.append(
        f"#EXTINF:-1,{event_title}"
    )

    lines.append(
        stream_url
    )

    playlist_path.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8"
    )

    print(
        f"\nPlaylist created: "
        f"{playlist_path}"
    )


def main():

    print("=" * 70)
    print("Live Stream Manager")
    print("Full HLS Diagnostic Test")
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

    stream_config = config.get(
        "stream",
        {}
    )

    stream_url = stream_config.get(
        "stream_url",
        ""
    ).strip()

    event_title = stream_config.get(
        "event_title",
        "Live Stream"
    ).strip()

    enabled = stream_config.get(
        "enabled",
        False
    )

    status = stream_config.get(
        "status",
        "unknown"
    )

    print(
        f"\nEvent: {event_title}"
    )

    print(
        f"Status: {status}"
    )

    print(
        f"Enabled: {enabled}"
    )

    if not enabled:

        print(
            "\nStream is disabled in config.json."
        )

        return

    if not stream_url:

        print(
            "\nNo stream URL configured."
        )

        return

    if not validate_stream_url(stream_url):

        print(
            "\nInvalid HLS/M3U8 URL."
        )

        return

    headers = build_headers(
        config
    )

    print(
        "\nConfigured headers:"
    )

    if headers:

        for key in headers:
            print(
                f"- {key}"
            )

    else:

        print(
            "- None"
        )

    # -------------------------------------------------
    # STEP 1
    # -------------------------------------------------

    master_response = test_master_playlist(
        stream_url,
        headers
    )

    if master_response is None:

        print(
            "\nHLS test stopped at Master Playlist."
        )

        return

    # -------------------------------------------------
    # STEP 2
    # -------------------------------------------------

    variant_response = test_variant_playlist(
        master_response,
        headers
    )

    if variant_response is None:

        print(
            "\nHLS test stopped at Variant Playlist."
        )

        return

    # -------------------------------------------------
    # STEP 3
    # -------------------------------------------------

    segment_success = test_media_segments(
        variant_response,
        headers
    )

    # -------------------------------------------------
    # STEP 4
    # -------------------------------------------------

    if segment_success:

        test_multiple_segments(
            variant_response,
            headers
        )

    # -------------------------------------------------
    # CREATE PLAYLIST
    # -------------------------------------------------

    create_m3u_playlist(
        config
    )

    # -------------------------------------------------
    # FINAL RESULT
    # -------------------------------------------------

    print("\n")
    print("=" * 70)
    print("FINAL HLS TEST RESULT")
    print("=" * 70)

    if segment_success:

        print(
            "\nSUCCESS:"
        )

        print(
            "Master Playlist: OK"
        )

        print(
            "Variant Playlist: OK"
        )

        print(
            "Media Segment: OK"
        )

        print(
            "\nThe HLS stream is providing actual media data."
        )

        print(
            "The next step can be playback testing."
        )

    else:

        print(
            "\nPARTIAL SUCCESS:"
        )

        print(
            "Master Playlist: OK"
        )

        print(
            "Variant Playlist: OK"
        )

        print(
            "Media Segment: FAILED"
        )

        print(
            "\nFurther investigation of the media segments "
            "is required."
        )

    print(
        "\nFull HLS diagnostic test completed."
    )


if __name__ == "__main__":
    main()

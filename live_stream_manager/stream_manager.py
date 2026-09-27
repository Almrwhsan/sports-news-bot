import json
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
    """Validate the basic structure of the stream URL."""
    parsed = urlparse(stream_url)

    if parsed.scheme not in ("http", "https"):
        return False

    if not parsed.netloc:
        return False

    if not parsed.path.lower().endswith(".m3u8"):
        return False

    return True


def build_headers(config):
    """Build HTTP headers from the configured values."""
    header_config = config.get("headers", {})

    headers = {}

    user_agent = header_config.get("User-Agent", "").strip()
    referer = header_config.get("Referer", "").strip()

    if user_agent:
        headers["User-Agent"] = user_agent

    if referer:
        headers["Referer"] = referer

    return headers


def print_response_headers(response):
    """Print useful HTTP response headers."""
    print("\nImportant response headers:")

    important_headers = [
        "Content-Type",
        "Content-Length",
        "Cache-Control",
        "Access-Control-Allow-Origin",
        "Server",
        "Location"
    ]

    for header_name in important_headers:
        value = response.headers.get(header_name)

        if value is not None:
            print(f"- {header_name}: {value}")


def extract_playlist_urls(playlist_text, base_url):
    """Extract child playlist URLs from a Master Playlist."""
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


def request_playlist(url, headers, test_name):
    """Request an HLS playlist and display diagnostic information."""
    print("\n" + "-" * 60)
    print(test_name)
    print("-" * 60)

    print(f"Request URL: {url}")

    if headers:
        print("Request headers:")

        for key, value in headers.items():
            if key.lower() == "user-agent":
                print(f"- {key}: {value}")
            elif key.lower() == "referer":
                print(f"- {key}: {value}")
    else:
        print("Request headers: None")

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=15,
            allow_redirects=True
        )

        print(f"\nHTTP Status: {response.status_code}")

        print(
            f"Content-Type: "
            f"{response.headers.get('Content-Type', 'Unknown')}"
        )

        print(f"Final URL: {response.url}")

        print_response_headers(response)

        if response.status_code == 200:
            print("\nResult: SUCCESS")

            content = response.text

            print("\nFirst 500 characters of response:")

            preview = content[:500].replace("\r", "")
            print(preview)

            return response

        if response.status_code == 403:
            print("\nResult: HTTP 403 Forbidden")
            print(
                "The server refused the request."
            )

            return response

        if response.status_code == 404:
            print("\nResult: HTTP 404 Not Found")
            print(
                "The requested playlist was not found."
            )

            return response

        print(
            f"\nResult: HTTP {response.status_code}"
        )

        return response

    except requests.RequestException as error:
        print(f"\nRequest error: {error}")
        return None


def test_master_playlist(stream_url, headers):
    """Test the Master Playlist using different header configurations."""

    print("\n" + "=" * 60)
    print("MASTER PLAYLIST TEST")
    print("=" * 60)

    # Test 1: configured headers
    response_with_headers = request_playlist(
        stream_url,
        headers,
        "TEST 1 - Master Playlist with configured headers"
    )

    # Test 2: no headers
    response_without_headers = request_playlist(
        stream_url,
        {},
        "TEST 2 - Master Playlist without headers"
    )

    # Prefer the successful response from the configured-header test.
    if (
        response_with_headers is not None
        and response_with_headers.status_code == 200
    ):
        return response_with_headers

    # Otherwise use the successful no-header response.
    if (
        response_without_headers is not None
        and response_without_headers.status_code == 200
    ):
        return response_without_headers

    return None


def test_variant_playlist(master_response, headers):
    """Extract and test the first Variant Playlist."""

    print("\n" + "=" * 60)
    print("VARIANT PLAYLIST TEST")
    print("=" * 60)

    if master_response is None:
        print(
            "Cannot test Variant Playlist because "
            "Master Playlist request failed."
        )
        return

    master_text = master_response.text

    variant_urls = extract_playlist_urls(
        master_text,
        master_response.url
    )

    print(
        f"\nChild playlist URLs found: "
        f"{len(variant_urls)}"
    )

    if not variant_urls:
        print(
            "No child playlist URLs were found "
            "inside the Master Playlist."
        )
        return

    for index, variant_url in enumerate(
        variant_urls,
        start=1
    ):
        print(f"{index}. {variant_url}")

    first_variant_url = variant_urls[0]

    # Test 3: Variant with configured headers
    variant_with_headers = request_playlist(
        first_variant_url,
        headers,
        "TEST 3 - Variant Playlist with configured headers"
    )

    # Test 4: Variant without headers
    variant_without_headers = request_playlist(
        first_variant_url,
        {},
        "TEST 4 - Variant Playlist without headers"
    )

    print("\n" + "=" * 60)
    print("VARIANT TEST SUMMARY")
    print("=" * 60)

    if (
        variant_with_headers is not None
        and variant_with_headers.status_code == 200
    ):
        print(
            "Configured headers → Variant: SUCCESS"
        )
    else:
        print(
            "Configured headers → Variant: FAILED"
        )

    if (
        variant_without_headers is not None
        and variant_without_headers.status_code == 200
    ):
        print(
            "No headers → Variant: SUCCESS"
        )
    else:
        print(
            "No headers → Variant: FAILED"
        )


def check_hls_stream(stream_url, headers):
    """Run complete HLS diagnostic tests."""

    master_response = test_master_playlist(
        stream_url,
        headers
    )

    test_variant_playlist(
        master_response,
        headers
    )


def create_m3u_playlist(config):
    """Create the M3U playlist file."""
    stream_config = config.get("stream", {})
    output_config = config.get("output", {})
    header_config = config.get("headers", {})

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

    lines.append(stream_url)

    playlist_path.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8"
    )

    print(
        f"\nPlaylist created: {playlist_path}"
    )


def main():
    print("=" * 60)
    print("Live Stream Manager")
    print("=" * 60)

    try:
        config = load_config()

    except (
        FileNotFoundError,
        json.JSONDecodeError
    ) as error:

        print(
            f"Configuration error: {error}"
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

    print(f"\nEvent: {event_title}")
    print(f"Status: {status}")
    print(f"Enabled: {enabled}")

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

    headers = build_headers(config)

    print("\nConfigured headers:")

    if headers:
        for key in headers:
            print(f"- {key}")
    else:
        print("- None")

    check_hls_stream(
        stream_url,
        headers
    )

    create_m3u_playlist(config)

    print("\n" + "=" * 60)
    print("Diagnostic test completed.")
    print("=" * 60)


if __name__ == "__main__":
    main()

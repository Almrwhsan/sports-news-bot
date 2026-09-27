import json
from pathlib import Path
from urllib.parse import urlparse

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


def check_hls_stream(stream_url, headers):
    """Check whether the HLS URL can be reached."""
    print("\nChecking HLS stream...")
    print(f"URL: {stream_url}")

    try:
        response = requests.get(
            stream_url,
            headers=headers,
            timeout=15,
            allow_redirects=True
        )

        print(f"HTTP Status: {response.status_code}")
        print(
            f"Content-Type: "
            f"{response.headers.get('Content-Type', 'Unknown')}"
        )

        print(f"Final URL: {response.url}")

        if response.status_code == 200:
            print("HLS request succeeded.")

            content_preview = response.text[:200].replace("\n", " ")
            print(f"Response preview: {content_preview}")

            return True

        if response.status_code == 403:
            print(
                "HTTP 403 Forbidden: "
                "the server refused the request."
            )
            print(
                "Only use headers explicitly provided by "
                "the authorized stream provider."
            )
            return False

        print("HLS request did not return HTTP 200.")
        return False

    except requests.RequestException as error:
        print(f"Connection error: {error}")
        return False


def create_m3u_playlist(config):
    """Create the M3U playlist file."""
    stream_config = config.get("stream", {})
    output_config = config.get("output", {})
    header_config = config.get("headers", {})

    stream_url = stream_config.get("stream_url", "").strip()
    event_title = stream_config.get(
        "event_title",
        "Live Stream"
    ).strip()

    playlist_name = output_config.get(
        "playlist_file",
        "live_playlist.m3u"
    ).strip()

    playlist_path = BASE_DIR / playlist_name

    user_agent = header_config.get("User-Agent", "").strip()
    referer = header_config.get("Referer", "").strip()

    lines = [
        "#EXTM3U"
    ]

    if user_agent:
        lines.append(f'#EXTVLCOPT:http-user-agent={user_agent}')

    if referer:
        lines.append(f'#EXTVLCOPT:http-referrer={referer}')

    lines.append(f"#EXTINF:-1,{event_title}")
    lines.append(stream_url)

    playlist_path.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8"
    )

    print(f"\nPlaylist created: {playlist_path}")


def main():
    print("=" * 50)
    print("Live Stream Manager")
    print("=" * 50)

    try:
        config = load_config()
    except (FileNotFoundError, json.JSONDecodeError) as error:
        print(f"Configuration error: {error}")
        return

    stream_config = config.get("stream", {})

    stream_url = stream_config.get("stream_url", "").strip()
    event_title = stream_config.get(
        "event_title",
        "Live Stream"
    ).strip()

    enabled = stream_config.get("enabled", False)
    status = stream_config.get("status", "unknown")

    print(f"\nEvent: {event_title}")
    print(f"Status: {status}")
    print(f"Enabled: {enabled}")

    if not enabled:
        print("\nStream is disabled in config.json.")
        return

    if not stream_url:
        print("\nNo stream URL configured.")
        return

    if not validate_stream_url(stream_url):
        print("\nInvalid HLS/M3U8 URL.")
        return

    headers = build_headers(config)

    print("\nConfigured headers:")
    if headers:
        for key in headers:
            print(f"- {key}")
    else:
        print("- None")

    check_hls_stream(stream_url, headers)

    create_m3u_playlist(config)

    print("\nDone.")
    print(
        "You can now test the generated "
        "live_playlist.m3u with VLC."
    )


if __name__ == "__main__":
    main()

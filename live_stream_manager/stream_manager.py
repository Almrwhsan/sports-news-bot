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


def check_variant_playlist(variant_url, headers):
    """Check the first child/media playlist."""
    print("\nChecking first child playlist...")
    print(f"Variant URL: {variant_url}")

    try:
        response = requests.get(
            variant_url,
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
            print("Child playlist request succeeded.")

            lines = response.text.splitlines()

            print("\nChild playlist preview:")

            shown = 0

            for line in lines:
                line = line.strip()

                if not line:
                    continue

                print(line)

                shown += 1

                if shown >= 20:
                    print("... preview limited to 20 lines ...")
                    break

            return True

        if response.status_code == 403:
            print(
                "HTTP 403 Forbidden: "
                "the server refused the child playlist request."
            )
            return False

        print("Child playlist did not return HTTP 200.")
        return False

    except requests.RequestException as error:
        print(f"Child playlist connection error: {error}")
        return False


def check_hls_stream(stream_url, headers):
    """Check the Master HLS playlist and its first child playlist."""
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
            print("HLS Master Playlist request succeeded.")

            print("\nMaster Playlist:")

            master_lines = response.text.splitlines()

            for line in master_lines:
                line = line.strip()

                if line:
                    print(line)

            variant_urls = extract_playlist_urls(
                response.text,
                response.url
            )

            print(
                f"\nChild playlist URLs found: "
                f"{len(variant_urls)}"
            )

            if variant_urls:
                for index, variant_url in enumerate(
                    variant_urls,
                    start=1
                ):
                    print(f"{index}. {variant_url}")

                check_variant_playlist(
                    variant_urls[0],
                    headers
                )

            else:
                print(
                    "No child playlist URLs were found "
                    "inside the Master Playlist."
                )

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
        lines.append(
            f'#EXTVLCOPT:http-user-agent={user_agent}'
        )

    if referer:
        lines.append(
            f'#EXTVLCOPT:http-referrer={referer}'
        )

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

    check_hls_stream(
        stream_url,
        headers
    )

    create_m3u_playlist(config)

    print("\nDone.")
    print(
        "Diagnostic test completed."
    )


if __name__ == "__main__":
    main()

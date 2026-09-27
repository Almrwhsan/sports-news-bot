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


def extract_child_urls(playlist_text, base_url):
    """Extract non-comment URLs from an M3U8 playlist."""
    urls = []

    for line in playlist_text.splitlines():
        line = line.strip()

        if not line:
            continue

        if line.startswith("#"):
            continue

        urls.append(
            urljoin(base_url, line)
        )

    return urls


def test_once(stream_url, headers, attempt_number):
    """Perform one complete Master -> Variant test."""

    print("\n")
    print("=" * 70)
    print(f"ATTEMPT {attempt_number}")
    print("=" * 70)

    print("\nMaster URL:")
    print(stream_url)

    try:
        master_response = requests.get(
            stream_url,
            headers=headers,
            timeout=15,
            allow_redirects=True
        )

    except requests.RequestException as error:
        print(f"\nMaster request error: {error}")
        return None, None

    print(
        f"\nMaster HTTP Status: "
        f"{master_response.status_code}"
    )

    print(
        f"Master Content-Type: "
        f"{master_response.headers.get('Content-Type', 'Unknown')}"
    )

    print(
        f"Master Final URL: "
        f"{master_response.url}"
    )

    if master_response.status_code != 200:
        print(
            "\nMaster Playlist FAILED."
        )

        return None, None

    print(
        "\nMaster Playlist: SUCCESS"
    )

    print("\nMaster content:")

    for line in master_response.text.splitlines():
        line = line.strip()

        if line:
            print(line)

    child_urls = extract_child_urls(
        master_response.text,
        master_response.url
    )

    print(
        f"\nChild URLs found: {len(child_urls)}"
    )

    if not child_urls:
        print(
            "No child playlist URL was found."
        )

        return master_response, None

    for index, child_url in enumerate(
        child_urls,
        start=1
    ):
        print(
            f"{index}. {child_url}"
        )

    variant_url = child_urls[0]

    print("\nTesting first child playlist...")

    try:
        variant_response = requests.get(
            variant_url,
            headers=headers,
            timeout=15,
            allow_redirects=True
        )

    except requests.RequestException as error:
        print(
            f"\nVariant request error: {error}"
        )

        return master_response, variant_url

    print(
        f"\nVariant HTTP Status: "
        f"{variant_response.status_code}"
    )

    print(
        f"Variant Content-Type: "
        f"{variant_response.headers.get('Content-Type', 'Unknown')}"
    )

    print(
        f"Variant Final URL: "
        f"{variant_response.url}"
    )

    if variant_response.status_code == 200:
        print(
            "\nVariant Playlist: SUCCESS"
        )

        print("\nVariant content preview:")

        print(
            variant_response.text[:1000]
        )

    elif variant_response.status_code == 404:
        print(
            "\nVariant Playlist: 404 NOT FOUND"
        )

    else:
        print(
            f"\nVariant Playlist FAILED "
            f"with HTTP {variant_response.status_code}"
        )

    return master_response, variant_url


def run_repeated_test(stream_url, headers):
    """Run the same Master -> Variant test three times."""

    results = []

    previous_variant_url = None

    for attempt in range(1, 4):

        master_response, variant_url = test_once(
            stream_url,
            headers,
            attempt
        )

        variant_status = None

        if variant_url:

            try:
                response = requests.get(
                    variant_url,
                    headers=headers,
                    timeout=15,
                    allow_redirects=True
                )

                variant_status = response.status_code

            except requests.RequestException:
                variant_status = "ERROR"

        results.append(
            {
                "attempt": attempt,
                "master_status": (
                    master_response.status_code
                    if master_response
                    else "ERROR"
                ),
                "variant_url": variant_url,
                "variant_status": variant_status
            }
        )

        if previous_variant_url is not None:

            if variant_url == previous_variant_url:
                print(
                    "\nVariant URL is the same as "
                    "the previous attempt."
                )
            else:
                print(
                    "\nVariant URL changed from "
                    "the previous attempt."
                )

        previous_variant_url = variant_url

        if attempt < 3:
            print(
                "\nWaiting 3 seconds before "
                "the next attempt..."
            )

            time.sleep(3)

    print("\n")
    print("=" * 70)
    print("FINAL COMPARISON")
    print("=" * 70)

    for result in results:

        print(
            f"\nAttempt {result['attempt']}:"
        )

        print(
            f"- Master HTTP: "
            f"{result['master_status']}"
        )

        print(
            f"- Variant HTTP: "
            f"{result['variant_status']}"
        )

        print(
            f"- Variant URL: "
            f"{result['variant_url']}"
        )

    print("\n")
    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)

    all_master_ok = all(
        result["master_status"] == 200
        for result in results
    )

    all_variant_404 = all(
        result["variant_status"] == 404
        for result in results
    )

    variant_urls = [
        result["variant_url"]
        for result in results
    ]

    same_variant = (
        len(set(variant_urls)) == 1
        and variant_urls[0] is not None
    )

    if all_master_ok and all_variant_404 and same_variant:

        print(
            "\nRESULT:"
        )

        print(
            "Master Playlist consistently returns HTTP 200."
        )

        print(
            "The same Variant Playlist consistently "
            "returns HTTP 404."
        )

        print(
            "\nThis strongly indicates that the current "
            "test stream URL is not providing a usable "
            "child/media playlist at the moment."
        )

    elif all_master_ok:

        print(
            "\nRESULT:"
        )

        print(
            "The Master Playlist is reachable, but the "
            "Variant behavior is not consistently 404."
        )

        print(
            "Further HLS investigation is required."
        )

    else:

        print(
            "\nRESULT:"
        )

        print(
            "The Master Playlist itself was not consistently "
            "reachable."
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
        f"\nPlaylist created: {playlist_path}"
    )


def main():
    print("=" * 70)
    print("Live Stream Manager")
    print("Repeated HLS Diagnostic Test")
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

    headers = build_headers(config)

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

    run_repeated_test(
        stream_url,
        headers
    )

    create_m3u_playlist(
        config
    )

    print("\n")
    print("=" * 70)
    print("Repeated diagnostic test completed.")
    print("=" * 70)


if __name__ == "__main__":
    main()

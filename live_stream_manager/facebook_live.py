
import json
import os
import subprocess
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "config.json"


def load_config():
    with CONFIG_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def main():
    print("=" * 70)
    print("FACEBOOK LIVE TEST")
    print("=" * 70)

    config = load_config()

    streams = config.get("streams", [])

    if not streams:
        print("ERROR: No streams configured.")
        return

    stream = next(
        (item for item in streams if item.get("enabled", False)),
        None
    )

    if not stream:
        print("ERROR: No enabled stream found.")
        return

    hls_url = stream.get("stream_url")

    rtmps_url = os.getenv("FACEBOOK_RTMPS_URL")
    stream_key = os.getenv("FACEBOOK_STREAM_KEY")

    if not hls_url:
        print("ERROR: HLS stream URL is missing.")
        return

    if not rtmps_url:
        print("ERROR: FACEBOOK_RTMPS_URL secret is missing.")
        return

    if not stream_key:
        print("ERROR: FACEBOOK_STREAM_KEY secret is missing.")
        return

    # Remove accidental trailing slash from Server URL.
    rtmps_url = rtmps_url.rstrip("/")

    facebook_url = f"{rtmps_url}/{stream_key}"

    print("\nSource HLS:")
    print(hls_url)

    print("\nFacebook RTMPS:")
    print(rtmps_url)

    print("\nStream key:")
    print("[HIDDEN]")

    print("\nStarting FFmpeg...")
    print("Test duration: 60 seconds")

    command = [
        "ffmpeg",

        "-hide_banner",

        "-reconnect", "1",
        "-reconnect_streamed", "1",
        "-reconnect_delay_max", "5",

        "-i", hls_url,

        "-t", "60",

        "-c", "copy",

        "-f", "flv",

        facebook_url
    ]

    print("\nFFmpeg command:")
    print("ffmpeg ... [STREAM KEY HIDDEN]")

    result = subprocess.run(command)

    print("\n" + "=" * 70)

    if result.returncode == 0:
        print("FACEBOOK LIVE TEST FINISHED")
        print("=" * 70)
    else:
        print("FACEBOOK LIVE TEST FAILED")
        print("=" * 70)
        print(f"FFmpeg exit code: {result.returncode}")


if __name__ == "__main__":
    main()

import json
import os
import subprocess
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "config.json"


def load_config():
    with CONFIG_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def build_audio_filter(audio_config):
    """
    Build FFmpeg audio filters from config.json.
    """

    if not audio_config.get("enabled", True):
        return "anull"

    filters = []

    mode = audio_config.get("mode", "normal").lower()

    volume = float(audio_config.get("volume", 1.0))

    if volume != 1.0:
        filters.append(f"volume={volume}")

    # Audio modes
    if mode == "clear":
        filters.append("highpass=f=80")
        filters.append("lowpass=f=15000")
        filters.append("acompressor=threshold=-18dB:ratio=3:attack=20:release=250")

    elif mode == "bass":
        filters.append("bass=g=6:f=100")

    elif mode == "treble":
        filters.append("treble=g=6:f=5000")

    elif mode == "voice":
        filters.append("highpass=f=120")
        filters.append("lowpass=f=12000")
        filters.append("acompressor=threshold=-20dB:ratio=3:attack=10:release=200")

    # Custom bass / treble
    bass = float(audio_config.get("bass", 0))
    treble = float(audio_config.get("treble", 0))

    if bass != 0:
        filters.append(f"bass=g={bass}:f=100")

    if treble != 0:
        filters.append(f"treble=g={treble}:f=5000")

    # Echo
    echo = audio_config.get("echo", {})

    if echo.get("enabled", False):
        in_gain = echo.get("in_gain", 0.8)
        out_gain = echo.get("out_gain", 0.9)
        delays = echo.get("delays", "1200|1200")
        decays = echo.get("decays", "0.25|0.15")

        filters.append(
            f"aecho={in_gain}:{out_gain}:{delays}:{decays}"
        )

    if not filters:
        return "anull"

    return ",".join(filters)


def build_video_filter(config):
    """
    Build FFmpeg video filters for:
    - logo
    - frame
    - LIVE badge
    """

    ffmpeg_config = config.get("ffmpeg", {})
    overlay = ffmpeg_config.get("overlay", {})

    filters = []

    frame = overlay.get("frame", {})

    if frame.get("enabled", True):
        width = int(frame.get("width", 8))
        color = frame.get("color", "0x8B0000")

        filters.append(
            f"drawbox=x=0:y=0:w=iw:h=ih:"
            f"color={color}:t={width}"
        )

    return filters


def main():
    print("=" * 70)
    print("FACEBOOK LIVE - LOGO / FRAME / AUDIO TEST")
    print("=" * 70)

    config = load_config()

    streams = config.get("streams", [])

    if not streams:
        print("ERROR: No streams configured.")
        return 1

    stream = next(
        (item for item in streams if item.get("enabled", False)),
        None
    )

    if not stream:
        print("ERROR: No enabled stream found.")
        return 1

    hls_url = stream.get("stream_url")

    rtmps_url = os.getenv("FACEBOOK_RTMPS_URL")
    stream_key = os.getenv("FACEBOOK_STREAM_KEY")

    if not hls_url:
        print("ERROR: HLS stream URL is missing.")
        return 1

    if not rtmps_url:
        print("ERROR: FACEBOOK_RTMPS_URL secret is missing.")
        return 1

    if not stream_key:
        print("ERROR: FACEBOOK_STREAM_KEY secret is missing.")
        return 1

    ffmpeg_config = config.get("ffmpeg", {})

    duration_minutes = int(
        ffmpeg_config.get("duration_minutes", 10)
    )

    video_config = ffmpeg_config.get("video", {})

    width = int(video_config.get("width", 1920))
    height = int(video_config.get("height", 1080))
    fps = int(video_config.get("fps", 25))

    bitrate = video_config.get("bitrate", "5000k")
    maxrate = video_config.get("maxrate", "5500k")
    bufsize = video_config.get("bufsize", "10000k")
    preset = video_config.get("preset", "veryfast")

    rtmps_url = rtmps_url.rstrip("/")
    facebook_url = f"{rtmps_url}/{stream_key}"

    overlay = ffmpeg_config.get("overlay", {})

    logo_enabled = overlay.get("enabled", True)

    logo_path = BASE_DIR / overlay.get(
        "logo",
        "assets/logo.png"
    )

    logo_width = int(
        overlay.get("logo_width", 180)
    )

    logo_position = overlay.get(
        "logo_position",
        {}
    )

    logo_x = int(logo_position.get("x", 35))
    logo_y = int(logo_position.get("y", 35))

    print("\nSource HLS:")
    print(hls_url)

    print("\nFacebook RTMPS:")
    print(rtmps_url)

    print("\nStream key:")
    print("[HIDDEN]")

    print("\nVideo:")
    print(f"{width}x{height} @ {fps} FPS")
    print(f"Bitrate: {bitrate}")

    print("\nDuration:")
    print(f"{duration_minutes} minutes")

    print("\nLogo:")
    print("Enabled" if logo_enabled else "Disabled")

    if logo_enabled:
        if not logo_path.exists():
            print("\nERROR: Logo file not found:")
            print(logo_path)
            return 1

        print(f"Path: {logo_path}")
        print(f"Width: {logo_width}px")
        print(f"Position: {logo_x},{logo_y}")

    audio_config = ffmpeg_config.get(
        "audio",
        {}
    )

    audio_mode = audio_config.get(
        "mode",
        "normal"
    )

    audio_filter = build_audio_filter(
        audio_config
    )

    print("\nAudio:")
    print(f"Mode: {audio_mode}")
    print(f"Filter: {audio_filter}")

    print("\nStarting FFmpeg...")

    command = [
        "ffmpeg",
        "-hide_banner",

        "-reconnect", "1",
        "-reconnect_streamed", "1",
        "-reconnect_delay_max", "5",

        "-i",
        hls_url
    ]

    # Logo input
    if logo_enabled:
        command.extend([
            "-i",
            str(logo_path)
        ])

    # Video filter
    video_filters = build_video_filter(config)

    if logo_enabled:
        logo_filter = (
            f"[1:v]scale={logo_width}:-1[logo]"
        )

        main_video = "[0:v]"

        video_filters_string = ",".join(
            video_filters
        )

        if video_filters_string:
            video_chain = (
                f"{main_video}{video_filters_string}"
                f"[base];"
                f"{logo_filter};"
                f"[base][logo]overlay="
                f"{logo_x}:{logo_y}[vout]"
            )
        else:
            video_chain = (
                f"{logo_filter};"
                f"[0:v][logo]overlay="
                f"{logo_x}:{logo_y}[vout]"
            )

        filter_complex = (
            f"{video_chain};"
            f"[0:a]{audio_filter}[aout]"
        )

        command.extend([
            "-filter_complex",
            filter_complex,
            "-map", "[vout]",
            "-map", "[aout]"
        ])

    else:
        video_filters_string = ",".join(
            video_filters
        )

        if video_filters_string:
            command.extend([
                "-vf",
                video_filters_string
            ])

        command.extend([
            "-map", "0:v:0",
            "-map", "0:a:0"
        ])

        command.extend([
            "-af",
            audio_filter
        ])

    command.extend([
        "-t",
        str(duration_minutes * 60),

        "-c:v",
        "libx264",

        "-preset",
        preset,

        "-tune",
        "zerolatency",

        "-b:v",
        bitrate,

        "-maxrate",
        maxrate,

        "-bufsize",
        bufsize,

        "-pix_fmt",
        "yuv420p",

        "-r",
        str(fps),

        "-g",
        str(fps * 2),

        "-c:a",
        "aac",

        "-b:a",
        "128k",

        "-ar",
        "48000",

        "-f",
        "flv",

        facebook_url
    ])

    print("\nFFmpeg command:")
    print("ffmpeg ... [STREAM KEY HIDDEN]")

    print("\n" + "=" * 70)
    print("LIVE STREAM STARTING")
    print("=" * 70)

    result = subprocess.run(command)

    print("\n" + "=" * 70)

    if result.returncode == 0:
        print("FACEBOOK LIVE TEST FINISHED")
        print("=" * 70)
        return 0

    print("FACEBOOK LIVE TEST FAILED")
    print("=" * 70)
    print(f"FFmpeg exit code: {result.returncode}")

    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())

import json
import os
import subprocess
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "config.json"


# ============================================================
# CONFIGURATION
# ============================================================

def load_config():
    """Load configuration from config.json."""

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
# AUDIO FILTER
# ============================================================

def build_audio_filter(audio_config):
    """
    Build FFmpeg audio filters from config.json.
    """

    if not audio_config.get(
        "enabled",
        True
    ):
        return "anull"

    filters = []

    mode = audio_config.get(
        "mode",
        "normal"
    ).lower()

    volume = float(
        audio_config.get(
            "volume",
            1.0
        )
    )

    if volume != 1.0:
        filters.append(
            f"volume={volume}"
        )

    # --------------------------------------------------------
    # Audio modes
    # --------------------------------------------------------

    if mode == "clear":

        filters.append(
            "highpass=f=80"
        )

        filters.append(
            "lowpass=f=15000"
        )

        filters.append(
            "acompressor="
            "threshold=-18dB:"
            "ratio=3:"
            "attack=20:"
            "release=250"
        )

    elif mode == "bass":

        filters.append(
            "bass=g=6:f=100"
        )

    elif mode == "treble":

        filters.append(
            "treble=g=6:f=5000"
        )

    elif mode == "voice":

        filters.append(
            "highpass=f=120"
        )

        filters.append(
            "lowpass=f=12000"
        )

        filters.append(
            "acompressor="
            "threshold=-20dB:"
            "ratio=3:"
            "attack=10:"
            "release=200"
        )

    # --------------------------------------------------------
    # Custom bass / treble
    # --------------------------------------------------------

    bass = float(
        audio_config.get(
            "bass",
            0
        )
    )

    treble = float(
        audio_config.get(
            "treble",
            0
        )
    )

    if bass != 0:

        filters.append(
            f"bass=g={bass}:f=100"
        )

    if treble != 0:

        filters.append(
            f"treble=g={treble}:f=5000"
        )

    # --------------------------------------------------------
    # Echo
    # --------------------------------------------------------

    echo = audio_config.get(
        "echo",
        {}
    )

    if echo.get(
        "enabled",
        False
    ):

        in_gain = echo.get(
            "in_gain",
            0.8
        )

        out_gain = echo.get(
            "out_gain",
            0.9
        )

        delays = echo.get(
            "delays",
            "1200|1200"
        )

        decays = echo.get(
            "decays",
            "0.25|0.15"
        )

        filters.append(
            f"aecho="
            f"{in_gain}:"
            f"{out_gain}:"
            f"{delays}:"
            f"{decays}"
        )

    if not filters:
        return "anull"

    return ",".join(
        filters
    )


# ============================================================
# VIDEO FILTER
# ============================================================

def build_video_filter(config):
    """
    Build FFmpeg video filters for:

    - Frame
    - LIVE badge
    """

    ffmpeg_config = config.get(
        "ffmpeg",
        {}
    )

    overlay = ffmpeg_config.get(
        "overlay",
        {}
    )

    filters = []

    # --------------------------------------------------------
    # Frame
    # --------------------------------------------------------

    frame = overlay.get(
        "frame",
        {}
    )

    if frame.get(
        "enabled",
        True
    ):

        width = int(
            frame.get(
                "width",
                8
            )
        )

        color = frame.get(
            "color",
            "0x8B0000"
        )

        filters.append(
            f"drawbox="
            f"x=0:"
            f"y=0:"
            f"w=iw:"
            f"h=ih:"
            f"color={color}:"
            f"t={width}"
        )

    # --------------------------------------------------------
    # LIVE badge
    # --------------------------------------------------------

    live_badge = overlay.get(
        "live_badge",
        {}
    )

    if live_badge.get(
        "enabled",
        False
    ):

        text_value = str(
            live_badge.get(
                "text",
                "LIVE"
            )
        )

        x = int(
            live_badge.get(
                "x",
                35
            )
        )

        y = int(
            live_badge.get(
                "y",
                220
            )
        )

        font_size = int(
            live_badge.get(
                "font_size",
                42
            )
        )

        font_color = live_badge.get(
            "font_color",
            "white"
        )

        box_color = live_badge.get(
            "box_color",
            "0x8B0000"
        )

        box_opacity = float(
            live_badge.get(
                "box_opacity",
                0.85
            )
        )

        # Escape characters that can affect FFmpeg drawtext.
        safe_text = (
            text_value
            .replace("\\", "\\\\")
            .replace(":", "\\:")
            .replace("'", "\\'")
        )

        # GitHub Ubuntu runners normally provide DejaVu Sans.
        font_file = (
            "/usr/share/fonts/"
            "truetype/dejavu/"
            "DejaVuSans-Bold.ttf"
        )

        filters.append(
            f"drawtext="
            f"fontfile='{font_file}':"
            f"text='{safe_text}':"
            f"x={x}:"
            f"y={y}:"
            f"fontsize={font_size}:"
            f"fontcolor={font_color}:"
            f"box=1:"
            f"boxcolor={box_color}@{box_opacity}:"
            f"boxborderw=12"
        )

    return filters


# ============================================================
# HLS HTTP HEADERS
# ============================================================

def build_hls_headers(config):
    """
    Build HTTP headers for the HLS input.

    These headers are passed directly to FFmpeg.
    """

    header_config = config.get(
        "headers",
        {}
    )

    user_agent = str(
        header_config.get(
            "User-Agent",
            ""
        )
    ).strip()

    referer = str(
        header_config.get(
            "Referer",
            ""
        )
    ).strip()

    headers = {}

    if user_agent:
        headers["User-Agent"] = user_agent

    if referer:
        headers["Referer"] = referer

    return headers


def build_ffmpeg_input_headers(headers):
    """
    Convert HTTP headers into FFmpeg's -headers format.

    FFmpeg expects CRLF between HTTP headers.
    """

    header_lines = []

    for name, value in headers.items():

        if not value:
            continue

        safe_value = str(
            value
        ).replace(
            "\r",
            ""
        ).replace(
            "\n",
            ""
        )

        header_lines.append(
            f"{name}: {safe_value}"
        )

    if not header_lines:
        return ""

    return "\r\n".join(
        header_lines
    ) + "\r\n"


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("FACEBOOK LIVE - HLS / LOGO / FRAME / LIVE / AUDIO TEST")
    print("=" * 70)

    # --------------------------------------------------------
    # Load configuration
    # --------------------------------------------------------

    try:

        config = load_config()

    except (
        FileNotFoundError,
        json.JSONDecodeError
    ) as error:

        print(
            f"ERROR: Configuration error: {error}"
        )

        return 1

    # --------------------------------------------------------
    # Streams
    # --------------------------------------------------------

    streams = config.get(
        "streams",
        []
    )

    if not streams:

        print(
            "ERROR: No streams configured."
        )

        return 1

    stream = next(
        (
            item
            for item in streams
            if item.get(
                "enabled",
                False
            )
        ),
        None
    )

    if not stream:

        print(
            "ERROR: No enabled stream found."
        )

        return 1

    stream_name = stream.get(
        "name",
        "Unknown Stream"
    )

    stream_id = stream.get(
        "id",
        "unknown"
    )

    hls_url = str(
        stream.get(
            "stream_url",
            ""
        )
    ).strip()

    # --------------------------------------------------------
    # Facebook credentials
    # --------------------------------------------------------

    rtmps_url = os.getenv(
        "FACEBOOK_RTMPS_URL"
    )

    stream_key = os.getenv(
        "FACEBOOK_STREAM_KEY"
    )

    if not hls_url:

        print(
            "ERROR: HLS stream URL is missing."
        )

        return 1

    if not rtmps_url:

        print(
            "ERROR: FACEBOOK_RTMPS_URL secret is missing."
        )

        return 1

    if not stream_key:

        print(
            "ERROR: FACEBOOK_STREAM_KEY secret is missing."
        )

        return 1

    # --------------------------------------------------------
    # FFmpeg configuration
    # --------------------------------------------------------

    ffmpeg_config = config.get(
        "ffmpeg",
        {}
    )

    duration_minutes = int(
        ffmpeg_config.get(
            "duration_minutes",
            10
        )
    )

    if duration_minutes <= 0:

        print(
            "ERROR: duration_minutes must be greater than 0."
        )

        return 1

    video_config = ffmpeg_config.get(
        "video",
        {}
    )

    width = int(
        video_config.get(
            "width",
            1920
        )
    )

    height = int(
        video_config.get(
            "height",
            1080
        )
    )

    fps = int(
        video_config.get(
            "fps",
            25
        )
    )

    bitrate = video_config.get(
        "bitrate",
        "5000k"
    )

    maxrate = video_config.get(
        "maxrate",
        "5500k"
    )

    bufsize = video_config.get(
        "bufsize",
        "10000k"
    )

    preset = video_config.get(
        "preset",
        "veryfast"
    )

    # --------------------------------------------------------
    # Facebook output URL
    # --------------------------------------------------------

    rtmps_url = rtmps_url.rstrip(
        "/"
    )

    facebook_url = (
        f"{rtmps_url}/"
        f"{stream_key}"
    )

    # --------------------------------------------------------
    # Overlay configuration
    # --------------------------------------------------------

    overlay = ffmpeg_config.get(
        "overlay",
        {}
    )

    logo_enabled = overlay.get(
        "enabled",
        True
    )

    logo_path = BASE_DIR / overlay.get(
        "logo",
        "assets/logo.png"
    )

    logo_width = int(
        overlay.get(
            "logo_width",
            180
        )
    )

    logo_position = overlay.get(
        "logo_position",
        {}
    )

    logo_x = int(
        logo_position.get(
            "x",
            35
        )
    )

    logo_y = int(
        logo_position.get(
            "y",
            35
        )
    )

    # --------------------------------------------------------
    # HLS headers
    # --------------------------------------------------------

    hls_headers = build_hls_headers(
        config
    )

    ffmpeg_headers = (
        build_ffmpeg_input_headers(
            hls_headers
        )
    )

    # --------------------------------------------------------
    # Display configuration
    # --------------------------------------------------------

    print("\nStream:")
    print(f"Name: {stream_name}")
    print(f"ID: {stream_id}")

    print("\nSource HLS:")
    print(hls_url)

    print("\nHLS HTTP headers:")

    if hls_headers:

        for name in hls_headers:

            print(
                f"- {name}: configured"
            )

    else:

        print(
            "- None"
        )

    print("\nFacebook RTMPS:")
    print(rtmps_url)

    print("\nStream key:")
    print("[HIDDEN]")

    print("\nVideo:")
    print(
        f"{width}x{height} @ {fps} FPS"
    )

    print(
        f"Bitrate: {bitrate}"
    )

    print(
        f"Maxrate: {maxrate}"
    )

    print(
        f"Bufsize: {bufsize}"
    )

    print(
        f"Preset: {preset}"
    )

    print("\nDuration:")
    print(
        f"{duration_minutes} minutes"
    )

    # --------------------------------------------------------
    # Logo
    # --------------------------------------------------------

    print("\nLogo:")

    print(
        "Enabled"
        if logo_enabled
        else "Disabled"
    )

    if logo_enabled:

        if not logo_path.exists():

            print(
                "\nERROR: Logo file not found:"
            )

            print(
                logo_path
            )

            return 1

        print(
            f"Path: {logo_path}"
        )

        print(
            f"Width: {logo_width}px"
        )

        print(
            f"Position: {logo_x},{logo_y}"
        )

    # --------------------------------------------------------
    # Frame / LIVE badge
    # --------------------------------------------------------

    frame_config = overlay.get(
        "frame",
        {}
    )

    live_badge_config = overlay.get(
        "live_badge",
        {}
    )

    print("\nFrame:")

    if frame_config.get(
        "enabled",
        True
    ):

        print(
            "Enabled"
        )

        print(
            f"Width: "
            f"{frame_config.get('width', 8)}px"
        )

        print(
            f"Color: "
            f"{frame_config.get('color', '0x8B0000')}"
        )

    else:

        print(
            "Disabled"
        )

    print("\nLIVE badge:")

    if live_badge_config.get(
        "enabled",
        False
    ):

        print(
            "Enabled"
        )

        print(
            f"Text: "
            f"{live_badge_config.get('text', 'LIVE')}"
        )

        print(
            f"Position: "
            f"{live_badge_config.get('x', 35)},"
            f"{live_badge_config.get('y', 220)}"
        )

    else:

        print(
            "Disabled"
        )

    # --------------------------------------------------------
    # Audio
    # --------------------------------------------------------

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
    print(
        f"Mode: {audio_mode}"
    )

    print(
        f"Filter: {audio_filter}"
    )

    # ========================================================
    # BUILD FFMPEG COMMAND
    # ========================================================

    print("\nStarting FFmpeg...")

    command = [
        "ffmpeg",

        "-hide_banner",

        "-loglevel",
        "info",

        # ----------------------------------------------------
        # HLS reconnect
        # ----------------------------------------------------

        "-reconnect",
        "1",

        "-reconnect_streamed",
        "1",

        "-reconnect_at_eof",
        "1",

        "-reconnect_delay_max",
        "5",
    ]

    # --------------------------------------------------------
    # HLS HTTP headers
    # --------------------------------------------------------

    if ffmpeg_headers:

        command.extend([
            "-headers",
            ffmpeg_headers
        ])

    # --------------------------------------------------------
    # HLS input
    # --------------------------------------------------------

    command.extend([
        "-i",
        hls_url
    ])

    # --------------------------------------------------------
    # Logo input
    # --------------------------------------------------------

    if logo_enabled:

        command.extend([
            "-i",
            str(logo_path)
        ])

    # ========================================================
    # VIDEO / AUDIO FILTER GRAPH
    # ========================================================

    video_filters = build_video_filter(
        config
    )

    video_filters_string = ",".join(
        video_filters
    )

    # --------------------------------------------------------
    # Logo enabled
    # --------------------------------------------------------

    if logo_enabled:

        logo_filter = (
            f"[1:v]"
            f"scale={logo_width}:-1"
            f"[logo]"
        )

        if video_filters_string:

            video_chain = (
                f"[0:v]"
                f"{video_filters_string}"
                f"[base];"
                f"{logo_filter};"
                f"[base][logo]"
                f"overlay="
                f"{logo_x}:{logo_y}"
                f"[vout]"
            )

        else:

            video_chain = (
                f"{logo_filter};"
                f"[0:v][logo]"
                f"overlay="
                f"{logo_x}:{logo_y}"
                f"[vout]"
            )

        filter_complex = (
            f"{video_chain};"
            f"[0:a]"
            f"{audio_filter}"
            f"[aout]"
        )

        command.extend([
            "-filter_complex",
            filter_complex,

            "-map",
            "[vout]",

            "-map",
            "[aout]"
        ])

    # --------------------------------------------------------
    # Logo disabled
    # --------------------------------------------------------

    else:

        if video_filters_string:

            command.extend([
                "-vf",
                video_filters_string
            ])

        command.extend([
            "-map",
            "0:v:0",

            "-map",
            "0:a:0",

            "-af",
            audio_filter
        ])

    # ========================================================
    # OUTPUT
    # ========================================================

    command.extend([

        # ----------------------------------------------------
        # Duration
        # ----------------------------------------------------

        "-t",
        str(
            duration_minutes * 60
        ),

        # ----------------------------------------------------
        # Video encoder
        # ----------------------------------------------------

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
        str(
            fps * 2
        ),

        # ----------------------------------------------------
        # Audio encoder
        # ----------------------------------------------------

        "-c:a",
        "aac",

        "-b:a",
        "128k",

        "-ar",
        "48000",

        # ----------------------------------------------------
        # Facebook / RTMPS
        # ----------------------------------------------------

        "-f",
        "flv",

        facebook_url
    ])

    # ========================================================
    # DISPLAY COMMAND
    # ========================================================

    print("\nFFmpeg command:")

    print(
        "ffmpeg ..."
        " [HLS HEADERS HIDDEN]"
        " [STREAM KEY HIDDEN]"
    )

    # ========================================================
    # START
    # ========================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "LIVE STREAM STARTING"
    )

    print(
        "=" * 70
    )

    try:

        result = subprocess.run(
            command,
            check=False
        )

    except FileNotFoundError:

        print(
            "\nERROR: FFmpeg was not found."
        )

        print(
            "Please make sure FFmpeg is installed."
        )

        return 1

    except KeyboardInterrupt:

        print(
            "\nFFmpeg process interrupted."
        )

        return 130

    except Exception as error:

        print(
            "\nERROR while running FFmpeg:"
        )

        print(
            error
        )

        return 1

    # ========================================================
    # RESULT
    # ========================================================

    print(
        "\n" + "=" * 70
    )

    if result.returncode == 0:

        print(
            "FACEBOOK LIVE TEST FINISHED"
        )

        print(
            "=" * 70
        )

        return 0

    print(
        "FACEBOOK LIVE TEST FAILED"
    )

    print(
        "=" * 70
    )

    print(
        f"FFmpeg exit code: "
        f"{result.returncode}"
    )

    return result.returncode


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )

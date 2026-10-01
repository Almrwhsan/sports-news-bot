import json
import os
import subprocess
import time
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

    if not audio_config.get("enabled", True):
        return "anull"

    filters = []

    mode = str(
        audio_config.get(
            "mode",
            "normal"
        )
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

    if mode == "young":

        filters.append(
            "asetrate=48000*1.12,aresample=48000"
        )

        filters.append(
            "highpass=f=180"
        )

        filters.append(
            "lowpass=f=13000"
        )

        filters.append(
            "acompressor="
            "threshold=-18dB:"
            "ratio=3:"
            "attack=10:"
            "release=200"
        )

    elif mode == "clear":

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

    return ",".join(filters)


# ============================================================
# VIDEO FILTER
# ============================================================

def build_video_filter(config):
    """
    Build FFmpeg video filters for:

    - Scaling
    - Padding
    - Semi-transparent frame
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

    filters = []

    # --------------------------------------------------------
    # Scale source to requested output size
    # --------------------------------------------------------

    filters.append(
        f"scale="
        f"{width}:"
        f"{height}:"
        f"force_original_aspect_ratio=decrease"
    )

    # --------------------------------------------------------
    # Pad to exact output resolution
    # --------------------------------------------------------

    filters.append(
        f"pad="
        f"{width}:"
        f"{height}:"
        f"(ow-iw)/2:"
        f"(oh-ih)/2"
    )

    # --------------------------------------------------------
    # Semi-transparent frame
    # --------------------------------------------------------

    frame = overlay.get(
        "frame",
        {}
    )

    if frame.get(
        "enabled",
        True
    ):

        frame_width = int(
            frame.get(
                "width",
                8
            )
        )

        color = frame.get(
            "color",
            "0x8B0000"
        )

        opacity = float(
            frame.get(
                "opacity",
                0.35
            )
        )

        filters.append(
            f"drawbox="
            f"x=0:"
            f"y=0:"
            f"w=iw:"
            f"h=ih:"
            f"color={color}@{opacity}:"
            f"t={frame_width}"
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

        safe_text = (
            text_value
            .replace("\\", "\\\\")
            .replace(":", "\\:")
            .replace("'", "\\'")
        )

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
    Convert HTTP headers into FFmpeg -headers format.
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
# BUILD FFMPEG COMMAND
# ============================================================

def build_ffmpeg_command(
    config,
    hls_url,
    facebook_url,
    logo_path,
    logo_enabled,
    logo_width,
    logo_x,
    logo_y,
    ffmpeg_headers
):
    """
    Build the complete FFmpeg command.

    The main logo is shown continuously.
    A second transparent moving watermark logo is also
    shown continuously for the entire broadcast.
    """

    ffmpeg_config = config.get(
        "ffmpeg",
        {}
    )

    video_config = ffmpeg_config.get(
        "video",
        {}
    )

    audio_config = ffmpeg_config.get(
        "audio",
        {}
    )

    overlay_config = ffmpeg_config.get(
        "overlay",
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

    audio_filter = build_audio_filter(
        audio_config
    )

    video_filters = build_video_filter(
        config
    )

    video_filters_string = ",".join(
        video_filters
    )

    command = [
        "ffmpeg",

        "-hide_banner",

        "-loglevel",
        "info",

        # ====================================================
        # HLS reconnect
        # ====================================================

        "-reconnect",
        "1",

        "-reconnect_streamed",
        "1",

        "-reconnect_at_eof",
        "1",

        "-reconnect_on_network_error",
        "1",

        "-reconnect_on_http_error",
        "4xx,5xx",

        "-reconnect_delay_max",
        "10",
    ]

    # ========================================================
    # HLS INPUT HEADERS
    # ========================================================

    if ffmpeg_headers:

        command.extend([
            "-headers",
            ffmpeg_headers
        ])

    # ========================================================
    # HLS INPUT
    # ========================================================

    command.extend([
        "-i",
        hls_url
    ])

    # ========================================================
    # MAIN LOGO INPUT
    # ========================================================

    if logo_enabled:

        command.extend([
            "-loop",
            "1",

            "-i",
            str(logo_path)
        ])

    # ========================================================
    # FILTER GRAPH
    # ========================================================

    if logo_enabled:

        # ----------------------------------------------------
        # Main corner logo
        # ----------------------------------------------------

        logo_filter = (
            f"[1:v]"
            f"format=rgba,"
            f"scale={logo_width}:-1"
            f"[logo]"
        )

        # ----------------------------------------------------
        # Transparent moving watermark
        #
        # IMPORTANT:
        # There is NO enable= expression here.
        #
        # Therefore the watermark stays visible continuously
        # from the beginning until FFmpeg stops.
        # ----------------------------------------------------

        watermark_config = overlay_config.get(
            "watermark",
            {}
        )

        watermark_enabled = watermark_config.get(
            "enabled",
            True
        )

        watermark_width = int(
            watermark_config.get(
                "width",
                500
            )
        )

        watermark_opacity = float(
            watermark_config.get(
                "opacity",
                0.10
            )
        )

        move_distance_x = float(
            watermark_config.get(
                "move_distance_x",
                100
            )
        )

        move_distance_y = float(
            watermark_config.get(
                "move_distance_y",
                50
            )
        )

        move_speed = float(
            watermark_config.get(
                "move_speed",
                0.015
            )
        )

        if watermark_enabled:

            watermark_filter = (
                f"[1:v]"
                f"format=rgba,"
                f"scale={watermark_width}:-1,"
                f"colorchannelmixer="
                f"aa={watermark_opacity}"
                f"[wm]"
            )

            # Continuous gentle movement.
            #
            # No mod()
            # No enable=
            # No show/hide cycle.
            #
            # The watermark remains on screen continuously.

            watermark_x = (
                f"(W-w)/2+"
                f"sin(t*{move_speed})*"
                f"{move_distance_x}"
            )

            watermark_y = (
                f"(H-h)/2+"
                f"cos(t*{move_speed})*"
                f"{move_distance_y}"
            )

            video_chain = (
                f"[0:v]"
                f"{video_filters_string}"
                f"[base];"

                f"{logo_filter};"

                f"{watermark_filter};"

                # Main logo - continuous
                f"[base][logo]"
                f"overlay="
                f"x={logo_x}:"
                f"y={logo_y}"
                f"[cornered];"

                # Transparent moving logo - continuous
                f"[cornered][wm]"
                f"overlay="
                f"x='{watermark_x}':"
                f"y='{watermark_y}'"
                f"[vout]"
            )

        else:

            video_chain = (
                f"[0:v]"
                f"{video_filters_string}"
                f"[base];"

                f"{logo_filter};"

                f"[base][logo]"
                f"overlay="
                f"x={logo_x}:"
                f"y={logo_y}"
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

    else:

        command.extend([
            "-vf",
            video_filters_string,

            "-map",
            "0:v:0",

            "-map",
            "0:a:0",

            "-af",
            audio_filter
        ])

    # ========================================================
    # VIDEO / AUDIO OUTPUT
    # ========================================================

    command.extend([

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

    return command


# ============================================================
# RUN FFMPEG
# ============================================================

def run_ffmpeg(
    command,
    restart_number
):
    """
    Run one FFmpeg session.

    Returns:
        FFmpeg exit code.
    """

    print(
        "\n" + "=" * 70
    )

    print(
        f"FFMPEG SESSION #{restart_number}"
    )

    print(
        "=" * 70
    )

    print(
        "LIVE STREAM RUNNING..."
    )

    print(
        "Continuous watermark: ENABLED"
    )

    print(
        "Press CTRL+C to stop."
    )

    try:

        result = subprocess.run(
            command,
            check=False
        )

        return result.returncode

    except KeyboardInterrupt:

        print(
            "\nFFmpeg interrupted by user."
        )

        return 130

    except FileNotFoundError:

        print(
            "\nERROR: FFmpeg was not found."
        )

        return 127

    except Exception as error:

        print(
            "\nERROR while running FFmpeg:"
        )

        print(
            error
        )

        return 1


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print(
        "FACEBOOK LIVE - AUTO RECONNECT / AUTO RESTART"
    )
    print("=" * 70)

    # ========================================================
    # LOAD CONFIG
    # ========================================================

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

    # ========================================================
    # STREAM
    # ========================================================

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

    if not hls_url:

        print(
            "ERROR: HLS stream URL is missing."
        )

        return 1

    # ========================================================
    # FACEBOOK
    # ========================================================

    rtmps_url = os.getenv(
        "FACEBOOK_RTMPS_URL"
    )

    stream_key = os.getenv(
        "FACEBOOK_STREAM_KEY"
    )

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

    rtmps_url = rtmps_url.rstrip("/")

    facebook_url = (
        f"{rtmps_url}/"
        f"{stream_key}"
    )

    # ========================================================
    # FFMPEG CONFIG
    # ========================================================

    ffmpeg_config = config.get(
        "ffmpeg",
        {}
    )

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

    # ========================================================
    # AUTO RESTART CONFIG
    # ========================================================

    auto_restart = config.get(
        "auto_restart",
        {}
    )

    auto_restart_enabled = auto_restart.get(
        "enabled",
        True
    )

    restart_delay = int(
        auto_restart.get(
            "restart_delay_seconds",
            5
        )
    )

    max_restarts = int(
        auto_restart.get(
            "max_restarts",
            0
        )
    )

    # 0 = unlimited

    max_restart_delay = int(
        auto_restart.get(
            "max_restart_delay_seconds",
            60
        )
    )

    # ========================================================
    # OVERLAY
    # ========================================================

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
            220
        )
    )

    logo_position = overlay.get(
        "logo_position",
        {}
    )

    logo_x = int(
        logo_position.get(
            "x",
            1660
        )
    )

    logo_y = int(
        logo_position.get(
            "y",
            35
        )
    )

    watermark_config = overlay.get(
        "watermark",
        {}
    )

    watermark_enabled = watermark_config.get(
        "enabled",
        True
    )

    watermark_width = int(
        watermark_config.get(
            "width",
            500
        )
    )

    watermark_opacity = float(
        watermark_config.get(
            "opacity",
            0.10
        )
    )

    watermark_move_x = float(
        watermark_config.get(
            "move_distance_x",
            100
        )
    )

    watermark_move_y = float(
        watermark_config.get(
            "move_distance_y",
            50
        )
    )

    watermark_speed = float(
        watermark_config.get(
            "move_speed",
            0.015
        )
    )

    # ========================================================
    # LOGO CHECK
    # ========================================================

    if logo_enabled:

        if not logo_path.exists():

            print(
                "\nERROR: Logo file not found:"
            )

            print(
                logo_path
            )

            return 1

    # ========================================================
    # HEADERS
    # ========================================================

    hls_headers = build_hls_headers(
        config
    )

    ffmpeg_headers = (
        build_ffmpeg_input_headers(
            hls_headers
        )
    )

    # ========================================================
    # DISPLAY
    # ========================================================

    print("\nStream:")
    print(
        f"Name: {stream_name}"
    )

    print(
        f"ID: {stream_id}"
    )

    print("\nSource HLS:")
    print(
        hls_url
    )

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
    print(
        rtmps_url
    )

    print("\nStream key:")
    print(
        "[HIDDEN]"
    )

    print("\nOutput:")
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

    print("\nMain Logo:")

    if logo_enabled:

        print(
            "Enabled"
        )

        print(
            f"Path: {logo_path}"
        )

        print(
            f"Width: {logo_width}px"
        )

        print(
            f"Position: {logo_x},{logo_y}"
        )

    else:

        print(
            "Disabled"
        )

    print("\nContinuous Watermark:")

    if watermark_enabled:

        print(
            "Enabled - visible for entire broadcast"
        )

        print(
            f"Width: {watermark_width}px"
        )

        print(
            f"Opacity: {watermark_opacity}"
        )

        print(
            f"Movement X: {watermark_move_x}px"
        )

        print(
            f"Movement Y: {watermark_move_y}px"
        )

        print(
            f"Movement speed: {watermark_speed}"
        )

        print(
            "Show/Hide timer: DISABLED"
        )

    else:

        print(
            "Disabled"
        )

    print("\nAuto Restart:")

    print(
        "Enabled"
        if auto_restart_enabled
        else "Disabled"
    )

    if auto_restart_enabled:

        print(
            f"Restart delay: "
            f"{restart_delay}s"
        )

        if max_restarts == 0:

            print(
                "Maximum restarts: Unlimited"
            )

        else:

            print(
                f"Maximum restarts: "
                f"{max_restarts}"
            )

        print(
            f"Maximum retry delay: "
            f"{max_restart_delay}s"
        )

    # ========================================================
    # BUILD COMMAND
    # ========================================================

    command = build_ffmpeg_command(
        config=config,
        hls_url=hls_url,
        facebook_url=facebook_url,
        logo_path=logo_path,
        logo_enabled=logo_enabled,
        logo_width=logo_width,
        logo_x=logo_x,
        logo_y=logo_y,
        ffmpeg_headers=ffmpeg_headers
    )

    print("\nFFmpeg command:")
    print(
        "ffmpeg ..."
        " [HLS HEADERS HIDDEN]"
        " [STREAM KEY HIDDEN]"
    )

    # ========================================================
    # AUTO RESTART LOOP
    # ========================================================

    restart_number = 1

    current_delay = restart_delay

    while True:

        return_code = run_ffmpeg(
            command,
            restart_number
        )

        # ----------------------------------------------------
        # Manual stop
        # ----------------------------------------------------

        if return_code == 130:

            print(
                "\n" + "=" * 70
            )

            print(
                "STREAM STOPPED BY USER"
            )

            print(
                "=" * 70
            )

            return 0

        # ----------------------------------------------------
        # FFmpeg missing
        # ----------------------------------------------------

        if return_code == 127:

            print(
                "\nFFmpeg is not installed."
            )

            return 127

        # ----------------------------------------------------
        # Auto restart disabled
        # ----------------------------------------------------

        if not auto_restart_enabled:

            print(
                "\n" + "=" * 70
            )

            print(
                "FACEBOOK LIVE FAILED"
            )

            print(
                "=" * 70
            )

            print(
                f"FFmpeg exit code: "
                f"{return_code}"
            )

            return return_code

        # ----------------------------------------------------
        # Check restart limit
        # ----------------------------------------------------

        if (
            max_restarts > 0
            and restart_number >= max_restarts
        ):

            print(
                "\n" + "=" * 70
            )

            print(
                "MAXIMUM RESTARTS REACHED"
            )

            print(
                "=" * 70
            )

            print(
                f"Last FFmpeg exit code: "
                f"{return_code}"
            )

            return return_code

        # ----------------------------------------------------
        # Restart
        # ----------------------------------------------------

        print(
            "\n" + "=" * 70
        )

        print(
            "FFMPEG STOPPED"
        )

        print(
            "=" * 70
        )

        print(
            f"Exit code: {return_code}"
        )

        print(
            "The stream may have disconnected."
        )

        print(
            f"Restarting FFmpeg in "
            f"{current_delay} seconds..."
        )

        try:

            time.sleep(
                current_delay
            )

        except KeyboardInterrupt:

            print(
                "\nRestart cancelled by user."
            )

            return 130

        restart_number += 1

        # ----------------------------------------------------
        # Exponential backoff
        # ----------------------------------------------------

        current_delay = min(
            current_delay * 2,
            max_restart_delay
        )

        print(
            "\nRe-opening HLS source..."
        )

        print(
            "Starting a fresh FFmpeg session..."
        )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )
import json
import os
import subprocess
import time
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

    if not audio_config.get("enabled", True):
        return "anull"

    filters = []

    mode = str(
        audio_config.get(
            "mode",
            "normal"
        )
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

    if mode == "young":

        filters.append(
            "asetrate=48000*1.12,aresample=48000"
        )

        filters.append(
            "highpass=f=180"
        )

        filters.append(
            "lowpass=f=13000"
        )

        filters.append(
            "acompressor="
            "threshold=-18dB:"
            "ratio=3:"
            "attack=10:"
            "release=200"
        )

    elif mode == "clear":

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

    return ",".join(filters)


# ============================================================
# VIDEO FILTER
# ============================================================

def build_video_filter(config):
    """
    Build FFmpeg video filters for:

    - Scaling
    - Padding
    - Semi-transparent frame
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

    filters = []

    # --------------------------------------------------------
    # Scale source to requested output size
    # --------------------------------------------------------

    filters.append(
        f"scale="
        f"{width}:"
        f"{height}:"
        f"force_original_aspect_ratio=decrease"
    )

    # --------------------------------------------------------
    # Pad to exact output resolution
    # --------------------------------------------------------

    filters.append(
        f"pad="
        f"{width}:"
        f"{height}:"
        f"(ow-iw)/2:"
        f"(oh-ih)/2"
    )

    # --------------------------------------------------------
    # Semi-transparent frame
    # --------------------------------------------------------

    frame = overlay.get(
        "frame",
        {}
    )

    if frame.get(
        "enabled",
        True
    ):

        frame_width = int(
            frame.get(
                "width",
                8
            )
        )

        color = frame.get(
            "color",
            "0x8B0000"
        )

        opacity = float(
            frame.get(
                "opacity",
                0.35
            )
        )

        filters.append(
            f"drawbox="
            f"x=0:"
            f"y=0:"
            f"w=iw:"
            f"h=ih:"
            f"color={color}@{opacity}:"
            f"t={frame_width}"
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

        safe_text = (
            text_value
            .replace("\\", "\\\\")
            .replace(":", "\\:")
            .replace("'", "\\'")
        )

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
    Convert HTTP headers into FFmpeg -headers format.
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
# BUILD FFMPEG COMMAND
# ============================================================

def build_ffmpeg_command(
    config,
    hls_url,
    facebook_url,
    logo_path,
    logo_enabled,
    logo_width,
    logo_x,
    logo_y,
    ffmpeg_headers
):
    """
    Build the complete FFmpeg command.

    The main logo is shown continuously.
    A second transparent moving watermark logo is also
    shown continuously for the entire broadcast.
    """

    ffmpeg_config = config.get(
        "ffmpeg",
        {}
    )

    video_config = ffmpeg_config.get(
        "video",
        {}
    )

    audio_config = ffmpeg_config.get(
        "audio",
        {}
    )

    overlay_config = ffmpeg_config.get(
        "overlay",
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

    audio_filter = build_audio_filter(
        audio_config
    )

    video_filters = build_video_filter(
        config
    )

    video_filters_string = ",".join(
        video_filters
    )

    command = [
        "ffmpeg",

        "-hide_banner",

        "-loglevel",
        "info",

        # ====================================================
        # HLS reconnect
        # ====================================================

        "-reconnect",
        "1",

        "-reconnect_streamed",
        "1",

        "-reconnect_at_eof",
        "1",

        "-reconnect_on_network_error",
        "1",

        "-reconnect_on_http_error",
        "4xx,5xx",

        "-reconnect_delay_max",
        "10",
    ]

    # ========================================================
    # HLS INPUT HEADERS
    # ========================================================

    if ffmpeg_headers:

        command.extend([
            "-headers",
            ffmpeg_headers
        ])

    # ========================================================
    # HLS INPUT
    # ========================================================

    command.extend([
        "-i",
        hls_url
    ])

    # ========================================================
    # MAIN LOGO INPUT
    # ========================================================

    if logo_enabled:

        command.extend([
            "-loop",
            "1",

            "-i",
            str(logo_path)
        ])

    # ========================================================
    # FILTER GRAPH
    # ========================================================

    if logo_enabled:

        # ----------------------------------------------------
        # Main corner logo
        # ----------------------------------------------------

        logo_filter = (
            f"[1:v]"
            f"format=rgba,"
            f"scale={logo_width}:-1"
            f"[logo]"
        )

        # ----------------------------------------------------
        # Transparent moving watermark
        #
        # IMPORTANT:
        # There is NO enable= expression here.
        #
        # Therefore the watermark stays visible continuously
        # from the beginning until FFmpeg stops.
        # ----------------------------------------------------

        watermark_config = overlay_config.get(
            "watermark",
            {}
        )

        watermark_enabled = watermark_config.get(
            "enabled",
            True
        )

        watermark_width = int(
            watermark_config.get(
                "width",
                500
            )
        )

        watermark_opacity = float(
            watermark_config.get(
                "opacity",
                0.10
            )
        )

        move_distance_x = float(
            watermark_config.get(
                "move_distance_x",
                100
            )
        )

        move_distance_y = float(
            watermark_config.get(
                "move_distance_y",
                50
            )
        )

        move_speed = float(
            watermark_config.get(
                "move_speed",
                0.015
            )
        )

        if watermark_enabled:

            watermark_filter = (
                f"[1:v]"
                f"format=rgba,"
                f"scale={watermark_width}:-1,"
                f"colorchannelmixer="
                f"aa={watermark_opacity}"
                f"[wm]"
            )

            # Continuous gentle movement.
            #
            # No mod()
            # No enable=
            # No show/hide cycle.
            #
            # The watermark remains on screen continuously.

            watermark_x = (
                f"(W-w)/2+"
                f"sin(t*{move_speed})*"
                f"{move_distance_x}"
            )

            watermark_y = (
                f"(H-h)/2+"
                f"cos(t*{move_speed})*"
                f"{move_distance_y}"
            )

            video_chain = (
                f"[0:v]"
                f"{video_filters_string}"
                f"[base];"

                f"{logo_filter};"

                f"{watermark_filter};"

                # Main logo - continuous
                f"[base][logo]"
                f"overlay="
                f"x={logo_x}:"
                f"y={logo_y}"
                f"[cornered];"

                # Transparent moving logo - continuous
                f"[cornered][wm]"
                f"overlay="
                f"x='{watermark_x}':"
                f"y='{watermark_y}'"
                f"[vout]"
            )

        else:

            video_chain = (
                f"[0:v]"
                f"{video_filters_string}"
                f"[base];"

                f"{logo_filter};"

                f"[base][logo]"
                f"overlay="
                f"x={logo_x}:"
                f"y={logo_y}"
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

    else:

        command.extend([
            "-vf",
            video_filters_string,

            "-map",
            "0:v:0",

            "-map",
            "0:a:0",

            "-af",
            audio_filter
        ])

    # ========================================================
    # VIDEO / AUDIO OUTPUT
    # ========================================================

    command.extend([

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

    return command


# ============================================================
# RUN FFMPEG
# ============================================================

def run_ffmpeg(
    command,
    restart_number
):
    """
    Run one FFmpeg session.

    Returns:
        FFmpeg exit code.
    """

    print(
        "\n" + "=" * 70
    )

    print(
        f"FFMPEG SESSION #{restart_number}"
    )

    print(
        "=" * 70
    )

    print(
        "LIVE STREAM RUNNING..."
    )

    print(
        "Continuous watermark: ENABLED"
    )

    print(
        "Press CTRL+C to stop."
    )

    try:

        result = subprocess.run(
            command,
            check=False
        )

        return result.returncode

    except KeyboardInterrupt:

        print(
            "\nFFmpeg interrupted by user."
        )

        return 130

    except FileNotFoundError:

        print(
            "\nERROR: FFmpeg was not found."
        )

        return 127

    except Exception as error:

        print(
            "\nERROR while running FFmpeg:"
        )

        print(
            error
        )

        return 1


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print(
        "FACEBOOK LIVE - AUTO RECONNECT / AUTO RESTART"
    )
    print("=" * 70)

    # ========================================================
    # LOAD CONFIG
    # ========================================================

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

    # ========================================================
    # STREAM
    # ========================================================

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

    if not hls_url:

        print(
            "ERROR: HLS stream URL is missing."
        )

        return 1

    # ========================================================
    # FACEBOOK
    # ========================================================

    rtmps_url = os.getenv(
        "FACEBOOK_RTMPS_URL"
    )

    stream_key = os.getenv(
        "FACEBOOK_STREAM_KEY"
    )

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

    rtmps_url 

import json
import subprocess
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "config.json"


# ============================================================
# CONFIG
# ============================================================

def load_config():
    with CONFIG_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


# ============================================================
# AUDIO FILTER
# ============================================================

def build_audio_filter(audio_config):
    """
    Build FFmpeg audio filter chain.

    IMPORTANT:
    The current audio settings are preserved exactly.
    """

    if not audio_config.get("enabled", True):
        return "anull"

    filters = []

    mode = str(
        audio_config.get("mode", "normal")
    ).lower()

    volume = float(
        audio_config.get("volume", 1.0)
    )

    # --------------------------------------------------------
    # Volume
    # --------------------------------------------------------

    if volume != 1.0:
        filters.append(
            f"volume={volume}"
        )

    # --------------------------------------------------------
    # Preset audio modes
    # --------------------------------------------------------

    if mode == "clear":

        filters.extend([
            "highpass=f=80",
            "lowpass=f=15000",
            "acompressor="
            "threshold=-18dB:"
            "ratio=3:"
            "attack=20:"
            "release=250"
        ])

    elif mode == "bass":

        filters.append(
            "bass=g=6:f=100"
        )

    elif mode == "treble":

        filters.append(
            "treble=g=6:f=5000"
        )

    elif mode == "voice":

        filters.extend([
            "highpass=f=120",
            "lowpass=f=12000",
            "acompressor="
            "threshold=-20dB:"
            "ratio=3:"
            "attack=10:"
            "release=200"
        ])

    # --------------------------------------------------------
    # Additional bass
    # --------------------------------------------------------

    bass = float(
        audio_config.get("bass", 0)
    )

    if bass != 0:

        filters.append(
            f"bass=g={bass}:f=100"
        )

    # --------------------------------------------------------
    # Additional treble
    # --------------------------------------------------------

    treble = float(
        audio_config.get("treble", 0)
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

    if echo.get("enabled", False):

        in_gain = float(
            echo.get("in_gain", 0.8)
        )

        out_gain = float(
            echo.get("out_gain", 0.9)
        )

        delays = str(
            echo.get(
                "delays",
                "1200|1200"
            )
        )

        decays = str(
            echo.get(
                "decays",
                "0.25|0.15"
            )
        )

        filters.append(
            "aecho="
            f"in_gain={in_gain}:"
            f"out_gain={out_gain}:"
            f"delays={delays}:"
            f"decays={decays}"
        )

    return (
        ",".join(filters)
        if filters
        else "anull"
    )


# ============================================================
# VIDEO FRAME
# ============================================================

def build_video_filter(config):

    overlay = config.get(
        "ffmpeg",
        {}
    ).get(
        "overlay",
        {}
    )

    frame = overlay.get(
        "frame",
        {}
    )

    filters = []

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

    return filters


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("FFMPEG GRAPHICS + AUDIO TEST")
    print("=" * 70)

    # --------------------------------------------------------
    # Load configuration
    # --------------------------------------------------------

    try:

        config = load_config()

    except Exception as error:

        print(
            f"ERROR: Could not load config.json: {error}"
        )

        return 1

    streams = config.get(
        "streams",
        []
    )

    if not streams:

        print(
            "ERROR: No streams configured."
        )

        return 1

    # --------------------------------------------------------
    # Find enabled stream
    # --------------------------------------------------------

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

    hls_url = stream.get(
        "stream_url"
    )

    if not hls_url:

        print(
            "ERROR: HLS URL is missing."
        )

        return 1

    # --------------------------------------------------------
    # Configuration sections
    # --------------------------------------------------------

    ffmpeg_config = config.get(
        "ffmpeg",
        {}
    )

    overlay = ffmpeg_config.get(
        "overlay",
        {}
    )

    audio_config = ffmpeg_config.get(
        "audio",
        {}
    )

    video_config = ffmpeg_config.get(
        "video",
        {}
    )

    # --------------------------------------------------------
    # Output
    # --------------------------------------------------------

    output_file = (
        BASE_DIR /
        "ffmpeg_graphics_test.mp4"
    )

    # --------------------------------------------------------
    # Main logo
    # --------------------------------------------------------

    logo_enabled = overlay.get(
        "enabled",
        True
    )

    logo_path = (
        BASE_DIR /
        overlay.get(
            "logo",
            "assets/logo.png"
        )
    )

    logo_width = int(
        overlay.get(
            "logo_width",
            0
        )
    )

    position = overlay.get(
        "logo_position",
        {}
    )

    logo_x = int(
        position.get(
            "x",
            1635
        )
    )

    logo_y = int(
        position.get(
            "y",
            35
        )
    )

    # --------------------------------------------------------
    # Watermark
    # --------------------------------------------------------

    watermark = overlay.get(
        "watermark",
        {}
    )

    watermark_enabled = watermark.get(
        "enabled",
        False
    )

    watermark_opacity = float(
        watermark.get(
            "opacity",
            0.15
        )
    )

    watermark_width = int(
        watermark.get(
            "width",
            320
        )
    )

    watermark_show_duration = float(
        watermark.get(
            "show_duration",
            8
        )
    )

    watermark_interval = float(
        watermark.get(
            "interval",
            35
        )
    )

    watermark_move_x = float(
        watermark.get(
            "move_distance_x",
            300
        )
    )

    watermark_move_y = float(
        watermark.get(
            "move_distance_y",
            150
        )
    )

    watermark_speed = float(
        watermark.get(
            "move_speed",
            0.03
        )
    )

    # --------------------------------------------------------
    # Video settings
    # --------------------------------------------------------

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
    # Print information
    # --------------------------------------------------------

    print("\nSource:")
    print(hls_url)

    print("\nOutput:")
    print(output_file)

    print("\nResolution:")
    print(
        f"{width}x{height}"
    )

    # --------------------------------------------------------
    # Logo information
    # --------------------------------------------------------

    print("\nMain Logo:")

    if logo_enabled:

        if not logo_path.exists():

            print(
                "ERROR: Logo file not found:"
            )

            print(
                logo_path
            )

            return 1

        print("Enabled")

        print(
            f"Path: {logo_path}"
        )

        if logo_width <= 0:

            print(
                "Size: Original image size"
            )

        else:

            print(
                f"Width: {logo_width}"
            )

        print(
            f"Position: "
            f"{logo_x},{logo_y}"
        )

    else:

        print("Disabled")

    # --------------------------------------------------------
    # Watermark information
    # --------------------------------------------------------

    print("\nMoving Watermark:")

    if watermark_enabled:

        print("Enabled")

        print(
            f"Opacity: "
            f"{watermark_opacity}"
        )

        print(
            f"Width: "
            f"{watermark_width}"
        )

        print(
            f"Visible duration: "
            f"{watermark_show_duration}s"
        )

        print(
            f"Interval: "
            f"{watermark_interval}s"
        )

        print(
            f"Movement: "
            f"{watermark_move_x}x"
            f"{watermark_move_y}"
        )

    else:

        print("Disabled")

    # --------------------------------------------------------
    # Audio
    # --------------------------------------------------------

    audio_filter = build_audio_filter(
        audio_config
    )

    print("\nAudio mode:")

    print(
        audio_config.get(
            "mode",
            "normal"
        )
    )

    print("\nAudio filter:")

    print(
        audio_filter
    )

    # --------------------------------------------------------
    # Base video filter
    # --------------------------------------------------------

    video_filters = build_video_filter(
        config
    )

    if video_filters:

        video_filter_string = ",".join(
            video_filters
        )

        video_base = (
            f"[0:v]"
            f"{video_filter_string}"
            f"[base]"
        )

    else:

        video_base = (
            "[0:v]"
            "null"
            "[base]"
        )

    # --------------------------------------------------------
    # Build video / logo filter
    # --------------------------------------------------------

    if logo_enabled:

        # ----------------------------------------------------
        # Main logo
        # ----------------------------------------------------

        if logo_width <= 0:

            logo_chain = (
                "[1:v]"
                "format=rgba"
                "[logo]"
            )

        else:

            logo_chain = (
                "[1:v]"
                f"scale={logo_width}:-1"
                ",format=rgba"
                "[logo]"
            )

        main_overlay = (
            "[base][logo]"
            f"overlay={logo_x}:{logo_y}"
            "[v1]"
        )

        # ----------------------------------------------------
        # Moving watermark
        # ----------------------------------------------------

        if watermark_enabled:

            watermark_chain = (
                "[2:v]"
                f"scale={watermark_width}:-1,"
                "format=rgba,"
                f"colorchannelmixer=aa={watermark_opacity}"
                "[wm]"
            )

            # The watermark appears periodically.
            #
            # Example with current settings:
            #
            # 0 - 8 sec     visible
            # 8 - 35 sec    hidden
            # 35 - 43 sec   visible
            # 43 - 70 sec   hidden
            #
            # While visible, it moves gently.

            watermark_cycle = (
                watermark_show_duration +
                watermark_interval
            )

            moving_overlay = (
                "[v1][wm]"
                "overlay="
                f"x='(W-w)/2+"
                f"sin(t*{watermark_speed})*"
                f"{watermark_move_x}':"
                f"y='(H-h)/2+"
                f"cos(t*{watermark_speed})*"
                f"{watermark_move_y}':"
                f"enable='lt("
                f"mod(t,{watermark_cycle}),"
                f"{watermark_show_duration}"
                f")'"
                "[vout]"
            )

            filter_complex = (
                f"{video_base};"
                f"{logo_chain};"
                f"{main_overlay};"
                f"{watermark_chain};"
                f"{moving_overlay};"
                f"[0:a]{audio_filter}[aout]"
            )

        else:

            filter_complex = (
                f"{video_base};"
                f"{logo_chain};"
                f"{main_overlay};"
                f"[0:a]{audio_filter}[aout]"
            )

    else:

        # ----------------------------------------------------
        # No main logo
        # ----------------------------------------------------

        if watermark_enabled:

            watermark_chain = (
                "[1:v]"
                f"scale={watermark_width}:-1,"
                "format=rgba,"
                f"colorchannelmixer=aa={watermark_opacity}"
                "[wm]"
            )

            watermark_cycle = (
                watermark_show_duration +
                watermark_interval
            )

            moving_overlay = (
                "[base][wm]"
                "overlay="
                f"x='(W-w)/2+"
                f"sin(t*{watermark_speed})*"
                f"{watermark_move_x}':"
                f"y='(H-h)/2+"
                f"cos(t*{watermark_speed})*"
                f"{watermark_move_y}':"
                f"enable='lt("
                f"mod(t,{watermark_cycle}),"
                f"{watermark_show_duration}"
                f")'"
                "[vout]"
            )

            filter_complex = (
                f"{video_base};"
                f"{watermark_chain};"
                f"{moving_overlay};"
                f"[0:a]{audio_filter}[aout]"
            )

        else:

            filter_complex = (
                f"{video_base}[vout];"
                f"[0:a]{audio_filter}[aout]"
            )

    # --------------------------------------------------------
    # FFmpeg command
    # --------------------------------------------------------

    command = [
        "ffmpeg",

        "-hide_banner",

        # HLS reconnect
        "-reconnect",
        "1",

        "-reconnect_streamed",
        "1",

        "-reconnect_at_eof",
        "1",

        "-reconnect_delay_max",
        "5",

        # HLS input
        "-i",
        hls_url
    ]

    # --------------------------------------------------------
    # Logo inputs
    # --------------------------------------------------------

    if logo_enabled:

        command.extend([
            "-loop",
            "1",

            "-i",
            str(logo_path)
        ])

        if watermark_enabled:

            command.extend([
                "-loop",
                "1",

                "-i",
                str(logo_path)
            ])

    else:

        if watermark_enabled:

            command.extend([
                "-loop",
                "1",

                "-i",
                str(logo_path)
            ])

    # --------------------------------------------------------
    # Encoding
    # --------------------------------------------------------

    command.extend([

        # Test duration
        "-t",
        "30",

        # Filter graph
        "-filter_complex",
        filter_complex,

        # Video map
        "-map",
        "[vout]",

        # Audio map
        "-map",
        "[aout]",

        # Video encoder
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

        # Audio encoder
        "-c:a",
        "aac",

        "-b:a",
        "128k",

        "-ar",
        "48000",

        # MP4
        "-movflags",
        "+faststart",

        # Replace existing test
        "-y",

        str(output_file)
    ])

    # --------------------------------------------------------
    # Print command information
    # --------------------------------------------------------

    print("\nStarting FFmpeg...")

    print(
        "Test duration: 30 seconds"
    )

    print(
        "\nMain logo:"
        " fixed position"
    )

    if watermark_enabled:

        print(
            "Moving watermark:"
            " enabled"
        )

    # --------------------------------------------------------
    # Start FFmpeg
    # --------------------------------------------------------

    result = subprocess.run(
        command
    )

    # --------------------------------------------------------
    # Result
    # --------------------------------------------------------

    print(
        "\n" + "=" * 70
    )

    if result.returncode != 0:

        print(
            "FFMPEG GRAPHICS TEST FAILED"
        )

        print(
            "=" * 70
        )

        print(
            f"FFmpeg exit code: "
            f"{result.returncode}"
        )

        return result.returncode

    # --------------------------------------------------------
    # Verify output
    # --------------------------------------------------------

    if not output_file.exists():

        print(
            "TEST FAILED: "
            "Output file was not created."
        )

        return 1

    file_size = output_file.stat().st_size

    if file_size <= 0:

        print(
            "TEST FAILED: "
            "Output file is empty."
        )

        return 1

    size_mb = (
        file_size /
        (1024 * 1024)
    )

    # --------------------------------------------------------
    # Success
    # --------------------------------------------------------

    print(
        "FFMPEG GRAPHICS TEST SUCCESSFUL"
    )

    print(
        "=" * 70
    )

    print("\nOutput file:")

    print(
        output_file
    )

    print(
        f"\nFile size: "
        f"{size_mb:.2f} MB"
    )

    return 0


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )

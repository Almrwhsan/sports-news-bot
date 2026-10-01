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
    Audio configuration intentionally preserved.
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

    if volume != 1.0:
        filters.append(
            f"volume={volume}"
        )

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
    # Bass
    # --------------------------------------------------------

    bass = float(
        audio_config.get("bass", 0)
    )

    if bass != 0:

        filters.append(
            f"bass=g={bass}:f=100"
        )

    # --------------------------------------------------------
    # Treble
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
                40
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

        # ----------------------------------------------------
        # Semi-transparent frame.
        # The original video remains visible beneath it.
        # ----------------------------------------------------

        filters.append(
            f"drawbox="
            f"x=0:"
            f"y=0:"
            f"w=iw:"
            f"h=ih:"
            f"color={color}@{opacity}:"
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

    # ========================================================
    # LOAD CONFIG
    # ========================================================

    try:

        config = load_config()

    except Exception as error:

        print(
            f"ERROR: Could not load config.json: {error}"
        )

        return 1

    # ========================================================
    # STREAMS
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

    hls_url = stream.get(
        "stream_url"
    )

    if not hls_url:

        print(
            "ERROR: HLS URL is missing."
        )

        return 1

    # ========================================================
    # CONFIGURATION
    # ========================================================

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

    # ========================================================
    # OUTPUT
    # ========================================================

    output_file = (
        BASE_DIR /
        "ffmpeg_graphics_test.mp4"
    )

    # ========================================================
    # MAIN LOGO
    # ========================================================

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

    # ========================================================
    # WATERMARK
    # ========================================================

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
            0.10
        )
    )

    watermark_width = int(
        watermark.get(
            "width",
            500
        )
    )

    watermark_move_x = float(
        watermark.get(
            "move_distance_x",
            100
        )
    )

    watermark_move_y = float(
        watermark.get(
            "move_distance_y",
            50
        )
    )

    watermark_move_speed = float(
        watermark.get(
            "move_speed",
            0.015
        )
    )

    # ========================================================
    # VIDEO
    # ========================================================

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
    # PRINT INFORMATION
    # ========================================================

    print("\nSource:")
    print(hls_url)

    print("\nTarget video:")
    print(
        f"{width}x{height}"
    )

    # ========================================================
    # MAIN LOGO INFO
    # ========================================================

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
            f"Size: {logo_width}px"
        )

        print(
            f"Position: "
            f"{logo_x},{logo_y}"
        )

    else:

        print("Disabled")

    # ========================================================
    # WATERMARK INFO
    # ========================================================

    print("\nCenter Watermark:")

    if watermark_enabled:

        print("Enabled")

        print(
            f"Size: {watermark_width}px"
        )

        print(
            f"Opacity: {watermark_opacity}"
        )

        print(
            "Visibility: ALWAYS"
        )

        print(
            "Movement: CONTINUOUS"
        )

    else:

        print("Disabled")

    # ========================================================
    # AUDIO
    # ========================================================

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

    # ========================================================
    # VIDEO BASE
    # ========================================================

    video_filters = build_video_filter(
        config
    )

    # --------------------------------------------------------
    # Resize to exact 1920x1080.
    #
    # The source is scaled while preserving aspect ratio.
    # Crop is applied only when necessary.
    # --------------------------------------------------------

    video_resize = (
        f"scale={width}:{height}:"
        "force_original_aspect_ratio=increase,"
        f"crop={width}:{height}"
    )

    if video_filters:

        frame_filters = ",".join(
            video_filters
        )

        video_base = (
            "[0:v]"
            f"{video_resize},"
            f"{frame_filters}"
            "[base]"
        )

    else:

        video_base = (
            "[0:v]"
            f"{video_resize}"
            "[base]"
        )

    # ========================================================
    # FILTER COMPLEX
    # ========================================================

    filter_parts = []

    filter_parts.append(
        video_base
    )

    # ========================================================
    # MAIN LOGO
    # ========================================================

    if logo_enabled:

        logo_chain = (
            "[1:v]"
            "format=rgba,"
            f"scale={logo_width}:-1"
            "[logo]"
        )

        filter_parts.append(
            logo_chain
        )

        main_logo_overlay = (
            "[base][logo]"
            f"overlay={logo_x}:{logo_y}"
            "[v1]"
        )

        filter_parts.append(
            main_logo_overlay
        )

        current_video = "[v1]"

    else:

        current_video = "[base]"

    # ========================================================
    # CENTER WATERMARK
    # ========================================================

    if watermark_enabled:

        if logo_enabled:

            watermark_input_index = 2

        else:

            watermark_input_index = 1

        # ----------------------------------------------------
        # Same logo image.
        #
        # Larger than the corner logo.
        # Very transparent.
        # ALWAYS VISIBLE.
        # ----------------------------------------------------

        watermark_chain = (
            f"[{watermark_input_index}:v]"
            "format=rgba,"
            f"scale={watermark_width}:-1,"
            f"colorchannelmixer=aa={watermark_opacity}"
            "[wm]"
        )

        filter_parts.append(
            watermark_chain
        )

        # ----------------------------------------------------
        # Center position with gentle continuous movement.
        #
        # No enable expression.
        # Therefore the watermark never disappears.
        # ----------------------------------------------------

        watermark_x = (
            f"(W-w)/2+"
            f"sin(t*{watermark_move_speed})*"
            f"{watermark_move_x}"
        )

        watermark_y = (
            f"(H-h)/2+"
            f"cos(t*{watermark_move_speed})*"
            f"{watermark_move_y}"
        )

        moving_overlay = (
            f"{current_video}[wm]"
            "overlay="
            f"x='{watermark_x}':"
            f"y='{watermark_y}'"
            "[vout]"
        )

        filter_parts.append(
            moving_overlay
        )

    else:

        filter_parts.append(
            f"{current_video}"
            "null"
            "[vout]"
        )

    # ========================================================
    # AUDIO
    # ========================================================

    filter_parts.append(
        f"[0:a]{audio_filter}[aout]"
    )

    filter_complex = ";".join(
        filter_parts
    )

    # ========================================================
    # FFMPEG COMMAND
    # ========================================================

    command = [

        "ffmpeg",

        "-hide_banner",

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

        # ----------------------------------------------------
        # HLS source
        # ----------------------------------------------------

        "-i",
        hls_url
    ]

    # ========================================================
    # LOGO INPUTS
    # ========================================================

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

    elif watermark_enabled:

        command.extend([
            "-loop",
            "1",

            "-i",
            str(logo_path)
        ])

    # ========================================================
    # ENCODING
    # ========================================================

    command.extend([

        # ----------------------------------------------------
        # Test duration
        # ----------------------------------------------------

        "-t",
        "30",

        # ----------------------------------------------------
        # Filter graph
        # ----------------------------------------------------

        "-filter_complex",
        filter_complex,

        # ----------------------------------------------------
        # Video map
        # ----------------------------------------------------

        "-map",
        "[vout]",

        # ----------------------------------------------------
        # Audio map
        # ----------------------------------------------------

        "-map",
        "[aout]",

        # ----------------------------------------------------
        # Video encoding
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
        # Audio encoding
        # ----------------------------------------------------

        "-c:a",
        "aac",

        "-b:a",
        "128k",

        "-ar",
        "48000",

        # ----------------------------------------------------
        # MP4
        # ----------------------------------------------------

        "-movflags",
        "+faststart",

        "-y",

        str(output_file)
    ])

    # ========================================================
    # RUN
    # ========================================================

    print("\nStarting FFmpeg...")

    print(
        "Test duration: 30 seconds"
    )

    print(
        f"Output: {width}x{height}"
    )

    print(
        f"Main logo: {logo_width}px"
    )

    print(
        f"Center watermark: "
        f"{watermark_width}px / "
        f"{watermark_opacity * 100:.0f}% opacity / ALWAYS"
    )

    print(
        "Frame: semi-transparent 40px"
    )

    print(
        "\nAudio settings: UNCHANGED"
    )

    result = subprocess.run(
        command
    )

    # ========================================================
    # RESULT
    # ========================================================

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

    # ========================================================
    # VERIFY
    # ========================================================

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

    # ========================================================
    # SUCCESS
    # ========================================================

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

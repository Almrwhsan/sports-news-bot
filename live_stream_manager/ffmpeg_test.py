import json
import subprocess
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "config.json"


def load_config():
    with CONFIG_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


# ============================================================
# AUDIO FILTER
# ============================================================

def build_audio_filter(audio_config):
    """
    Build FFmpeg audio filter chain.

    Supports:
    - volume
    - bass
    - treble
    - clear
    - voice
    - echo

    The aecho filter uses named parameters because
    this is the correct FFmpeg syntax.
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

        # Correct FFmpeg aecho syntax.
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
# VIDEO FILTER
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
    # Logo
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
            260
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
    # Print test information
    # --------------------------------------------------------

    print("\nSource:")
    print(hls_url)

    print("\nOutput:")
    print(output_file)

    print("\nResolution:")
    print(
        f"{width}x{height}"
    )

    print("\nLogo:")

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
    # Build audio filter
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
    # Build video filter
    # --------------------------------------------------------

    video_filters = build_video_filter(
        config
    )

    video_base = "[0:v]"

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
    # Build complete filter_complex
    # --------------------------------------------------------

    if logo_enabled:

        logo_chain = (
            f"[1:v]"
            f"scale={logo_width}:-1"
            f"[logo]"
        )

        overlay_chain = (
            f"[base][logo]"
            f"overlay={logo_x}:{logo_y}"
            f"[vout]"
        )

        filter_complex = (
            f"{video_base};"
            f"{logo_chain};"
            f"{overlay_chain};"
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

        # Input
        "-i",
        hls_url
    ]

    # --------------------------------------------------------
    # Logo input
    # --------------------------------------------------------

    if logo_enabled:

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

        # Filters
        "-filter_complex",
        filter_complex,

        # Video
        "-map",
        "[vout]",

        # Audio
        "-map",
        "[aout]",

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

        # Audio encoding
        "-c:a",
        "aac",

        "-b:a",
        "128k",

        "-ar",
        "48000",

        # MP4
        "-movflags",
        "+faststart",

        "-y",

        str(output_file)
    ])

    # --------------------------------------------------------
    # Start FFmpeg
    # --------------------------------------------------------

    print("\nStarting FFmpeg...")

    print(
        "Test duration: 30 seconds"
    )

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


if __name__ == "__main__":
    raise SystemExit(
        main()
    )

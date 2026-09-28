import json
import subprocess
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "config.json"


def load_config():
    with CONFIG_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def build_audio_filter(audio_config):
    if not audio_config.get("enabled", True):
        return "anull"

    filters = []

    mode = audio_config.get("mode", "normal").lower()
    volume = float(audio_config.get("volume", 1.0))

    if volume != 1.0:
        filters.append(f"volume={volume}")

    if mode == "clear":
        filters.extend([
            "highpass=f=80",
            "lowpass=f=15000",
            "acompressor=threshold=-18dB:ratio=3:attack=20:release=250"
        ])

    elif mode == "bass":
        filters.append("bass=g=6:f=100")

    elif mode == "treble":
        filters.append("treble=g=6:f=5000")

    elif mode == "voice":
        filters.extend([
            "highpass=f=120",
            "lowpass=f=12000",
            "acompressor=threshold=-20dB:ratio=3:attack=10:release=200"
        ])

    bass = float(audio_config.get("bass", 0))
    treble = float(audio_config.get("treble", 0))

    if bass != 0:
        filters.append(f"bass=g={bass}:f=100")

    if treble != 0:
        filters.append(f"treble=g={treble}:f=5000")

    echo = audio_config.get("echo", {})

    # ---------------------------------------------------------
    # Echo
    # ---------------------------------------------------------
    # We do NOT use the aecho filter because it may not be
    # available in some FFmpeg builds.
    #
    # Instead:
    #   - Keep the original audio
    #   - Create a delayed copy
    #   - Create a second, weaker delayed copy
    #   - Mix all three together
    # ---------------------------------------------------------

    if echo.get("enabled", False):

        in_gain = float(echo.get("in_gain", 0.8))
        out_gain = float(echo.get("out_gain", 0.7))

        delays = str(
            echo.get("delays", "900|900")
        ).split("|")

        decays = str(
            echo.get("decays", "0.18|0.10")
        ).split("|")

        # Use the configured delay values when available.
        delay1 = int(float(delays[0])) if delays else 900

        if len(delays) > 1:
            delay2 = int(float(delays[1]))
        else:
            delay2 = delay1 * 2

        # Use configured decay values.
        decay1 = float(decays[0]) if decays else 0.18

        if len(decays) > 1:
            decay2 = float(decays[1])
        else:
            decay2 = 0.10

        # The values are intentionally kept moderate.
        # This prevents the echo from overpowering commentary.
        echo_gain1 = max(0.0, min(decay1 * out_gain, 1.0))
        echo_gain2 = max(0.0, min(decay2 * out_gain, 1.0))

        # Store the normal filters first.
        base_filters = filters.copy()

        if base_filters:
            base_audio = ",".join(base_filters)
            main_chain = (
                f"[0:a]{base_audio}[main]"
            )
        else:
            main_chain = "[0:a]anull[main]"

        # Build the delayed copies.
        echo_chain1 = (
            f"[main]"
            f"volume={echo_gain1},"
            f"adelay={delay1}|{delay1}"
            f"[echo1]"
        )

        echo_chain2 = (
            f"[main]"
            f"volume={echo_gain2},"
            f"adelay={delay2}|{delay2}"
            f"[echo2]"
        )

        # Mix original + echo 1 + echo 2.
        mix_chain = (
            "[main][echo1][echo2]"
            "amix=inputs=3:"
            "duration=longest:"
            "normalize=0"
            "[aout]"
        )

        return (
            f"{main_chain};"
            f"{echo_chain1};"
            f"{echo_chain2};"
            f"{mix_chain}"
        )

    return ",".join(filters) if filters else "anull"


def build_video_filter(config):
    overlay = config.get("ffmpeg", {}).get("overlay", {})
    frame = overlay.get("frame", {})

    filters = []

    if frame.get("enabled", True):
        width = int(frame.get("width", 8))
        color = frame.get("color", "0x8B0000")

        filters.append(
            f"drawbox="
            f"x=0:y=0:w=iw:h=ih:"
            f"color={color}:t={width}"
        )

    return filters


def main():
    print("=" * 70)
    print("FFMPEG GRAPHICS + AUDIO TEST")
    print("=" * 70)

    config = load_config()

    streams = config.get("streams", [])

    if not streams:
        print("ERROR: No streams configured.")
        return 1

    stream = next(
        (
            item
            for item in streams
            if item.get("enabled", False)
        ),
        None
    )

    if not stream:
        print("ERROR: No enabled stream found.")
        return 1

    hls_url = stream.get("stream_url")

    if not hls_url:
        print("ERROR: HLS URL is missing.")
        return 1

    ffmpeg_config = config.get("ffmpeg", {})
    overlay = ffmpeg_config.get("overlay", {})
    audio_config = ffmpeg_config.get("audio", {})
    video_config = ffmpeg_config.get("video", {})

    output_file = (
        BASE_DIR / "ffmpeg_graphics_test.mp4"
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

    position = overlay.get(
        "logo_position",
        {}
    )

    logo_x = int(
        position.get(
            "x",
            35
        )
    )

    logo_y = int(
        position.get(
            "y",
            35
        )
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

    print("\nSource:")
    print(hls_url)

    print("\nOutput:")
    print(output_file)

    print("\nResolution:")
    print(f"{width}x{height}")

    print("\nLogo:")

    if logo_enabled:

        if not logo_path.exists():
            print(
                "ERROR: Logo file not found:"
            )
            print(logo_path)
            return 1

        print("Enabled")
        print(
            f"Path: {logo_path}"
        )
        print(
            f"Width: {logo_width}"
        )
        print(
            f"Position: {logo_x},{logo_y}"
        )

    else:
        print("Disabled")

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
    print(audio_filter)

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
            "[0:v]null[base]"
        )

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

        # If the audio filter contains its own
        # filter_complex chains, use it directly.
        if ";" in audio_filter:

            filter_complex = (
                f"{video_base};"
                f"{logo_chain};"
                f"{overlay_chain};"
                f"{audio_filter}"
            )

        else:

            filter_complex = (
                f"{video_base};"
                f"{logo_chain};"
                f"{overlay_chain};"
                f"[0:a]{audio_filter}[aout]"
            )

    else:

        if ";" in audio_filter:

            filter_complex = (
                f"{video_base}[vout];"
                f"{audio_filter}"
            )

        else:

            filter_complex = (
                f"{video_base}[vout];"
                f"[0:a]{audio_filter}[aout]"
            )

    command = [
        "ffmpeg",
        "-hide_banner",

        "-reconnect",
        "1",

        "-reconnect_streamed",
        "1",

        "-reconnect_delay_max",
        "5",

        "-i",
        hls_url
    ]

    if logo_enabled:

        command.extend([
            "-i",
            str(logo_path)
        ])

    command.extend([
        "-t",
        "30",

        "-filter_complex",
        filter_complex,

        "-map",
        "[vout]",

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
        str(fps * 2),

        "-c:a",
        "aac",

        "-b:a",
        "128k",

        "-ar",
        "48000",

        "-movflags",
        "+faststart",

        "-y",

        str(output_file)
    ])

    print("\nStarting FFmpeg...")
    print("Test duration: 30 seconds")

    result = subprocess.run(
        command
    )

    print("\n" + "=" * 70)

    if result.returncode != 0:

        print(
            "FFMPEG GRAPHICS TEST FAILED"
        )

        print("=" * 70)

        print(
            f"FFmpeg exit code: "
            f"{result.returncode}"
        )

        return result.returncode

    if not output_file.exists():

        print(
            "TEST FAILED: "
            "Output file was not created."
        )

        return 1

    size_mb = (
        output_file.stat().st_size
        / (1024 * 1024)
    )

    print(
        "FFMPEG GRAPHICS TEST SUCCESSFUL"
    )

    print("=" * 70)

    print("\nOutput file:")
    print(output_file)

    print(
        f"\nFile size: "
        f"{size_mb:.2f} MB"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )

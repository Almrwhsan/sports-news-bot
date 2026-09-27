import json
import subprocess
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "config.json"


def load_config():
    with CONFIG_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def main():

    print("=" * 70)
    print("FFMPEG HLS TEST")
    print("=" * 70)

    config = load_config()

    streams = config.get(
        "streams",
        []
    )

    if not streams:
        print("No streams configured.")
        return

    stream = streams[0]

    stream_url = stream["stream_url"]

    output_file = (
        BASE_DIR / "ffmpeg_test_output.mp4"
    )

    print(
        f"\nSource:\n{stream_url}"
    )

    print(
        "\nStarting FFmpeg..."
    )

    command = [
        "ffmpeg",
        "-y",
        "-reconnect",
        "1",
        "-reconnect_streamed",
        "1",
        "-reconnect_delay_max",
        "5",
        "-i",
        stream_url,
        "-t",
        "20",
        "-c",
        "copy",
        "-movflags",
        "+faststart",
        str(output_file)
    ]

    print(
        "\nCommand:"
    )

    print(
        " ".join(command)
    )

    result = subprocess.run(
        command
    )

    print("\n")

    if result.returncode == 0:

        print("=" * 70)
        print("FFMPEG TEST SUCCESSFUL")
        print("=" * 70)

        print(
            f"\nOutput file:"
        )

        print(
            output_file
        )

        if output_file.exists():

            size_mb = (
                output_file.stat().st_size
                / (1024 * 1024)
            )

            print(
                f"\nFile size: {size_mb:.2f} MB"
            )

    else:

        print("=" * 70)
        print("FFMPEG TEST FAILED")
        print("=" * 70)

        print(
            f"\nFFmpeg exit code: "
            f"{result.returncode}"
        )


if __name__ == "__main__":
    main()

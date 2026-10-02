#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import os
import signal
import subprocess
import sys
import time

# ==========================================
# Logging Setup
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("FacebookLiveStreamer")

# ==========================================
# Helper & Utility Functions
# ==========================================
def load_config(config_path="config.json"):
    """Loads configuration settings from config.json."""
    if not os.path.exists(config_path):
        logger.error(f"Configuration file '{config_path}' not found!")
        sys.exit(1)
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to parse '{config_path}': {e}")
        sys.exit(1)

def get_audio_preset_filters(preset_name):
    """Returns FFmpeg filter chain strings for defined audio presets."""
    presets = {
        "young": "equalizer=f=60:width_type=h:width=100:g=3,equalizer=f=1000:width_type=h:width=200:g=-2,equalizer=f=3000:width_type=h:width=500:g=4",
        "clear": "highpass=f=80,lowpass=f=12000,equalizer=f=3000:width_type=h:width=1000:g=3",
        "bass": "equalizer=f=80:width_type=h:width=100:g=6,equalizer=f=200:width_type=h:width=150:g=3",
        "treble": "equalizer=f=4000:width_type=h:width=1000:g=5,equalizer=f=8000:width_type=h:width=2000:g=4",
        "voice": "highpass=f=100,lowpass=f=8000,equalizer=f=300:width_type=h:width=200:g=-3,equalizer=f=2500:width_type=h:width=800:g=4"
    }
    return presets.get(preset_name, "")

def build_filter_complex(cfg):
    """Constructs complex FFmpeg filter graphs for audio and video processing."""
    ffmpeg_cfg = cfg.get("ffmpeg", {})
    overlay_cfg = ffmpeg_cfg.get("overlay", {})
    audio_cfg = ffmpeg_cfg.get("audio", {})
    video_cfg = ffmpeg_cfg.get("video", {})

    width = video_cfg.get("width", 1920)
    height = video_cfg.get("height", 1080)

    # --- Video Filters Chain ---
    v_filters = []
    # Dynamic aspect ratio scaling with black padding
    v_filters.append(
        f"scale=w={width}:h={height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black"
    )

    # Decorative Border Frame
    frame_cfg = overlay_cfg.get("frame", {})
    if frame_cfg.get("enabled", False):
        fw = frame_cfg.get("width", 8)
        color = frame_cfg.get("color", "0x8B0000")
        opacity = frame_cfg.get("opacity", 0.35)
        v_filters.append(
            f"drawbox=x=0:y=0:w=iw:h=ih:color={color}@{opacity}:t={fw}"
        )

    # LIVE Badge Overlay
    live_cfg = overlay_cfg.get("live_badge", {})
    if live_cfg.get("enabled", False):
        text = live_cfg.get("text", "LIVE")
        lx = live_cfg.get("x", 35)
        ly = live_cfg.get("y", 220)
        font_size = live_cfg.get("font_size", 42)
        font_color = live_cfg.get("font_color", "white")
        box_color = live_cfg.get("box_color", "0x8B0000")
        box_opacity = live_cfg.get("box_opacity", 0.85)

        font_file_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        font_param = f":fontfile='{font_file_path}'" if os.path.exists(font_file_path) else ""

        v_filters.append(
            f"drawtext=text='{text}'{font_param}:x={lx}:y={ly}:fontsize={font_size}:"
            f"fontcolor={font_color}:box=1:boxcolor={box_color}@{box_opacity}:boxborderw=10"
        )

    video_filters_str = ",".join(v_filters)

    # --- Audio Filters Chain ---
    a_filters = []
    if audio_cfg.get("enabled", True):
        # Preset equalizer
        preset_str = get_audio_preset_filters(audio_cfg.get("mode", "clear"))
        if preset_str:
            a_filters.append(preset_str)

        # Volume control
        vol = audio_cfg.get("volume", 1.0)
        if vol != 1.0:
            a_filters.append(f"volume={vol}")

        # Manual Bass & Treble Adjustments
        bass_g = audio_cfg.get("bass", 0)
        if bass_g != 0:
            a_filters.append(f"equalizer=f=100:width_type=h:width=200:g={bass_g}")
        
        treble_g = audio_cfg.get("treble", 0)
        if treble_g != 0:
            a_filters.append(f"equalizer=f=8000:width_type=h:width=2000:g={treble_g}")

        # Echo/Reverb Effects
        echo_cfg = audio_cfg.get("echo", {})
        if echo_cfg.get("enabled", False):
            ig = echo_cfg.get("in_gain", 0.8)
            og = echo_cfg.get("out_gain", 0.9)
            delays = echo_cfg.get("delays", "1200|1200")
            decays = echo_cfg.get("decays", "0.25|0.15")
            a_filters.append(f"aecho={ig}:{og}:{delays}:{decays}")

    audio_filters_str = ",".join(a_filters) if a_filters else "anull"

    # --- Image Overlays (Logo & Watermark) ---
    logo_file = overlay_cfg.get("logo", "assets/logo.png")
    overlay_enabled = overlay_cfg.get("enabled", True) and os.path.exists(logo_file)

    if not overlay_enabled:
        filter_complex = f"[0:v]{video_filters_str}[vout];[0:a]{audio_filters_str}[aout]"
        return filter_complex, False, None

    # Overlays logic
    logo_w = overlay_cfg.get("logo_width", 220)
    logo_pos = overlay_cfg.get("logo_position", {"x": 1660, "y": 35})
    logo_x = logo_pos.get("x", 1660)
    logo_y = logo_pos.get("y", 35)

    wm_cfg = overlay_cfg.get("watermark", {})
    wm_enabled = wm_cfg.get("enabled", False)

    if wm_enabled:
        wm_w = wm_cfg.get("width", 500)
        wm_op = wm_cfg.get("opacity", 0.10)
        dx = wm_cfg.get("move_distance_x", 100)
        dy = wm_cfg.get("move_distance_y", 50)
        speed = wm_cfg.get("move_speed", 0.015)

        center_x = (width - wm_w) / 2
        center_y = (height - (wm_w * 0.5)) / 2  # Approximate proportional height
        
        wm_x = f"'{center_x} + {dx}*sin(t*{speed})'"
        wm_y = f"'{center_y} + {dy}*cos(t*{speed})'"

        # Split input image [1:v] cleanly into two streams to avoid parser bugs
        filter_complex = (
            f"[1:v]split=2[logo_in][wm_in];"
            f"[logo_in]format=rgba,scale={logo_w}:-1[logo];"
            f"[wm_in]format=rgba,scale={wm_w}:-1,colorchannelmixer=aa={wm_op}[wm];"
            f"[0:v]{video_filters_str}[base];"
            f"[base][logo]overlay=x={logo_x}:y={logo_y}[cornered];"
            f"[cornered][wm]overlay=x={wm_x}:y={wm_y}[vout];"
            f"[0:a]{audio_filters_str}[aout]"
        )
    else:
        filter_complex = (
            f"[1:v]format=rgba,scale={logo_w}:-1[logo];"
            f"[0:v]{video_filters_str}[base];"
            f"[base][logo]overlay=x={logo_x}:y={logo_y}[vout];"
            f"[0:a]{audio_filters_str}[aout]"
        )

    return filter_complex, True, logo_file

def build_ffmpeg_command(stream_url, rtmps_destination, cfg):
    """Generates complete FFmpeg CLI command with all arguments."""
    ffmpeg_cfg = cfg.get("ffmpeg", {})
    video_cfg = ffmpeg_cfg.get("video", {})
    headers_cfg = cfg.get("headers", {})

    # Build custom HTTP Headers for HLS ingestion
    header_lines = [f"{k}: {v}" for k, v in headers_cfg.items()]
    headers_str = "\r\n".join(header_lines) + "\r\n" if header_lines else ""

    filter_complex, has_overlay, logo_file = build_filter_complex(cfg)

    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "info"]

    # HLS Network Reconnect Settings
    cmd.extend([
        "-reconnect", "1",
        "-reconnect_at_eof", "1",
        "-reconnect_streamed", "1",
        "-reconnect_delay_max", "10"
    ])

    if headers_str:
        cmd.extend(["-headers", headers_str])

    # Video Input [0:v]
    cmd.extend(["-i", stream_url])

    # Overlay Image Input [1:v]
    if has_overlay and logo_file:
        cmd.extend(["-i", logo_file])

    # Apply Filter Complex
    cmd.extend(["-filter_complex", filter_complex])
    cmd.extend(["-map", "[vout]", "-map", "[aout]"])

    # Output Video Encoders & Encoding Parameters
    cmd.extend([
        "-c:v", "libx264",
        "-preset", video_cfg.get("preset", "veryfast"),
        "-b:v", video_cfg.get("bitrate", "5000k"),
        "-maxrate", video_cfg.get("maxrate", "5500k"),
        "-bufsize", video_cfg.get("bufsize", "10000k"),
        "-pix_fmt", "yuv420p",
        "-g", str(video_cfg.get("fps", 25) * 2),
        "-r", str(video_cfg.get("fps", 25))
    ])

    # Output Audio Encoders
    cmd.extend([
        "-c:a", "aac",
        "-b:a", "128k",
        "-ar", "44100",
        "-ac", "2"
    ])

    # RTMP Stream Output Format & Settings
    cmd.extend([
        "-f", "flv",
        "-flvflags", "no_duration_filesize",
        rtmps_destination
    ])

    return cmd

# ==========================================
# Process Runner & Life Cycle Management
# ==========================================
def run_stream():
    """Manages full lifecycle, subprocess execution, and auto-reconnection loop."""
    config = load_config()
    
    # Active stream selection
    streams = [s for s in config.get("streams", []) if s.get("enabled", True)]
    if not streams:
        logger.error("No enabled streams found in config.json!")
        sys.exit(1)

    selected_stream = streams[0]
    stream_url = selected_stream.get("stream_url")
    logger.info(f"Selected Stream: {selected_stream.get('name')} ({selected_stream.get('id')})")

    # Facebook Credentials
    rtmps_url = os.getenv("FACEBOOK_RTMPS_URL", "rtmps://live-api-s.facebook.com:443/rtmp/")
    stream_key = os.getenv("FACEBOOK_STREAM_KEY")

    if not stream_key:
        logger.error("FACEBOOK_STREAM_KEY environment variable is not set!")
        sys.exit(1)

    rtmps_destination = f"{rtmps_url.rstrip('/')}/{stream_key}"

    # Auto-restart Configurations
    auto_restart = config.get("auto_restart", {})
    restart_enabled = auto_restart.get("enabled", True)
    restart_delay = auto_restart.get("restart_delay_seconds", 5)
    max_restarts = auto_restart.get("max_restarts", 0)  # 0 = infinite
    max_delay = auto_restart.get("max_restart_delay_seconds", 60)

    restart_count = 0
    current_delay = restart_delay

    while True:
        cmd = build_ffmpeg_command(stream_url, rtmps_destination, config)
        logger.info("Starting FFmpeg broadcast process...")
        
        start_time = time.time()
        process = None

        try:
            process = subprocess.Popen(cmd)

            # Signal handler for graceful shutdown
            def signal_handler(sig, frame):
                logger.info("Termination signal received. Stopping stream...")
                if process:
                    process.terminate()
                sys.exit(0)

            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

            # Block until FFmpeg terminates
            return_code = process.wait()
            logger.warning(f"FFmpeg process terminated with exit code: {return_code}")

        except Exception as e:
            logger.error(f"Error running FFmpeg process: {e}")

        # Reset retry backoff delay if stream ran successfully for > 5 minutes
        if time.time() - start_time > 300:
            restart_count = 0
            current_delay = restart_delay

        if not restart_enabled:
            logger.info("Auto-restart is disabled. Exiting program.")
            break

        restart_count += 1
        if max_restarts > 0 and restart_count > max_restarts:
            logger.error(f"Exceeded maximum restart limit ({max_restarts}). Exiting.")
            break

        logger.info(f"Reconnecting in {current_delay} seconds... (Attempt {restart_count})")
        time.sleep(current_delay)

        # Exponential backoff logic
        current_delay = min(current_delay * 2, max_delay)

# ==========================================
# Main Execution Entry Point
# ==========================================
if __name__ == "__main__":
    run_stream()

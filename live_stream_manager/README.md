# Live Stream Manager

A Python-based HLS/M3U8 live streaming management system.

## Current Version

1.0.0

## Current Features

- HLS Master Playlist detection
- HLS Variant Playlist detection
- Multiple stream configuration
- Media segment detection
- Media segment health testing
- HTTP status monitoring
- Configurable User-Agent
- Configurable Referer
- Automatic M3U playlist generation
- Logging
- Healthy/Unhealthy stream detection
- Designed for future FFmpeg and Facebook Live integration

## Project Structure

```text
live_stream_manager/
│
├── config.json
├── stream_manager.py
├── live_playlist.m3u
├── requirements.txt
├── README.md
│
└── logs/
    └── stream_manager.log

# Live Stream Manager

A standalone Python project for managing authorized HLS/M3U8 live streams.

## Current Features

- Read stream settings from `config.json`
- Validate HLS/M3U8 URLs
- Test HTTP access to the HLS source
- Support authorized HTTP headers
- Generate an M3U playlist automatically
- Prepare the playlist for VLC
- Keep Facebook integration disabled during testing

## Project Structure

```text
live_stream_manager/
├── config.json
├── stream_manager.py
├── live_playlist.m3u
├── requirements.txt
└── README.md

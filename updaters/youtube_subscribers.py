#!/usr/bin/env python3
"""
YouTube Subscribers Updater

Fetches subscriber count from YouTube using yt-dlp.
No API key required.
"""

import os
import json
import yaml
import subprocess
from datetime import datetime


def get_channel_stats(channel_url: str) -> dict | None:
    """Fetch channel stats using yt-dlp."""
    try:
        # Use yt-dlp to get metadata from the first video (includes channel info)
        result = subprocess.run(
            [
                "yt-dlp",
                "--dump-json",
                "--playlist-items", "1",
                f"{channel_url}/videos",
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.stdout:
            # Find the first valid JSON line (skip warnings)
            for line in result.stdout.split("\n"):
                line = line.strip()
                if line.startswith("{"):
                    try:
                        data = json.loads(line)
                        return {
                            "channel_title": data.get("channel", data.get("uploader", "Unknown")),
                            "subscribers": data.get("channel_follower_count", 0),
                            "channel_id": data.get("channel_id", ""),
                        }
                    except json.JSONDecodeError:
                        continue

        if result.stderr:
            print(f"yt-dlp warnings: {result.stderr[:500]}")

    except subprocess.TimeoutExpired:
        print("Timeout fetching YouTube data")
    except FileNotFoundError:
        print("Error: yt-dlp not found. Install with: pip install yt-dlp")
    except Exception as e:
        print(f"Error: {e}")

    return None


def update(config: dict) -> bool:
    """
    Fetch YouTube subscriber count and save to YAML file.

    Args:
        config: Dictionary with 'channel' (handle or URL) and 'output_file' keys.

    Returns:
        True if updated, False if skipped or failed.
    """
    channel = config.get("channel")
    output_file = config.get("output_file", "data/youtube_subscribers.yml")

    if not channel:
        print("Error: Please set 'channel' (handle like @vincenttalk) in config.yml")
        return False

    today = datetime.now().strftime("%Y-%m-%d")

    # Load existing data
    existing_data = {}
    if os.path.exists(output_file):
        try:
            with open(output_file, "r") as f:
                existing_data = yaml.safe_load(f) or {}
            last_updated = existing_data.get("metadata", {}).get("last_updated")
            if last_updated == today:
                print("YouTube subscribers already updated today. Skipping.")
                return False
        except Exception as e:
            print(f"Warning: Could not read existing data: {e}")

    # Build channel URL
    if channel.startswith("http"):
        channel_url = channel
    elif channel.startswith("@"):
        channel_url = f"https://www.youtube.com/{channel}"
    else:
        channel_url = f"https://www.youtube.com/@{channel}"

    print(f"Fetching stats from: {channel_url}")
    stats = get_channel_stats(channel_url)

    if not stats:
        print("Error: Could not fetch channel statistics")
        return False

    print(f"  Channel: {stats['channel_title']}")
    print(f"  Subscribers: {stats['subscribers']:,}")

    # Build output data
    history = existing_data.get("history", {})
    history[today] = {
        "subscribers": stats["subscribers"],
    }

    output_data = {
        "metadata": {
            "last_updated": today,
            "channel": channel,
            "channel_url": channel_url,
            "channel_title": stats["channel_title"],
            "channel_id": stats.get("channel_id", ""),
            "total_days": len(history),
            "latest_subscribers": stats["subscribers"],
        },
        "history": dict(sorted(history.items())),
    }

    # Save to file
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    try:
        with open(output_file, "w") as f:
            yaml.dump(output_data, f, width=1000, sort_keys=False, allow_unicode=True)
        print(f"Saved to {output_file}")
        return True
    except Exception as e:
        print(f"Error saving file: {e}")
        return False


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        test_config = {
            "channel": sys.argv[1],
            "output_file": "data/youtube_subscribers.yml",
        }
        update(test_config)
    else:
        print("Usage: python youtube_subscribers.py <@handle or channel_url>")
        print("Example: python youtube_subscribers.py @vincenttalk")

#!/usr/bin/env python3
"""
YouTube Subscribers Updater

Fetches subscriber count from YouTube using yt-dlp.
No API key required.
"""

import os
import json
import logging
import yaml
import subprocess
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_result

logger = logging.getLogger(__name__)


def _is_none(result):
    return result is None


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_result(_is_none),
    before_sleep=lambda rs: logger.info("Retrying YouTube fetch (attempt %d)...", rs.attempt_number + 1),
)
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
            logger.warning("yt-dlp warnings: %s", result.stderr[:500])

    except subprocess.TimeoutExpired:
        logger.error("Timeout fetching YouTube data")
    except FileNotFoundError:
        logger.error("yt-dlp not found. Install with: pip install yt-dlp")
        raise  # Don't retry if yt-dlp is not installed
    except Exception as e:
        logger.error("Error: %s", e)

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
        logger.error("Please set 'channel' (handle like @vincenttalk) in config.yml")
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
                logger.info("YouTube subscribers already updated today. Skipping.")
                return False
        except Exception as e:
            logger.warning("Could not read existing data: %s", e)

    # Build channel URL
    if channel.startswith("http"):
        channel_url = channel
    elif channel.startswith("@"):
        channel_url = f"https://www.youtube.com/{channel}"
    else:
        channel_url = f"https://www.youtube.com/@{channel}"

    logger.info("Fetching stats from: %s", channel_url)
    stats = get_channel_stats(channel_url)

    if not stats:
        logger.error("Could not fetch channel statistics")
        return False

    logger.info("  Channel: %s", stats["channel_title"])
    logger.info("  Subscribers: %s", f"{stats['subscribers']:,}")

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
        logger.info("Saved to %s", output_file)
        return True
    except Exception as e:
        logger.error("Error saving file: %s", e)
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
        logger.info("Usage: python youtube_subscribers.py <@handle or channel_url>")
        logger.info("Example: python youtube_subscribers.py @vincenttalk")

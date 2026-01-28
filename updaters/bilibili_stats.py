#!/usr/bin/env python3
"""
Bilibili Stats Updater

Fetches follower count, views, and other stats from Bilibili and saves to YAML.
"""

import os
import yaml
import requests
from datetime import datetime


def get_user_stats(mid: str) -> dict | None:
    """Fetch user stats from Bilibili public API."""
    # User relation stats (followers, following)
    stat_url = f"https://api.bilibili.com/x/relation/stat?vmid={mid}"
    # User card API (username, level, etc.)
    card_url = f"https://api.bilibili.com/x/web-interface/card?mid={mid}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Referer": "https://space.bilibili.com/",
    }

    try:
        # Get follower stats
        stat_resp = requests.get(stat_url, headers=headers, timeout=15)
        stat_resp.raise_for_status()
        stat_data = stat_resp.json()

        if stat_data.get("code") != 0:
            print(f"Error from stat API: {stat_data.get('message')}")
            return None

        # Get user card (name, level, etc.)
        card_resp = requests.get(card_url, headers=headers, timeout=15)
        card_resp.raise_for_status()
        card_data = card_resp.json()

        stat_info = stat_data.get("data", {})
        card_info = card_data.get("data", {}).get("card", {})
        level_info = card_info.get("level_info", {})

        return {
            "username": card_info.get("name", "Unknown"),
            "followers": stat_info.get("follower", 0),
            "following": stat_info.get("following", 0),
            "level": level_info.get("current_level", 0),
        }

    except Exception as e:
        print(f"Error fetching Bilibili stats: {e}")
        return None


def update(config: dict) -> bool:
    """
    Fetch Bilibili user stats and save to YAML file.

    Args:
        config: Dictionary with 'mid' (user ID) and 'output_file' keys.

    Returns:
        True if updated, False if skipped or failed.
    """
    mid = config.get("mid")
    output_file = config.get("output_file", "data/bilibili_stats.yml")

    if not mid:
        print("Error: Please set 'mid' (Bilibili user ID) in config.yml")
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
                print("Bilibili stats already updated today. Skipping.")
                return False
        except Exception as e:
            print(f"Warning: Could not read existing data: {e}")

    # Fetch stats
    print(f"Fetching Bilibili stats for user ID: {mid}")
    stats = get_user_stats(mid)

    if not stats:
        print("Error: Could not fetch Bilibili statistics")
        return False

    print(f"  Username: {stats['username']}")
    print(f"  Followers: {stats['followers']:,}")
    print(f"  Following: {stats['following']:,}")
    print(f"  Level: {stats['level']}")

    # Build output data
    history = existing_data.get("history", {})
    history[today] = {
        "followers": stats["followers"],
        "following": stats["following"],
        "level": stats["level"],
    }

    output_data = {
        "metadata": {
            "last_updated": today,
            "mid": str(mid),
            "username": stats["username"],
            "space_url": f"https://space.bilibili.com/{mid}",
            "total_days": len(history),
            "latest_followers": stats["followers"],
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
            "mid": sys.argv[1],
            "output_file": "data/bilibili_stats.yml",
        }
        update(test_config)
    else:
        print("Usage: python bilibili_stats.py <user_mid>")
        print("Example: python bilibili_stats.py 494163254")

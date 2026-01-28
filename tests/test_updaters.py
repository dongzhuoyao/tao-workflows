#!/usr/bin/env python3
"""
Tests for all updaters.

Run with: pytest tests/ -v
"""

import os
import sys
import tempfile
import yaml
import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from updaters import youtube_subscribers, bilibili_stats


class TestYouTubeUpdater:
    """Tests for YouTube subscriber updater."""

    def test_get_channel_stats_valid_handle(self):
        """Test fetching stats for a valid YouTube channel."""
        stats = youtube_subscribers.get_channel_stats("https://www.youtube.com/@vincenttalk/videos")

        assert stats is not None, "Should return stats for valid channel"
        assert "channel_title" in stats
        assert "subscribers" in stats
        assert isinstance(stats["subscribers"], int)
        assert stats["subscribers"] >= 0

    def test_get_channel_stats_invalid_handle(self):
        """Test fetching stats for an invalid YouTube channel."""
        stats = youtube_subscribers.get_channel_stats("https://www.youtube.com/@thischanneldoesnotexist12345xyz/videos")

        # Should return None or stats with 0 subscribers for invalid channel
        if stats is not None:
            assert stats["subscribers"] == 0 or stats["channel_title"] == "Unknown"

    def test_update_creates_file(self):
        """Test that update() creates the output file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "youtube_test.yml")
            config = {
                "channel": "@vincenttalk",
                "output_file": output_file,
            }

            result = youtube_subscribers.update(config)

            assert result is True, "Update should succeed"
            assert os.path.exists(output_file), "Output file should be created"

            with open(output_file) as f:
                data = yaml.safe_load(f)

            assert "metadata" in data
            assert "history" in data
            assert data["metadata"]["channel"] == "@vincenttalk"

    def test_update_skips_if_already_updated(self):
        """Test that update() skips if already updated today."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "youtube_test.yml")
            config = {
                "channel": "@vincenttalk",
                "output_file": output_file,
            }

            # First update
            result1 = youtube_subscribers.update(config)
            assert result1 is True

            # Second update should skip
            result2 = youtube_subscribers.update(config)
            assert result2 is False, "Should skip if already updated today"


class TestBilibiliUpdater:
    """Tests for Bilibili stats updater."""

    def test_get_user_stats_valid_mid(self):
        """Test fetching stats for a valid Bilibili user."""
        stats = bilibili_stats.get_user_stats("494163254")

        assert stats is not None, "Should return stats for valid user"
        assert "username" in stats
        assert "followers" in stats
        assert "following" in stats
        assert "level" in stats
        assert isinstance(stats["followers"], int)
        assert stats["followers"] >= 0

    def test_get_user_stats_invalid_mid(self):
        """Test fetching stats for an invalid Bilibili user."""
        stats = bilibili_stats.get_user_stats("999999999999")

        # Should return None or stats with issues for invalid user
        # Bilibili API may still return data with 0 followers
        if stats is not None:
            assert stats["followers"] == 0 or stats["username"] == "Unknown"

    def test_update_creates_file(self):
        """Test that update() creates the output file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "bilibili_test.yml")
            config = {
                "mid": "494163254",
                "output_file": output_file,
            }

            result = bilibili_stats.update(config)

            assert result is True, "Update should succeed"
            assert os.path.exists(output_file), "Output file should be created"

            with open(output_file) as f:
                data = yaml.safe_load(f)

            assert "metadata" in data
            assert "history" in data
            assert data["metadata"]["mid"] == "494163254"

    def test_update_skips_if_already_updated(self):
        """Test that update() skips if already updated today."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "bilibili_test.yml")
            config = {
                "mid": "494163254",
                "output_file": output_file,
            }

            # First update
            result1 = bilibili_stats.update(config)
            assert result1 is True

            # Second update should skip
            result2 = bilibili_stats.update(config)
            assert result2 is False, "Should skip if already updated today"


class TestConfigValidation:
    """Tests for configuration validation."""

    def test_youtube_missing_channel(self):
        """Test YouTube updater with missing channel config."""
        result = youtube_subscribers.update({})
        assert result is False

    def test_bilibili_missing_mid(self):
        """Test Bilibili updater with missing mid config."""
        result = bilibili_stats.update({})
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

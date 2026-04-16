#!/usr/bin/env python3
"""
tao-workflows: Automated data fetchers with GitHub Actions

Run specific updaters or all updaters.

Usage:
    python main.py              # Run all updaters
    python main.py scholar      # Run only scholar updater
    python main.py scholar github  # Run multiple updaters
"""

import sys
import logging
import yaml
from updaters import UPDATERS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("tao-workflows")


def load_config():
    """Load configuration from config.yml"""
    try:
        with open("config.yml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.error("config.yml not found")
        sys.exit(1)
    except yaml.YAMLError as e:
        logger.error("Error parsing config.yml: %s", e)
        sys.exit(1)


def run_updater(name: str, config: dict) -> bool:
    """Run a single updater by name"""
    if name not in UPDATERS:
        logger.error("Unknown updater: %s", name)
        logger.info("Available: %s", ", ".join(UPDATERS.keys()))
        return False

    updater_config = config.get(name, {})
    if not updater_config:
        logger.error("No config found for '%s' in config.yml", name)
        return False

    logger.info("=" * 50)
    logger.info("Running: %s", name)
    logger.info("=" * 50)

    try:
        return UPDATERS[name].update(updater_config)
    except Exception as e:
        logger.error("Error running %s: %s", name, e)
        return False


def main():
    config = load_config()

    # Determine which updaters to run
    if len(sys.argv) > 1:
        updaters_to_run = sys.argv[1:]
    else:
        updaters_to_run = list(UPDATERS.keys())

    results = {}
    for name in updaters_to_run:
        results[name] = run_updater(name, config)

    # Summary
    logger.info("=" * 50)
    logger.info("Summary")
    logger.info("=" * 50)
    for name, success in results.items():
        status = "OK" if success else "SKIPPED/FAILED"
        logger.info("  %s: %s", name, status)


if __name__ == "__main__":
    main()

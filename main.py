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
import yaml
from updaters import UPDATERS


def load_config():
    """Load configuration from config.yml"""
    try:
        with open("config.yml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print("Error: config.yml not found")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing config.yml: {e}")
        sys.exit(1)


def run_updater(name: str, config: dict) -> bool:
    """Run a single updater by name"""
    if name not in UPDATERS:
        print(f"Unknown updater: {name}")
        print(f"Available: {', '.join(UPDATERS.keys())}")
        return False

    updater_config = config.get(name, {})
    if not updater_config:
        print(f"No config found for '{name}' in config.yml")
        return False

    print(f"\n{'='*50}")
    print(f"Running: {name}")
    print(f"{'='*50}")

    try:
        return UPDATERS[name].update(updater_config)
    except Exception as e:
        print(f"Error running {name}: {e}")
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
    print(f"\n{'='*50}")
    print("Summary")
    print(f"{'='*50}")
    for name, success in results.items():
        status = "OK" if success else "SKIPPED/FAILED"
        print(f"  {name}: {status}")


if __name__ == "__main__":
    main()

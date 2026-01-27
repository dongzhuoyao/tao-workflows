#!/usr/bin/env python3
"""
Google Scholar Citations Updater

Fetches citation data from Google Scholar and saves to YAML.
"""

import os
import yaml
from datetime import datetime
from scholarly import scholarly


def update(config: dict) -> bool:
    """
    Fetch Google Scholar citations and save to YAML file.

    Args:
        config: Dictionary with 'user_id' and 'output_file' keys

    Returns:
        True if updated, False if skipped (already up-to-date)
    """
    user_id = config.get("user_id")
    output_file = config.get("output_file", "data/scholar_citations.yml")

    if not user_id or user_id == "YOUR_GOOGLE_SCHOLAR_ID":
        print("Error: Please set your Google Scholar user_id in config.yml")
        return False

    print(f"Fetching citations for Google Scholar ID: {user_id}")
    today = datetime.now().strftime("%Y-%m-%d")

    # Check if already updated today
    existing_data = {}
    if os.path.exists(output_file):
        try:
            with open(output_file, "r") as f:
                existing_data = yaml.safe_load(f) or {}
            last_updated = existing_data.get("metadata", {}).get("last_updated")
            if last_updated == today:
                print("Citations already updated today. Skipping.")
                return False
        except Exception as e:
            print(f"Warning: Could not read existing data: {e}")

    # Fetch from Google Scholar
    citation_data = {
        "metadata": {
            "last_updated": today,
            "scholar_id": user_id,
        },
        "papers": {}
    }

    scholarly.set_timeout(15)
    scholarly.set_retries(3)

    try:
        author = scholarly.search_author_id(user_id)
        author_data = scholarly.fill(author)
    except Exception as e:
        print(f"Error fetching author data: {e}")
        return False

    if not author_data or "publications" not in author_data:
        print("No publications found.")
        return False

    # Extract citation stats
    total_citations = 0
    for pub in author_data.get("publications", []):
        try:
            pub_id = pub.get("author_pub_id", "").split(":")[-1] if ":" in pub.get("author_pub_id", "") else pub.get("author_pub_id")
            if not pub_id:
                continue

            title = pub.get("bib", {}).get("title", "Unknown")
            year = pub.get("bib", {}).get("pub_year", "Unknown")
            citations = pub.get("num_citations", 0)
            total_citations += citations

            print(f"  {title[:50]}... ({year}) - {citations} citations")

            citation_data["papers"][pub_id] = {
                "title": title,
                "year": year,
                "citations": citations,
            }
        except Exception as e:
            print(f"Warning: Error processing publication: {e}")

    citation_data["metadata"]["total_citations"] = total_citations
    citation_data["metadata"]["paper_count"] = len(citation_data["papers"])

    # Check if data changed
    if existing_data.get("papers") == citation_data["papers"]:
        print("No changes in citation data.")
        citation_data["metadata"]["last_updated"] = today

    # Save to file
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    try:
        with open(output_file, "w") as f:
            yaml.dump(citation_data, f, width=1000, sort_keys=False, allow_unicode=True)
        print(f"Saved to {output_file}")
        print(f"Total: {total_citations} citations across {len(citation_data['papers'])} papers")
        return True
    except Exception as e:
        print(f"Error saving file: {e}")
        return False


if __name__ == "__main__":
    # For standalone testing
    import sys
    if len(sys.argv) > 1:
        test_config = {"user_id": sys.argv[1], "output_file": "data/scholar_citations.yml"}
        update(test_config)
    else:
        print("Usage: python scholar_citations.py <scholar_user_id>")

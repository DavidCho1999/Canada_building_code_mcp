#!/usr/bin/env python3
"""
CI version of check_updates.py - outputs to website/public/data/
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

import requests
from bs4 import BeautifulSoup


# Output path for website
OUTPUT_FILE = Path(__file__).parent.parent / "website" / "public" / "data" / "code_status.json"


CODE_SOURCES = {
    "NBC": {
        "url": "https://nrc.canada.ca/en/certifications-evaluations-standards/codes-canada/codes-canada-publications/national-building-code-canada-2025",
        "name": "National Building Code 2025",
    },
    "NFC": {
        "url": "https://nrc.canada.ca/en/certifications-evaluations-standards/codes-canada/codes-canada-publications/national-fire-code-canada-2025",
        "name": "National Fire Code 2025",
    },
    "NPC": {
        "url": "https://nrc.canada.ca/en/certifications-evaluations-standards/codes-canada/codes-canada-publications/national-plumbing-code-canada-2025",
        "name": "National Plumbing Code 2025",
    },
    "NECB": {
        "url": "https://nrc.canada.ca/en/certifications-evaluations-standards/codes-canada/codes-canada-publications/national-energy-code-canada-buildings-2025",
        "name": "National Energy Code 2025",
    },
    "OBC": {
        "url": "https://www.ontario.ca/laws/regulation/120332",
        "name": "Ontario Building Code",
    },
    "BCBC": {
        "url": "https://www2.gov.bc.ca/gov/content/industry/construction-industry/building-codes-standards/bc-codes/2024-bc-codes",
        "name": "BC Building Code 2024",
    },
    "ABC": {
        "url": "https://nrc.canada.ca/en/certifications-evaluations-standards/codes-canada/codes-canada-publications/national-building-code-2023-alberta-edition",
        "name": "Alberta Building Code 2023",
    },
}


def get_page_hash(url: str) -> Optional[str]:
    """Get hash of page content."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            for tag in soup(['script', 'style', 'meta', 'link']):
                tag.decompose()
            text = soup.get_text()
            return hashlib.md5(text.encode()).hexdigest()[:16]
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return None


def load_previous() -> Dict:
    """Load previous check results."""
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, 'r') as f:
            return json.load(f)
    return {}


def check_all():
    """Check all codes and save results."""
    previous = load_previous()
    previous_codes = previous.get("codes", {})

    results = {
        "lastChecked": datetime.now().strftime("%Y-%m-%d"),
        "codes": {},
        "hasUpdates": False,
    }

    updates = []

    for code, info in CODE_SOURCES.items():
        print(f"Checking {code}...")

        current_hash = get_page_hash(info["url"])
        previous_hash = previous_codes.get(code, {}).get("hash")

        status = "ok"
        if current_hash is None:
            status = "error"
        elif previous_hash and current_hash != previous_hash:
            status = "updated"
            updates.append(code)

        results["codes"][code] = {
            "name": info["name"],
            "hash": current_hash,
            "status": status,
        }

        print(f"  {code}: {status}")

    if updates:
        results["hasUpdates"] = True
        results["updatedCodes"] = updates
        print(f"\n*** Updates detected: {', '.join(updates)} ***")
    else:
        print("\nNo updates detected.")

    # Save results
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to: {OUTPUT_FILE}")

    return results


if __name__ == "__main__":
    check_all()

#!/usr/bin/env python3
"""
Check for updates to Canadian Building Codes.
Run periodically (e.g., weekly) to detect changes.
"""

import json
import hashlib
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

import requests
from bs4 import BeautifulSoup


# Where to store version info
VERSION_FILE = Path(__file__).parent.parent / "data" / "code_versions.json"


# Code sources and what to check
CODE_SOURCES = {
    # Ontario e-Laws (check "Last amendment" number)
    "OFC": {
        "type": "elaws",
        "url": "https://www.ontario.ca/laws/regulation/070213",
        "name": "Ontario Fire Code",
    },
    "OBC": {
        "type": "elaws",
        "url": "https://www.ontario.ca/laws/regulation/120332",
        "name": "Ontario Building Code",
    },

    # NRC Publications (check page content hash)
    "NBC": {
        "type": "nrc",
        "url": "https://nrc.canada.ca/en/certifications-evaluations-standards/codes-canada/codes-canada-publications/national-building-code-canada-2025",
        "name": "National Building Code",
    },
    "NFC": {
        "type": "nrc",
        "url": "https://nrc.canada.ca/en/certifications-evaluations-standards/codes-canada/codes-canada-publications/national-fire-code-canada-2025",
        "name": "National Fire Code",
    },
    "NPC": {
        "type": "nrc",
        "url": "https://nrc.canada.ca/en/certifications-evaluations-standards/codes-canada/codes-canada-publications/national-plumbing-code-canada-2025",
        "name": "National Plumbing Code",
    },
    "NECB": {
        "type": "nrc",
        "url": "https://nrc.canada.ca/en/certifications-evaluations-standards/codes-canada/codes-canada-publications/national-energy-code-canada-buildings-2025",
        "name": "National Energy Code",
    },

    # BC Government
    "BCBC": {
        "type": "bc_gov",
        "url": "https://www2.gov.bc.ca/gov/content/industry/construction-industry/building-codes-standards/bc-codes/2024-bc-codes",
        "name": "BC Building Code",
    },

    # Alberta (NRC)
    "ABC": {
        "type": "nrc",
        "url": "https://nrc.canada.ca/en/certifications-evaluations-standards/codes-canada/codes-canada-publications/national-building-code-2023-alberta-edition",
        "name": "Alberta Building Code",
    },
}


def load_versions() -> Dict:
    """Load saved version info."""
    if VERSION_FILE.exists():
        with open(VERSION_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_versions(versions: Dict):
    """Save version info."""
    VERSION_FILE.parent.mkdir(exist_ok=True)
    with open(VERSION_FILE, 'w') as f:
        json.dump(versions, f, indent=2)


def get_page_hash(url: str) -> Optional[str]:
    """Get hash of page content (for detecting any changes)."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 200:
            # Hash only text content, ignore dynamic elements
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Remove script/style tags
            for tag in soup(['script', 'style', 'meta', 'link']):
                tag.decompose()
            text = soup.get_text()
            return hashlib.md5(text.encode()).hexdigest()[:16]
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
    return None


def check_elaws(code: str, info: Dict, saved: Dict) -> Dict:
    """Check Ontario e-Laws for amendment number."""
    result = {
        "code": code,
        "name": info["name"],
        "url": info["url"],
        "checked": datetime.now().isoformat(),
        "status": "unknown",
    }

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        resp = requests.get(info["url"], headers=headers, timeout=30)

        if resp.status_code == 200:
            # e-Laws uses JavaScript, so we can't get the actual content
            # But we can check if the page loads
            result["status"] = "page_loads"
            result["note"] = "e-Laws requires JavaScript - manual check recommended"

            # Try to find any version info in the raw HTML
            if "Last amendment" in resp.text:
                match = re.search(r'Last amendment[:\s]*([^<]+)', resp.text)
                if match:
                    result["last_amendment"] = match.group(1).strip()

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    return result


def check_nrc(code: str, info: Dict, saved: Dict) -> Dict:
    """Check NRC page for changes."""
    result = {
        "code": code,
        "name": info["name"],
        "url": info["url"],
        "checked": datetime.now().isoformat(),
        "status": "unknown",
    }

    page_hash = get_page_hash(info["url"])

    if page_hash:
        result["hash"] = page_hash
        saved_hash = saved.get(code, {}).get("hash")

        if saved_hash is None:
            result["status"] = "first_check"
        elif saved_hash == page_hash:
            result["status"] = "no_change"
        else:
            result["status"] = "CHANGED"
            result["previous_hash"] = saved_hash
    else:
        result["status"] = "error"

    return result


def check_bc_gov(code: str, info: Dict, saved: Dict) -> Dict:
    """Check BC Government page for changes."""
    return check_nrc(code, info, saved)  # Same logic


def check_all():
    """Check all codes for updates."""
    print("=" * 60)
    print(f"Code Update Check - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    saved = load_versions()
    results = {}
    changes_found = []

    for code, info in CODE_SOURCES.items():
        print(f"\nChecking {code} ({info['name']})...")

        check_type = info["type"]
        if check_type == "elaws":
            result = check_elaws(code, info, saved)
        elif check_type == "nrc":
            result = check_nrc(code, info, saved)
        elif check_type == "bc_gov":
            result = check_bc_gov(code, info, saved)
        else:
            result = {"status": "unknown_type"}

        results[code] = result

        status = result.get("status", "unknown")
        if status == "CHANGED":
            print(f"  *** CHANGE DETECTED! ***")
            changes_found.append(code)
        elif status == "no_change":
            print(f"  No change")
        elif status == "first_check":
            print(f"  First check - baseline saved")
        else:
            print(f"  Status: {status}")

    # Save results
    save_versions(results)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if changes_found:
        print(f"\n!!! CHANGES DETECTED in: {', '.join(changes_found)} !!!")
        print("Please update the maps for these codes.")
    else:
        print("\nNo changes detected.")

    print(f"\nResults saved to: {VERSION_FILE}")

    return results


def main():
    check_all()


if __name__ == "__main__":
    main()

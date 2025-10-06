#!/usr/bin/env python3
"""
Query available versions of packages from jsDelivr CDN
"""

import json
import sys
from typing import Dict, List, Optional

import requests


def get_jsdelivr_versions(package_name: str, registry: str = "npm") -> Optional[Dict]:
    """
    Get available versions of a package from jsDelivr CDN

    Args:
        package_name: Name of the package (e.g., 'pyodide')
        registry: Package registry ('npm', 'gh' for GitHub)

    Returns:
        Dictionary with 'tags' and 'versions' keys, or None if not found
    """
    url = f"https://data.jsdelivr.com/v1/package/{registry}/{package_name}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {package_name}: {e}")
        return None


def print_versions(package_name: str, data: Dict):
    """Pretty print version information"""
    print(f"\n=== {package_name.upper()} ===")

    if "tags" in data:
        print("Tags:")
        for tag, version in data["tags"].items():
            print(f"  {tag}: {version}")

    if "versions" in data:
        versions = data["versions"]
        print(f"\nAvailable versions ({len(versions)} total):")

        # Show all versions for MicroPython packages
        for version in versions:
            print(f"  {version}")

        # Show example CDN URLs
        if versions:
            print(f"\nExample CDN URLs:")
            latest_version = versions[0]
            package_url = package_name.replace("@", "").replace("/", "%2F")
            print(f"  https://cdn.jsdelivr.net/npm/{package_name}@{latest_version}/micropython.mjs")
            print(f"  https://cdn.jsdelivr.net/npm/{package_name}@{latest_version}/micropython.js")
            print(f"  https://cdn.jsdelivr.net/npm/{package_name}@latest/micropython.mjs")


def main():
    packages = ["@micropython/micropython-webassembly-pyscript"]

    if len(sys.argv) > 1:
        packages = sys.argv[1:]

    for package in packages:
        data = get_jsdelivr_versions(package)
        if data:
            print_versions(package, data)
        else:
            print(f"Package '{package}' not found or error occurred")


if __name__ == "__main__":
    main()

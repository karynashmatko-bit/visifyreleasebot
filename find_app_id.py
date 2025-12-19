#!/usr/bin/env python3
"""
Script to find and validate App Store app IDs
"""

import requests
import sys
import json
from typing import Optional

def get_app_info(app_id: str) -> Optional[dict]:
    """Get app information from App Store using iTunes API"""
    try:
        url = f"https://itunes.apple.com/lookup?id={app_id}&country=us"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        if data.get('resultCount', 0) == 0:
            return None

        app_data = data['results'][0]
        return {
            'name': app_data['trackName'],
            'developer': app_data['artistName'],
            'version': app_data['version'],
            'app_id': app_id
        }

    except Exception as e:
        print(f"❌ Error fetching app {app_id}: {e}")
        return None

def search_apps_by_name(app_name: str) -> list:
    """Search for apps by name (limited functionality)"""
    try:
        # URL encode the app name
        from urllib.parse import quote
        encoded_name = quote(app_name)

        url = f"https://itunes.apple.com/search?term={encoded_name}&country=us&entity=software"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        results = []
        for app in data.get('results', [])[:5]:  # Show top 5 results
            results.append({
                'name': app['trackName'],
                'developer': app['artistName'],
                'app_id': str(app['trackId']),
                'version': app['version']
            })

        return results

    except Exception as e:
        print(f"❌ Error searching for '{app_name}': {e}")
        return []

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 find_app_id.py <app_id>           # Test specific app ID")
        print("  python3 find_app_id.py search <app_name>  # Search for apps by name")
        print()
        print("Examples:")
        print("  python3 find_app_id.py 544007664")
        print("  python3 find_app_id.py search 'Remini'")
        return

    if sys.argv[1] == "search" and len(sys.argv) >= 3:
        app_name = " ".join(sys.argv[2:])
        print(f"🔍 Searching for '{app_name}'...")

        results = search_apps_by_name(app_name)
        if results:
            print(f"\n✅ Found {len(results)} results:")
            for i, app in enumerate(results, 1):
                print(f"{i}. {app['name']} by {app['developer']}")
                print(f"   App ID: {app['app_id']}")
                print(f"   Current Version: {app['version']}")
                print()
        else:
            print("❌ No results found")

    else:
        app_id = sys.argv[1]
        print(f"🧪 Testing App ID: {app_id}")

        app_info = get_app_info(app_id)
        if app_info:
            print("✅ Valid app found!")
            print(f"   Name: {app_info['name']}")
            print(f"   Developer: {app_info['developer']}")
            print(f"   Version: {app_info['version']}")
        else:
            print("❌ Invalid app ID or app not found")

if __name__ == "__main__":
    main()

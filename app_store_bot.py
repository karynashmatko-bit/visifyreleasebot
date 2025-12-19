#!/usr/bin/env python3
"""
Slack Bot for monitoring App Store competitor releases
"""

import os
import time
import json
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import schedule
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class AppInfo:
    """Represents an App Store app"""
    app_id: str
    name: str
    developer: str
    current_version: str
    last_updated: datetime
    store_url: str
    release_notes: str = ""

class AppStoreMonitor:
    """Monitors App Store for app updates"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def get_app_info(self, app_id: str) -> Optional[AppInfo]:
        """
        Get app information from App Store
        Uses iTunes API which provides JSON data
        """
        try:
            # Use iTunes lookup API
            url = f"https://itunes.apple.com/lookup?id={app_id}&country=us"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get('resultCount', 0) == 0:
                logger.warning(f"No app found with ID: {app_id}")
                return None

            app_data = data['results'][0]

            # Parse release date
            release_date = datetime.fromisoformat(
                app_data['currentVersionReleaseDate'].replace('Z', '+00:00')
            )

            return AppInfo(
                app_id=app_id,
                name=app_data['trackName'],
                developer=app_data['artistName'],
                current_version=app_data['version'],
                last_updated=release_date,
                store_url=app_data['trackViewUrl'],
                release_notes=app_data.get('releaseNotes', '')
            )

        except Exception as e:
            logger.error(f"Error fetching app info for {app_id}: {e}")
            return None

class SlackNotifier:
    """Handles Slack notifications"""

    def __init__(self, token: str, channel: str):
        self.client = WebClient(token=token)
        self.channel = channel

    def send_consolidated_notification(self, updated_apps: List[AppInfo]):
        """Send consolidated notification for multiple app updates"""
        try:
            if not updated_apps:
                return

            # Count new releases vs updates
            new_releases = [app for app in updated_apps if hasattr(app, '_is_new_release') and app._is_new_release]
            updates = [app for app in updated_apps if not (hasattr(app, '_is_new_release') and app._is_new_release)]

            emoji = "🆕" if new_releases else "📱"
            title = f"{emoji} Competitor App Updates ({len(updated_apps)})"

            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": title
                    }
                }
            ]

            # Add each app update as a section
            for app_info in updated_apps:
                is_new = hasattr(app_info, '_is_new_release') and app_info._is_new_release
                app_emoji = "🆕" if is_new else "📱"

                # Create app section
                app_section = {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"{app_emoji} *{app_info.name}*\n{app_info.developer}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Version:* {app_info.current_version}\n*Updated:* {app_info.last_updated.strftime('%Y-%m-%d %H:%M UTC')}"
                        }
                    ]
                }

                # Add hyperlink to App Store (no preview)
                app_section["fields"].append({
                    "type": "mrkdwn",
                    "text": f"<{app_info.store_url}|📱 App Store>"
                })

                blocks.append(app_section)

                # Add release notes if available
                if app_info.release_notes and app_info.release_notes.strip():
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*What's New:*\n```{app_info.release_notes[:500]}{'...' if len(app_info.release_notes) > 500 else ''}```"
                        }
                    })

                # Add divider between apps
                if app_info != updated_apps[-1]:
                    blocks.append({"type": "divider"})

            message = {
                "channel": self.channel,
                "text": title,
                "blocks": blocks
            }

            response = self.client.chat_postMessage(**message)
            logger.info(f"Consolidated notification sent for {len(updated_apps)} app updates")

        except SlackApiError as e:
            logger.error(f"Error sending consolidated Slack notification: {e}")

    def send_notification(self, app_info: AppInfo, is_new_release: bool = False):
        """Send notification about app update (legacy method for backward compatibility)"""
        self.send_consolidated_notification([app_info])

class CompetitorMonitor:
    """Main bot class"""

    def __init__(self):
        self.app_monitor = AppStoreMonitor()
        self.slack_notifier = SlackNotifier(
            token=os.getenv('SLACK_BOT_TOKEN'),
            channel=os.getenv('SLACK_CHANNEL')
        )
        self.competitors_file = 'competitors.json'
        self.last_check_file = 'last_check.json'

        # Load competitor app IDs
        self.competitors = self.load_competitors()
        self.last_versions = self.load_last_check()

    def load_competitors(self) -> List[str]:
        """Load competitor app IDs from config file"""
        try:
            if os.path.exists(self.competitors_file):
                with open(self.competitors_file, 'r') as f:
                    data = json.load(f)
                    return data.get('app_ids', [])
            else:
                # Default competitors (example app IDs)
                return [
                    "544007664",  # YouTube
                    "389801252",  # Instagram
                    "835599320",  # TikTok
                ]
        except Exception as e:
            logger.error(f"Error loading competitors: {e}")
            return []

    def load_last_check(self) -> Dict[str, str]:
        """Load last known versions"""
        try:
            if os.path.exists(self.last_check_file):
                with open(self.last_check_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading last check: {e}")
            return {}

    def save_last_check(self):
        """Save current versions for next check"""
        try:
            with open(self.last_check_file, 'w') as f:
                json.dump(self.last_versions, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving last check: {e}")

    def check_for_updates(self):
        """Check all competitors for updates"""
        logger.info("Starting competitor check...")

        updated_apps = []

        for app_id in self.competitors:
            app_info = self.app_monitor.get_app_info(app_id)

            if not app_info:
                continue

            last_version = self.last_versions.get(app_id)

            if last_version != app_info.current_version:
                # Version changed - this is a new release!
                is_new_release = last_version is not None

                # Mark the app as new release for consolidated notification
                app_info._is_new_release = is_new_release
                updated_apps.append(app_info)

                # Update stored version
                self.last_versions[app_id] = app_info.current_version
                logger.info(f"Update found for {app_info.name}: {last_version} → {app_info.current_version}")
            else:
                logger.info(f"No update for {app_info.name} (still v{app_info.current_version})")

        # Send consolidated notification for all updates
        if updated_apps:
            self.slack_notifier.send_consolidated_notification(updated_apps)
            self.save_last_check()
            logger.info(f"Found updates for {len(updated_apps)} apps - consolidated notification sent")
        else:
            logger.info("No updates found for any competitors")

def main():
    """Main function"""
    # Check for required environment variables
    if not os.getenv('SLACK_BOT_TOKEN'):
        logger.error("SLACK_BOT_TOKEN environment variable not set")
        return

    if not os.getenv('SLACK_CHANNEL'):
        logger.error("SLACK_CHANNEL environment variable not set")
        return

    # Initialize monitor
    monitor = CompetitorMonitor()

    # Run initial check
    monitor.check_for_updates()

    # Schedule regular checks (every 60 minutes)
    schedule.every(60).minutes.do(monitor.check_for_updates)

    logger.info("Bot started. Checking for updates every 60 minutes...")

    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute for scheduled tasks

if __name__ == "__main__":
    main()

# App Store Competitor Release Monitor Bot

A Slack bot that monitors App Store releases from competitor apps and sends notifications when new versions are released.

## Features

- 🔔 **Real-time Notifications**: Get Slack notifications when competitors release new app versions
- 📱 **App Store Integration**: Uses Apple's iTunes API to fetch app information
- ⏰ **Scheduled Monitoring**: Automatically checks for updates every 4 hours
- 🎯 **Customizable Competitors**: Easy configuration of which apps to monitor
- 📊 **Version Tracking**: Tracks version changes and detects new releases

## Prerequisites

- Python 3.7+
- Slack workspace with admin access to create apps
- App Store app IDs of competitors you want to monitor

## Setup Instructions

### 1. Clone and Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create Slack App

1. Go to [Slack API](https://api.slack.com/apps)
2. Click "Create New App" → "From scratch"
3. Name your app (e.g., "App Store Monitor")
4. Select your workspace
5. Go to "OAuth & Permissions"
6. Add these Bot Token Scopes:
   - `chat:write` (Send messages)
   - `chat:write.public` (Send messages to public channels)
7. Install the app to your workspace
8. Copy the "Bot User OAuth Token" (starts with `xoxb-`)

### 3. Configure Environment Variables

1. Copy `env.example` to `.env`:
   ```bash
   cp env.example .env
   ```

2. Edit `.env` and add your Slack credentials:
   ```
   SLACK_BOT_TOKEN=xoxb-your-bot-token-here
   SLACK_CHANNEL=#your-notifications-channel
   ```

### 4. Configure Competitors

Edit `competitors.json` to add the App Store IDs of apps you want to monitor:

```json
{
  "app_ids": [
    "544007664",  // YouTube
    "389801252"   // Instagram
  ]
}
```

**How to find App Store IDs:**
1. Search for the app on the App Store
2. Copy the number after `id` in the URL
3. Example: `https://apps.apple.com/us/app/youtube/id544007664` → ID is `544007664`

Or use tools like: https://tools.applemediaservices.com/

### 5. Run the Bot

```bash
python app_store_bot.py
```

The bot will:
- Perform an initial check for all configured apps
- Send notifications for any new releases found
- Continue monitoring every 4 hours

## How It Works

1. **Data Collection**: Uses Apple's iTunes Lookup API to fetch app metadata
2. **Version Tracking**: Compares current versions with previously stored versions
3. **Change Detection**: Identifies when version numbers change (new releases)
4. **Notifications**: Sends formatted Slack messages with app details and store links

## Configuration Files

- `competitors.json`: List of App Store app IDs to monitor
- `last_check.json`: Automatically created to track last known versions
- `.env`: Slack credentials (copy from `env.example`)

## Example Slack Notification

```
🆕 Competitor App New Release

App: Instagram
Developer: Instagram, Inc.
Version: 123.0.1
Updated: 2024-01-15 14:30 UTC

Store Link: https://apps.apple.com/us/app/instagram/id389801252
```

## Troubleshooting

### Bot Not Sending Messages
- Verify your Slack bot token is correct
- Ensure the bot is added to the target channel
- Check that the channel name starts with `#`

### App Not Found Errors
- Double-check App Store IDs in `competitors.json`
- Ensure the app is available in the US App Store
- Some apps might have region restrictions

### Rate Limiting
- The bot checks every 4 hours to avoid API rate limits
- Apple's iTunes API is generally very permissive

## Development

### Adding New Features
- App monitoring logic: `AppStoreMonitor` class
- Slack notifications: `SlackNotifier` class
- Main bot logic: `CompetitorMonitor` class

### Testing
Run a quick test to verify everything works:
```bash
python -c "from app_store_bot import AppStoreMonitor; m = AppStoreMonitor(); print(m.get_app_info('544007664'))"
```

## Deployment

### Quick Start (Local)

1. **Clone and setup:**
   ```bash
   git clone https://github.com/karynashmatko-bit/visifyreleasebot.git
   cd visifyreleasebot
   cp env.example .env
   # Edit .env with your SLACK_BOT_TOKEN and SLACK_CHANNEL
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run:**
   ```bash
   python app_store_bot.py
   ```

### Docker Deployment

```bash
# Build and run with Docker
docker build -t appstore-monitor .
docker run -d --name appstore-monitor --env-file .env appstore-monitor

# Or use Docker Compose
docker-compose up -d
```

### Production Deployment Options

#### 1. **Systemd Service (Linux Servers)**
```bash
sudo python deploy.py local  # Choose option 1
```

#### 2. **Cloud VPS (AWS/DigitalOcean/Google Cloud)**
```bash
# On your cloud server:
git clone https://github.com/karynashmatko-bit/visifyreleasebot.git
cd visifyreleasebot
cp env.example .env
# Configure .env with your credentials
pip install -r requirements.txt
python app_store_bot.py  # Consider using screen/tmux/nohup
```

#### 3. **Railway/Render (PaaS)**
- Connect your GitHub repo
- Set environment variables in dashboard
- Deploy automatically on git push

### Deployment Script

Use the included deployment script for various options:

```bash
# Check system requirements
python deploy.py check

# Deploy locally
python deploy.py local

# Deploy with Docker
python deploy.py docker

# Deploy with Docker Compose
python deploy.py docker-compose

# Get cloud deployment info
python deploy.py cloud
```

### Environment Variables

Required environment variables in `.env`:
```bash
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_CHANNEL=#your-channel-name
LOG_LEVEL=INFO  # Optional: DEBUG, INFO, WARNING, ERROR
```

### Monitoring & Maintenance

- **Logs**: Bot logs to console, redirect to file for persistence
- **Health Check**: Test API connectivity every 5 minutes
- **Restart**: Bot automatically restarts on failure
- **Updates**: Pull latest code and restart to update

## License

This project is for educational and business intelligence purposes. Please respect app developers' privacy and terms of service.


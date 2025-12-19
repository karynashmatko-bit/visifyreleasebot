#!/usr/bin/env python3
"""
Deployment script for App Store Competitor Monitor Bot
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_requirements():
    """Check if required tools are installed"""
    required_tools = ['python3', 'pip']
    optional_tools = ['docker', 'docker-compose']

    print("🔍 Checking system requirements...")

    for tool in required_tools:
        try:
            subprocess.run([tool, '--version'], capture_output=True, check=True)
            print(f"✅ {tool} - OK")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"❌ {tool} - MISSING (required)")
            return False

    for tool in optional_tools:
        try:
            subprocess.run([tool, '--version'], capture_output=True, check=True)
            print(f"✅ {tool} - OK")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"⚠️  {tool} - Not found (optional)")

    return True

def setup_environment():
    """Set up environment variables"""
    print("\n📝 Setting up environment...")

    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please copy env.example to .env and configure your credentials:")
        print("  cp env.example .env")
        print("  # Then edit .env with your SLACK_BOT_TOKEN and SLACK_CHANNEL")
        return False

    # Load and validate environment
    from dotenv import load_dotenv
    load_dotenv()

    token = os.getenv('SLACK_BOT_TOKEN')
    channel = os.getenv('SLACK_CHANNEL')

    if not token:
        print("❌ SLACK_BOT_TOKEN not set in .env file")
        return False

    if not channel:
        print("❌ SLACK_CHANNEL not set in .env file")
        return False

    print("✅ Environment configured")
    return True

def deploy_local():
    """Deploy locally using systemd/screen/tmux"""
    print("\n🏠 Local Deployment Options:")
    print("1. Using systemd (Linux servers)")
    print("2. Using screen/tmux (persistent sessions)")
    print("3. Using nohup (basic background process)")

    choice = input("Choose deployment method (1-3): ").strip()

    if choice == '1':
        deploy_systemd()
    elif choice == '2':
        deploy_screen()
    elif choice == '3':
        deploy_nohup()
    else:
        print("❌ Invalid choice")

def deploy_systemd():
    """Deploy using systemd service"""
    print("\n🔧 Setting up systemd service...")

    service_content = f"""[Unit]
Description=App Store Competitor Monitor Bot
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'root')}
WorkingDirectory={os.getcwd()}
ExecStart={sys.executable} {os.getcwd()}/app_store_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

    service_path = "/etc/systemd/system/appstore-monitor.service"

    try:
        with open(service_path, 'w') as f:
            f.write(service_content)

        subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
        subprocess.run(['sudo', 'systemctl', 'enable', 'appstore-monitor'], check=True)
        subprocess.run(['sudo', 'systemctl', 'start', 'appstore-monitor'], check=True)

        print("✅ Service installed and started!")
        print("Check status: sudo systemctl status appstore-monitor")
        print("View logs: sudo journalctl -u appstore-monitor -f")

    except Exception as e:
        print(f"❌ Failed to setup systemd service: {e}")
        print("Manual setup required. Save the above content to /etc/systemd/system/appstore-monitor.service")

def deploy_screen():
    """Deploy using screen"""
    print("\n📺 Deploying with screen...")
    try:
        subprocess.run(['screen', '-dmS', 'appstore-monitor', sys.executable, 'app_store_bot.py'])
        print("✅ Bot started in screen session 'appstore-monitor'")
        print("Reattach: screen -r appstore-monitor")
        print("Detach: Ctrl+A, D")
    except FileNotFoundError:
        print("❌ screen not installed")
        print("Install: sudo apt install screen  # Ubuntu/Debian")
        print("        brew install screen      # macOS")

def deploy_nohup():
    """Deploy using nohup"""
    print("\n🔄 Deploying with nohup...")
    try:
        subprocess.run(['nohup', sys.executable, 'app_store_bot.py', '&'])
        print("✅ Bot started in background")
        print("Process ID saved to nohup.out")
        print("Monitor: tail -f nohup.out")
    except Exception as e:
        print(f"❌ Failed: {e}")

def deploy_docker():
    """Deploy using Docker"""
    print("\n🐳 Docker Deployment...")

    if not os.path.exists('Dockerfile'):
        print("❌ Dockerfile not found!")
        return

    try:
        # Build image
        print("Building Docker image...")
        subprocess.run(['docker', 'build', '-t', 'appstore-monitor', '.'], check=True)

        # Stop existing container
        subprocess.run(['docker', 'stop', 'appstore-monitor'], capture_output=True)
        subprocess.run(['docker', 'rm', 'appstore-monitor'], capture_output=True)

        # Run container
        env_file = '-env-file .env' if os.path.exists('.env') else ''
        cmd = f'docker run -d --name appstore-monitor --restart unless-stopped {env_file} -v $(pwd)/last_check.json:/app/last_check.json appstore-monitor'
        subprocess.run(cmd, shell=True, check=True)

        print("✅ Docker container deployed!")
        print("Check logs: docker logs -f appstore-monitor")
        print("Stop: docker stop appstore-monitor")

    except subprocess.CalledProcessError as e:
        print(f"❌ Docker deployment failed: {e}")

def deploy_docker_compose():
    """Deploy using Docker Compose"""
    print("\n🐳 Docker Compose Deployment...")

    if not os.path.exists('docker-compose.yml'):
        print("❌ docker-compose.yml not found!")
        return

    try:
        subprocess.run(['docker-compose', 'up', '-d', '--build'], check=True)
        print("✅ Docker Compose deployment successful!")
        print("Check logs: docker-compose logs -f")
        print("Stop: docker-compose down")

    except subprocess.CalledProcessError as e:
        print(f"❌ Docker Compose deployment failed: {e}")

def deploy_cloud():
    """Cloud deployment options"""
    print("\n☁️  Cloud Deployment Options:")
    print("1. AWS EC2 / Lightsail")
    print("2. Google Cloud Compute Engine")
    print("3. DigitalOcean Droplet")
    print("4. Railway / Render (PaaS)")
    print("5. Heroku")

    print("\n📋 General steps for any cloud provider:")
    print("1. Create a VPS instance (Ubuntu recommended)")
    print("2. SSH into the server")
    print("3. Clone your repository:")
    print(f"   git clone https://github.com/karynashmatko-bit/visifyreleasebot.git")
    print("4. Set up environment: cp env.example .env && nano .env")
    print("5. Install dependencies: pip install -r requirements.txt")
    print("6. Run: python app_store_bot.py")

    print("\n🔧 For production, consider:")
    print("- Process manager: systemd/pm2")
    print("- Monitoring: health checks")
    print("- Logs: centralized logging")
    print("- Backups: automated data backup")

def main():
    parser = argparse.ArgumentParser(description='Deploy App Store Competitor Monitor Bot')
    parser.add_argument('method', choices=['local', 'docker', 'docker-compose', 'cloud', 'check'],
                       help='Deployment method')
    parser.add_argument('--force', action='store_true', help='Skip confirmation prompts')

    args = parser.parse_args()

    print("🚀 App Store Competitor Monitor - Deployment Tool")
    print("=" * 50)

    if not check_requirements():
        sys.exit(1)

    if not setup_environment():
        sys.exit(1)

    if args.method == 'check':
        print("✅ All checks passed! Ready for deployment.")
        return

    if not args.force:
        confirm = input(f"\n⚠️  Ready to deploy using {args.method}? (y/N): ")
        if confirm.lower() not in ['y', 'yes']:
            print("Deployment cancelled.")
            return

    if args.method == 'local':
        deploy_local()
    elif args.method == 'docker':
        deploy_docker()
    elif args.method == 'docker-compose':
        deploy_docker_compose()
    elif args.method == 'cloud':
        deploy_cloud()

if __name__ == "__main__":
    main()

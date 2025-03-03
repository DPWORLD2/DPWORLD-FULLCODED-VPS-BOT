#!/bin/bash

echo "🚀 Starting Installation..."

read -p "Enter your Discord Bot Token: " BOT_TOKEN

echo "🔄 Updating system packages..."
apt update && apt upgrade -y

echo "📦 Installing required dependencies..."
apt install -y python3 python3-pip tmate curl wget

echo "🐍 Installing Python libraries..."
pip3 install discord asyncio

echo "📥 Downloading bot.py from GitHub..."
wget -O bot.py https://raw.githubusercontent.com/DPWORLD2/DPWORLD-FULLCODED-VPS-BOT/main/bot.py

echo "🔑 Updating bot.py with your token..."
sed -i "s/YOUR_BOT_TOKEN/$BOT_TOKEN/g" bot.py

echo "🤖 Starting Discord Bot..."
nohup python3 bot.py &

echo "✅ Installation Completed!"

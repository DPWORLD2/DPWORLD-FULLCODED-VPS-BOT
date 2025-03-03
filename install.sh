#!/bin/bash

echo "🚀 Starting Automated Installation..."

# Prompt for Bot Token
read -p "Enter your Discord Bot Token: " BOT_TOKEN

# Update System
echo "🔄 Updating system packages..."
apt update && apt upgrade -y

# Install Required Packages
echo "📦 Installing required dependencies..."
apt install -y python3 python3-pip docker docker-compose bc curl wget

# Install Python Dependencies
echo "🐍 Installing Python libraries..."
pip3 install discord docker asyncio

# Download bot.py from GitHub
echo "📥 Downloading bot.py from GitHub..."
wget -O bot.py https://raw.githubusercontent.com/DPWORLD2/DPWORLD-FULLCODED-VPS-BOT/main/bot.py

# Download Dockerfile from GitHub
echo "📥 Downloading Dockerfile from GitHub..."
wget -O Dockerfile https://raw.githubusercontent.com/DPWORLD2/DPWORLD-FULLCODED-VPS-BOT/main/Dockerfile

# Update Bot Token in bot.py
echo "🔑 Updating bot.py with your token..."
sed -i "s/YOUR_BOT_TOKEN/$BOT_TOKEN/g" bot.py

# Build Docker Image
echo "🐳 Building Docker image..."
docker build -t ubuntu-22.04-with-tmate .

# Start the Bot
echo "🤖 Starting Discord Bot..."
nohup python3 bot.py &

echo "✅ Installation Completed!"

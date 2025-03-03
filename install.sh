#!/bin/bash

echo "🚀 Starting Installation..."

# Prompt for Bot Token
read -p "Enter your Discord Bot Token: " BOT_TOKEN

# Update System
echo "🔄 Updating system packages..."
apt update && apt upgrade -y

# Install Required Packages
echo "📦 Installing required dependencies..."
apt install -y python3 python3-pip docker docker-compose bc

# Install Python Dependencies
echo "🐍 Installing Python libraries..."
pip3 install discord docker asyncio

# Update Bot Token in bot.py
echo "🔑 Updating bot.py with your token..."
sed -i "s/YOUR_BOT_TOKEN/$BOT_TOKEN/g" bot.py

# Start the Bot
echo "🤖 Starting Discord Bot..."
nohup python3 bot.py &

echo "✅ Installation Completed!"

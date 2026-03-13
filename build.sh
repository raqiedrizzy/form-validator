#!/bin/bash
# Build Script for Render Ubuntu Environment
echo "Starting build process..."

# Install Google Chrome
echo "Installing Google Chrome..."
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
apt-get update
apt-get install -y google-chrome-stable

# Install ChromeDriver
echo "Installing ChromeDriver..."
CHROME_VERSION=$(google-chrome --version | cut -d " " -f3 | cut -d "." -f1)
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}")
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/
chmod +x /usr/local/bin/chromedriver

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create logs directory
mkdir -p logs
touch logs/heartbeat.log

echo "Build completed successfully!"

#!/bin/bash
# Setup script for Streamlit Sharing deployment

# Install system dependencies
apt-get update
apt-get install -y python3-dev python3-pip

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
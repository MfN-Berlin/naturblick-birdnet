#!/bin/bash
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get -y install --no-install-recommends ffmpeg
apt-get clean
rm -rf /var/lib/apt/lists/*
pip install --no-cache-dir -r requirements.txt

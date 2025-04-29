#!/bin/bash

set -e

# 📦 Environment Variables
REQUIRED_NODE_MAJOR_VERSION=${REQUIRED_NODE_MAJOR_VERSION:-22}
REQUIRED_ELECTRON_VERSION=${REQUIRED_ELECTRON_VERSION:-36.0.0}
REQUIRED_ELECTRON_BUILDER_VERSION=${REQUIRED_ELECTRON_BUILDER_VERSION:-26.0.12}
APP_SPELLCHECK_LANGS=${APP_SPELLCHECK_LANGS:-en-US,pt-BR}
APP_USERDATA=${APP_USERDATA:-$(pwd)/user-data/$(whoami)}
APP_LANG=${APP_LANG:-pt-BR}

# 📂 Prepare Directories
echo "📂 Creating necessary directories..."
mkdir -p build opt desktop-entries icons user-data/$(whoami)

# 📦 Install Electron and Electron-Builder
echo "📦 Installing Electron and Electron-Builder..."
npm install -g electron@${REQUIRED_ELECTRON_VERSION} electron-builder@${REQUIRED_ELECTRON_BUILDER_VERSION}

# 🚀 Build Applications
echo "🚀 Building applications..."
APP_SPELLCHECK_LANGS=$APP_SPELLCHECK_LANGS \
  APP_USERDATA=$APP_USERDATA \
  APP_LANG=$APP_LANG \
  REQUIRED_ELECTRON_VERSION=$REQUIRED_ELECTRON_VERSION \
  REQUIRED_NODE_MAJOR_VERSION=$REQUIRED_NODE_MAJOR_VERSION \
  python3 generate_apps.py

# 🖥️ Install Desktop Entries
echo "🖥️ Installing desktop entries..."
mkdir -p ~/.local/share/applications
cp desktop-entries/*.desktop ~/.local/share/applications/
update-desktop-database ~/.local/share/applications || true

# ✅ Done
echo "✅ Build and installation completed!"

#!/bin/bash

echo "============================================"
echo "  Python 3.10 Virtual Environment Installer"
echo "============================================"

# Detect package manager
detect_package_manager() {
    if command -v apt &> /dev/null; then
        echo "apt"
    elif command -v dnf &> /dev/null; then
        echo "dnf"
    elif command -v yum &> /dev/null; then
        echo "yum"
    elif command -v zypper &> /dev/null; then
        echo "zypper"
    elif command -v pacman &> /dev/null; then
        echo "pacman"
    else
        echo "unknown"
    fi
}

PKG_MANAGER=$(detect_package_manager)
echo "[INFO] Detected package manager: $PKG_MANAGER"

# Check if Python 3.10 is available
if ! command -v python3.10 &> /dev/null; then
    echo
    echo "[WARN] Python 3.10 is not installed. Attempting to install..."

    case "$PKG_MANAGER" in
        apt)
            sudo apt install -y python3.10 python3.10-venv python3.10-distutils
            ;;
        dnf)
            sudo dnf install -y python3.10 python3.10-venv
            ;;
        yum)
            sudo yum install -y python3.10 python3.10-venv
            ;;
        zypper)
            sudo zypper install -y python310 python310-venv
            ;;
        *)
            echo "[ERROR] Unsupported package manager. Please install Python 3.10 manually."
            exit 1
            ;;
    esac
fi

# Verify installation
if ! command -v python3.10 &> /dev/null; then
    echo "[ERROR] Python 3.10 could not be installed automatically."
    echo "Please install it manually and re-run this script."
    exit 1
fi

echo "[INFO] Python 3.10 found. Proceeding..."

# Create virtual environment
python3.10 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install rvc dependencies
echo "[INFO] Installing rvc dependencies..."
pip install rvc-python
pip install torch==2.1.1+cu118 torchaudio==2.1.1+cu118 --index-url https://download.pytorch.org/whl/cu118

# Upgrade pip, wheel, setuptools
echo "[INFO] Upgrading pip, wheel, setuptools..."
pip install --upgrade pip wheel setuptools

# Install other dependencies
echo "[INFO] Installing other dependencies..."
pip install openai pillow mss imagehash librosa sounddevice

echo
echo "============================================"
echo "  Environment setup complete!"
echo "  To activate later: source venv/bin/activate"
echo "============================================"

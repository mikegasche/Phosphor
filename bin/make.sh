#!/bin/bash
# ------------------------------------------------------------------------------
# make.sh - Build Phosphor.app (macOS Intel/ARM64) using PyInstaller + pyenc
# ------------------------------------------------------------------------------
set -e

# --- 0. Detect architecture (Intel or Apple Silicon) ---
ARCH=$(uname -m)
echo "==> Detected architecture: $ARCH"

# --- 1. Set project root to parent directory of this script ---
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"
echo "==> Project root: $PROJECT_ROOT"

# --- 2. Select exact Python version depending on architecture ---
if [ "$ARCH" = "arm64" ]; then
    # ARM / Apple Silicon → latest Python 3.11.x available via pyenv
    PYTHON_VERSION="$(pyenv install -l | grep -E '^\s*3\.11\.' | tail -1 | tr -d ' ')"
    echo "==> macOS ARM detected → using Python $PYTHON_VERSION (3.11.x)"
else
    # Intel → fixed Python 3.11.x
    PYTHON_VERSION="3.11.14"
    echo "==> Intel mac detected → using Python $PYTHON_VERSION"
fi

# --- 3. Set pyenv local version ---
pyenv local "$PYTHON_VERSION"

# Add pyenv shims to PATH so python/pyinstaller can be found
export PATH="$HOME/.pyenv/shims:$PATH"

echo "==> Using Python $(python --version)"

# --- 4. Activate virtual environment ---
if [ ! -d "venv" ]; then
    echo "ERROR: virtual environment not found. Run ./setup.sh first."
    exit 1
fi
source venv/bin/activate

# --- 5. Set environment variables for macOS / libmpv ---
export LC_NUMERIC=C
export LANG=C
# Ensure imports from 'app/' work during build
export PYTHONPATH="$PROJECT_ROOT/app:$PYTHONPATH"

echo "==> Locale set: LC_NUMERIC=$LC_NUMERIC, LANG=$LANG"
echo "==> PYTHONPATH=$PYTHONPATH"

# --- 6. Remove old builds ---
rm -rf build dist Phosphor.spec

# --- 7. PyInstaller build ---
pyinstaller \
    --name "Phosphor" \
    --windowed \
    --icon "app/resources/app_icon.icns" \
    --add-data "app/resources:resources" \
    app/phosphor.py

echo "==> Build finished. Check dist/Phosphor.app"

#!/bin/bash
# ------------------------------------------------------------------------------
# setup.sh
# macOS (Intel/ARM64) - Python env, venv, PySide6 + Pillow + PyInstaller
# ------------------------------------------------------------------------------

set -e

# --- 0. Detect architecture ---
ARCH=$(uname -m)
echo "==> Detected architecture: $ARCH"

# --- 1. Determine project root (bin/ is parallel to app/) ---
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# --- 2. Ensure pyenv is installed ---
if ! command -v pyenv >/dev/null 2>&1; then
  echo "ERROR: pyenv not found. Install pyenv first."
  exit 1
fi

# --- 3. Clean up old ENV variables + patches ---
unset PYTHON_CONFIGURE_OPTS
unset CONFIGURE_OPTS
unset LDFLAGS
unset CPPFLAGS
unset PKG_CONFIG_PATH
rm -rf ~/.pyenv/patches 2>/dev/null || true

# --- 4. Python version (3.11.x recommended for Intel & ARM) ---
PYTHON_VERSION="3.11.14"
echo "==> Using Python $PYTHON_VERSION"
pyenv install -s "$PYTHON_VERSION"
pyenv local "$PYTHON_VERSION"

# Activate shims
export PATH="$HOME/.pyenv/shims:$PATH"

# --- 5. Remove old venv ---
echo "==> Removing old venv..."
rm -rf venv

# --- 6. Create new venv ---
echo "==> Creating new venv..."
python -m venv venv
source venv/bin/activate

# --- 7. Upgrade pip, setuptools, wheel ---
echo '==> Upgrading pip, setuptools, wheel...'
pip install --upgrade pip setuptools wheel

# --- 8. Install required packages ---
echo "==> Installing required packages..."
pip install PySide6 pyinstaller python-mpv

# --- 9. Check installed packages ---
echo "==> Installed packages:"
python -m pip show PySide6
python -m pip show pyinstaller
python -m pip show python-mpv

python --version

echo "==> Setup complete. You can now run ./bin/make.sh to build the app."

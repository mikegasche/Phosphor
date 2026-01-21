#!/bin/sh

# Change to project root (one level up from this script)
cd "$(dirname "$0")/.." || exit 1
export PROJECT_ROOT="$(pwd)"

# Set PYTHONPATH to include the 'app/' folder so imports work correctly
export PYTHONPATH="$PROJECT_ROOT/app:$PYTHONPATH"

# Activate virtual environment
source venv/bin/activate

# Force macOS locale for libmpv to ensure numeric parsing works correctly
export LC_NUMERIC=C
export LANG=C

# Debug output
echo "Locale: LC_NUMERIC=$LC_NUMERIC, LANG=$LANG"

# Run the main Phosphor Python script
python app/phosphor.py

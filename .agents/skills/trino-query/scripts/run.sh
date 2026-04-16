#!/usr/bin/env bash
# run.sh - Automated runner for Trino Query skill

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
# Root directory of the skill (one level up from scripts/)
SKILL_ROOT="$(dirname "$SCRIPT_DIR")"

# Path to the virtual environment
VENV_DIR="$SKILL_ROOT/venv"

# Check if the virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Initializing virtual environment and installing dependencies for trino-query skill..."
    python3 -m venv "$VENV_DIR"
    "$VENV_DIR/bin/pip" install -r "$SKILL_ROOT/requirements.txt" --quiet
    echo "Initialization complete."
fi

# Execute the Trino query script with the virtual environment's Python
"$VENV_DIR/bin/python" "$SCRIPT_DIR/trino_query.py" "$@"

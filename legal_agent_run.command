#!/bin/zsh

# Source shell profile to get node/npm in PATH (needed when launched from Finder)
if [ -f "$HOME/.zshrc" ]; then
    source "$HOME/.zshrc" 2>/dev/null
elif [ -f "$HOME/.bash_profile" ]; then
    source "$HOME/.bash_profile" 2>/dev/null
fi

# Ensure we are in the script's directory
cd "$(dirname "$0")" || exit 1

echo "Starting Legal Agent Orchestrator..."

if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Run the master orchestrator
python3 master_orchestrator.py

#!/bin/bash

# Ensure we are in the script's directory
cd "$(dirname "$0")"

echo "========================================"
echo "    Setting up Agent Environment..."
echo "========================================"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt --quiet

# Run the agent
echo "========================================"
echo "        Running Agent A..."
echo "========================================"
python3 agent_a_glass_ceiling_scout.py

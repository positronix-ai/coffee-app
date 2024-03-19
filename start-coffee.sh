#!/bin/bash

# Get the directory of the current script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to the script's directory
cd "$SCRIPT_DIR"

source ./set-environment.sh

# Name of the tmux session
session_name="coffee-demo"

echo "Starting tmux session '$session_name'"

# Check if the tmux session already exists
tmux has-session -t $session_name 2>/dev/null

# If the session doesn't exist, create it
if [ $? != 0 ]; then
  echo "Tmux session '$session_name' does not exist. Creating it."
  # Start a new tmux session in the background
  tmux new-session -d -s $session_name "poetry run python ./coffee_demo.py"

  echo "Tmux session '$session_name' created. Attaching to it."

  # Attach to the tmux session
  tmux attach -t $session_name
else
  echo "Tmux session '$session_name' already exists. Attaching to it."
  tmux attach -t $session_name
fi
#!/bin/bash

# Usage: ./llama.sh [config] [action]
# Example: ./llama.sh nvidia-rtx3060-qwen3-14b-q4 start

# Check if 0 or 2 arguments are passed
if [ "$#" -eq 0 ]; then
  echo "Valid configurations:"
  for file in $( dirname "${BASH_SOURCE[0]}" )/llama.cpp/*.yaml; do
    echo "$(basename "$file" .yaml)"
  done
  exit 0
elif [ "$#" -ne 2 ]; then
  echo "Usage: $0 <configuration_name> <action>"
  echo "Valid actions: start, stop, status, logs"
  exit 1
fi

CONFIG_NAME="$1"
ACTION="$2"


# Construct the path to the YAML file
YAML_PATH="$( dirname "${BASH_SOURCE[0]}" )/llama.cpp/"
YAML_FILE="${YAML_PATH}${CONFIG_NAME}.yaml"

# Check if the YAML file exists
if [ ! -f "$YAML_FILE" ]; then
  echo "Error: The file $YAML_FILE does not exist."
  exit 1
fi

# Execute based on the action
case "$ACTION" in
  start)
    echo "Starting configuration: $CONFIG_NAME"
    docker compose -f "$YAML_FILE" up -d
    ;;
  stop)
    echo "Stopping configuration: $CONFIG_NAME"
    docker compose -f "$YAML_FILE" down
    ;;
  status)
    echo "Status of configuration: $CONFIG_NAME"
    docker compose -f "$YAML_FILE" ps
    ;;
  logs)
    echo "Showing logs for configuration: $CONFIG_NAME"
    docker compose -f "$YAML_FILE" logs -f
    ;;
  *)
    echo "Unknown action: $ACTION. Use: start, stop, status, logs."
    exit 1
    ;;
esac

exit 0
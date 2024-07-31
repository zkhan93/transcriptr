#!/bin/bash

# Function to display help message
usage() {
  echo "Usage: $0 -d DIRECTORY -t DURATION"
  echo "  -d DIRECTORY   Directory to place the recorded files"
  echo "  -t DURATION    Duration of each segment in seconds"
  exit 1
}

# Parse command line arguments
while getopts ":d:t:" opt; do
  case $opt in
    d) DIRECTORY=$OPTARG ;;
    t) DURATION=$OPTARG ;;
    *) usage ;;
  esac
done

# Check if all required arguments are provided
if [ -z "$DIRECTORY" ] || [ -z "$DURATION" ]; then
  usage
fi

# Create directory if it doesn't exist
mkdir -p "$DIRECTORY"

# Logging start
echo "Starting audio recording..."
echo "Directory: $DIRECTORY"
echo "Segment Duration: $DURATION seconds"

# Loop to continuously record in specified segments
while true; do
  filename="$DIRECTORY/$(date +'%Y-%m-%d_%H-%M-%S').wav"
  echo "Recording to $filename"
  arecord -Dac108 -f S32_LE -r 16000 -c 4 -d "$DURATION" "$filename"
  if [ $? -ne 0 ]; then
    echo "Recording failed. Exiting."
    exit 1
  fi
done

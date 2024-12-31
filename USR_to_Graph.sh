#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <input_file> <sent_id>"
  exit 1
fi

INPUT_FILE="$1"
SENT_ID="$2"

# Check if the input file exists
if [ ! -f "$INPUT_FILE" ]; then
  echo "Error: File '$INPUT_FILE' not found!"
  exit 1
fi

# Run the Python script with the input file and sent_id
python3 USR_to_Graph.py "$INPUT_FILE" "$SENT_ID"

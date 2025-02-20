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

# Check if virtual environment exists; create and activate it if necessary
if [ ! -d "venv" ]; then
  echo "Virtual environment not found. Creating one..."
  python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate || source venv/Scripts/activate

# Install required dependencies
echo "Installing required dependencies..."
pip install --quiet graphviz

# Ensure the script is executable
if [ ! -x USR_to_Graph.py ]; then
  echo "Making the Python script executable..."
  chmod +x USR_to_Graph.py
fi

# Run the Python script with the input file and sent_id
echo "Running the Python script..."
python3 USR_to_Graph.py "$INPUT_FILE" "$SENT_ID"

# Deactivate the virtual environment
echo "Deactivating virtual environment..."
deactivate

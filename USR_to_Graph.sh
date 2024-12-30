
#!/bin/bash

# Check if at least one argument (input file) and at least one sentence_id are provided
if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <input_file> <sent_id_1> [<sent_id_2> ... <sent_id_N>]"
  exit 1
fi

INPUT_FILE="$1"
shift  # Remove the input file argument so that $@ contains all sentence_ids

# Check if the input file exists
if [ ! -f "$INPUT_FILE" ]; then
  echo "Error: File '$INPUT_FILE' not found!"
  exit 1
fi

# Loop through each sentence_id and filter the corresponding block from the input file
FILTERED_CONTENT=""
for SENT_ID in "$@"; do
  # Extract the block between <sent_id=SENT_ID> and </sent_id>
  BLOCK=$(awk -v SENT_ID="<sent_id=$SENT_ID>" '
    BEGIN { in_block = 0 }
    $0 == SENT_ID { in_block = 1 }
    in_block == 1 { print $0 }
    $0 == "</sent_id>" { in_block = 0 }
  ' "$INPUT_FILE")

  # If block is not empty, append it to FILTERED_CONTENT
  if [ -n "$BLOCK" ]; then
    FILTERED_CONTENT="$FILTERED_CONTENT$BLOCK\n"
  else
    echo "Warning: Sentence ID '$SENT_ID' not found in the input file."
  fi
done

# If there are no valid sentence blocks to process, exit
if [ -z "$FILTERED_CONTENT" ]; then
  echo "No valid sentences found to process!"
  exit 1
fi

# Save the filtered content to a temporary file
TEMP_FILE=$(mktemp)
echo -e "$FILTERED_CONTENT" > "$TEMP_FILE"

# Run the Python script with the filtered content (temporary file)
python3 USR_to_Graph.py "$TEMP_FILE"

# Clean up temporary file
rm "$TEMP_FILE"

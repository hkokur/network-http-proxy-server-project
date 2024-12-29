#!/bin/bash

# Define test parameters
URL="http://127.0.0.1:8080/19999"
DURATION="5s"
THREADS=(1 2 4 8 16 32)  # Number of threads to test
CONNECTIONS=($(seq 20 20 200))  # Number of connections to test

# Output log file
OUTPUT_FILE="../test_outputs/wrk_test_results.log"

# Create the log directory if it doesn't exist
mkdir -p "$(dirname "$OUTPUT_FILE")"

# Append headers only if the file does not exist or is empty
if [ ! -s $OUTPUT_FILE ]; then
  echo "Performance Test Results" >> $OUTPUT_FILE
  echo "=========================" >> $OUTPUT_FILE
fi

# Ensure wrk is installed
if ! command -v wrk &>/dev/null; then
  echo "wrk command not found. Please install wrk first."
  exit 1
fi

# Run the tests
for t in "${THREADS[@]}"; do
  for c in "${CONNECTIONS[@]}"; do
    echo "---------------------------------------" >> $OUTPUT_FILE
    echo "Testing with $t threads and $c connections..." >> $OUTPUT_FILE
    wrk -t$t -c$c -d$DURATION $URL >> $OUTPUT_FILE 2>&1
    echo "---------------------------------------" >> $OUTPUT_FILE
  done
done

echo "Tests completed. Results are stored in $OUTPUT_FILE." >> $OUTPUT_FILE
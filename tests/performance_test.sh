#!/bin/bash

# Define test parameters
URL="http://127.0.0.1:8080/19999"
DURATION="5s"
THREADS=(20)  # Number of threads to test
CONNECTIONS=($(seq 1000 100 10000))  # Number of connections to test

# Output log file
OUTPUT_FILE="wrk_test_results.log"
echo "Performance Test Results" > $OUTPUT_FILE
echo "=========================" >> $OUTPUT_FILE

# Ensure wrk is installed
if ! command -v wrk &>/dev/null; then
  echo "wrk command not found. Please install wrk first."
  exit 1
fi

# Run the tests
for t in "${THREADS[@]}"; do
  for c in "${CONNECTIONS[@]}"; do
    echo "---------------------------------------" | tee -a $OUTPUT_FILE
    echo "Testing with $t threads and $c connections..." | tee -a $OUTPUT_FILE
    wrk -t$t -c$c -d$DURATION $URL 2>&1 | tee -a $OUTPUT_FILE
    echo "---------------------------------------" | tee -a $OUTPUT_FILE
  done
done

echo "Tests completed. Results are stored in $OUTPUT_FILE."
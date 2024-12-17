#!/bin/bash

# Define server URL and port
SERVER="http://127.0.0.1:8081"
LOG_FILE="test_server.log"

# Initialize log file
echo "Starting test suite at $(date)" > "$LOG_FILE"

# Helper function to log test results
test_case() {
  echo -e "\nRunning Test: $1" >> "$LOG_FILE"
  echo "Command: $2" >> "$LOG_FILE"
  echo "[DEBUG] Executing command: $2" >> "$LOG_FILE"
  eval "$2" >> "$LOG_FILE" 2>&1
  local status=$?
  echo "[DEBUG] Command finished with status: $status" >> "$LOG_FILE"
  if [[ $2 == *">"* ]]; then
    output_file=$(echo "$2" | awk -F'>' '{print $2}' | xargs)
    if [ -f "$output_file" ]; then
      size=$(wc -c < "$output_file")
      echo "[DEBUG] Output file '$output_file' size: $size bytes" >> "$LOG_FILE"
    else
      echo "[ERROR] Output file '$output_file' was not created." >> "$LOG_FILE"
    fi
  fi
  echo "-----------------------------------------" >> "$LOG_FILE"
}

# Section: Valid Requests
echo "[INFO] Starting valid request tests..." >> "$LOG_FILE"
test_case "Valid size request (100 bytes)" "curl -v \"$SERVER/100\" > valid_100.html"
test_case "Valid size request (20000 bytes)" "curl -v \"$SERVER/20000\" > valid_20000.html"
echo "[INFO] Finished valid request tests." >> "$LOG_FILE"

# Section: Invalid URI Requests
echo "[INFO] Starting invalid URI tests..." >> "$LOG_FILE"
test_case "Size below 100" "curl -v \"$SERVER/99\""
test_case "Size above 20000" "curl -v \"$SERVER/20001\""
test_case "Non-integer size" "curl -v \"$SERVER/abc\""
test_case "Missing size" "curl -v \"$SERVER/\""
echo "[INFO] Finished invalid URI tests." >> "$LOG_FILE"

# Section: Invalid HTTP Methods
echo "[INFO] Starting invalid HTTP method tests..." >> "$LOG_FILE"
test_case "POST method with valid URI" "curl -v -X POST \"$SERVER/500\""
echo "[INFO] Finished invalid HTTP method tests." >> "$LOG_FILE"

# Section: Concurrency Testing
echo "\n[INFO] Running concurrency tests..." >> "$LOG_FILE"
for i in {1..5}; do
  echo "[DEBUG] Sending concurrent request batch $i..." >> "$LOG_FILE"
  curl -s "$SERVER/1000" >> "concurrent_1000_batch_$i.html" 2>&1 &
  curl -s "$SERVER/200" >> "concurrent_200_batch_$i.html" 2>&1 &
  curl -s "$SERVER/300" >> "concurrent_300_batch_$i.html" 2>&1 &
done
wait
for i in {1..5}; do
  for size in 1000 200 300; do
    file="concurrent_${size}_batch_${i}.html"
    if [ -f "$file" ]; then
      size=$(wc -c < "$file")
      echo "[DEBUG] Concurrent batch output file '$file' size: $size bytes" >> "$LOG_FILE"
    else
      echo "[ERROR] Concurrent batch output file '$file' was not created." >> "$LOG_FILE"
    fi
  done
done
echo "[INFO] Concurrency tests complete." >> "$LOG_FILE"

# Section: Large Payloads
echo "[INFO] Starting large payload tests..." >> "$LOG_FILE"
test_case "Large valid request (20000 bytes)" "curl -v \"$SERVER/20000\" > large_output.html"
echo "[INFO] Finished large payload tests." >> "$LOG_FILE"

# Summary
echo "\n[INFO] All tests completed at $(date). Check $LOG_FILE for details." >> "$LOG_FILE"

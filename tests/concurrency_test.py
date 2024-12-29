#!/usr/bin/env python3

import requests
import concurrent.futures
import argparse
import logging
import time
from datetime import datetime

# Configure logging to write only to a file
logging.basicConfig(
    filename='../test_outputs/concurrency_test.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Default server configuration
DEFAULT_HOST = "http://127.0.0.1"
DEFAULT_PORT = 8080

# Define test parameters
VALID_SIZES = [100, 500, 1000, 5000, 10000, 20000]
HTTP_METHOD = 'GET'
CONCURRENT_REQUESTS = 100  # Total number of concurrent requests

def send_request(method, url, size=None):
    """
    Send an HTTP request to the server.

    :param method: HTTP method (GET)
    :param url: URL to send the request to
    :param size: Size parameter for the request
    :return: Tuple indicating success status and response or error message
    """
    try:
        if method == 'GET':
            target_url = f"{url}/{size}" if size is not None else url
            response = requests.get(target_url, timeout=5)
        else:
            logging.error(f"Unsupported HTTP method: {method}")
            return False, f"Unsupported HTTP method: {method}"

        return True, response
    except requests.exceptions.RequestException as e:
        logging.error(f"Request exception: {e}")
        return False, str(e)

def perform_concurrent_tests(url, num_requests):
    """
    Perform concurrent HTTP GET requests to the server with valid sizes.

    :param url: Server URL
    :param num_requests: Number of concurrent requests to send
    """
    logging.info("Starting concurrency tests with only valid GET requests")

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = []
        for i in range(num_requests):
            # Cycle through VALID_SIZES to distribute load
            size = VALID_SIZES[i % len(VALID_SIZES)]
            method = HTTP_METHOD

            futures.append(executor.submit(send_request, method, url, size))

        for future in concurrent.futures.as_completed(futures):
            success, result = future.result()
            if success:
                response = result
                if response.status_code == 200:
                    content_length = len(response.content)
                    logging.info(f"Success: {response.url} - {content_length} bytes received")
                else:
                    logging.warning(f"Failed: {response.url} - Status Code: {response.status_code}")
            else:
                logging.error(f"Error: {result}")

    logging.info("Concurrency tests with valid GET requests completed")

def main():
    parser = argparse.ArgumentParser(description="Concurrency Test for HTTP Server (GET Requests Only)")
    parser.add_argument("--host", type=str, default=DEFAULT_HOST, help="Server host (e.g., http://127.0.0.1)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Server port (e.g., 8080)")
    parser.add_argument("--concurrent", type=int, default=CONCURRENT_REQUESTS, help="Number of concurrent requests")
    args = parser.parse_args()

    server_url = f"{args.host}:{args.port}"
    logging.info(f"Starting tests against server at {server_url}")

    start_time = time.time()

    perform_concurrent_tests(server_url, args.concurrent)

    end_time = time.time()
    duration = end_time - start_time
    logging.info(f"All tests completed in {duration:.2f} seconds")

    # Summary
    print(f"Concurrency tests completed. Check 'concurrency_test.log' for details.")

if __name__ == "__main__":
    main()
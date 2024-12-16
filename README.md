```markdown
# Custom HTTP Server

A lightweight, multithreaded HTTP server with dynamic HTML generation, request validation, and a comprehensive test suite to ensure reliable functionality.

## Features

- **Dynamic HTML Page Generation**: Produces HTML pages of sizes ranging from 100 to 20,000 bytes based on the URI.
- **Supported HTTP Methods**: Handles `GET` requests exclusively.
- **Multithreading**: Manages concurrent client connections efficiently.
- **Request Validation**: Ensures requests have valid sizes and adhere to expected structures.

## Requirements

- **Python 3.x**
- **curl**: For sending HTTP requests and testing.
- **Bash shell**: For running the provided test suite.

## Usage

### Starting the Server

To run the server, execute the following command:

```bash
python server.py <port>
```

### Sending Requests

You can interact with the server using a browser or tools like `curl`:

```bash
curl http://127.0.0.1:<port>/<size>
```

- Replace `<port>` with the server's port.
- Replace `<size>` with the desired HTML size (must be between 100 and 20,000 bytes).

### Testing the Server

The project includes a test suite (`test.sh`) for comprehensive server testing under various scenarios.

#### Running Tests

Execute the test script as follows:

```bash
./test.sh
```

### Test Suite Details

The `test.sh` script covers:

1. **Valid Requests**:
   - Tests with sizes within the valid range (`/100` to `/20000`).
   - Validates that generated HTML matches the requested size.

2. **Invalid URI Requests**:
   - Tests with:
     - Out-of-range sizes (e.g., `/99`, `/20001`).
     - Non-integer sizes (e.g., `/abc`).
     - Missing size (e.g., `/`).
   - Confirms the server responds with `400 Bad Request`.

3. **Unsupported HTTP Methods**:
   - Sends `POST` requests and ensures the response is `510 Not Implemented`.

4. **Concurrency**:
   - Simulates multiple simultaneous requests to verify the server’s multithreading capabilities.

5. **Large Payload Handling**:
   - Validates server behavior for the maximum size (`/20000`).

#### Test Logs

- **Location**: `test_server.log`
- Includes detailed results for all test cases:
  - Executed commands.
  - Server responses.
  - Status of generated HTML files.

## Examples

### Valid Request
```http
GET /500 HTTP/1.1
```
**Response**: HTML content of 500 bytes.

### Invalid Request
```http
GET /99 HTTP/1.1
```
**Response**: `400 Bad Request: Size out of range`.

### Unsupported HTTP Method
```http
POST /500 HTTP/1.1
```
**Response**: `510 Not Implemented: Only GET method is supported`.

## Project Structure

- `server.py`: The core HTTP server implementation.
- `test/test.sh`: Test suite for automated server validation.
- `test/test_server.log`: Log file capturing the results of all tests.
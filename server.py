import socket, threading, argparse
import concurrent.futures  # Added import

# Check active IP addresses on your local machine by:
# MacOS/Linux: ifconfig
# Windows: ipconfig
HOST = "127.0.0.1"
PORT = 8080  # Default port number
BASE_SENTENCE = "Hello,World!"

parser = argparse.ArgumentParser()
parser.add_argument("port", type=int, help="Port number")
args = parser.parse_args()
PORT = args.port

# Define a set of standard HTTP methods
STANDARD_HTTP_METHODS = {
    "GET",
    "HEAD",
    "POST",
    "PUT",
    "DELETE",
    "CONNECT",
    "OPTIONS",
    "TRACE",
    "PATCH"
}

def handle_client(client_socket, address):
    # Receive the request from the client
    try:
        request = client_socket.recv(1024).decode("utf-8")
        print(f"Received request from {address}: \n{request}")
        if not request:
            client_socket.close()
            return

        # Parse the request line (the first line of the request)
        request_line = request.splitlines()[0]
        is_valid, result = parse_and_validate_uri(request_line)

        # Handle the response based on validation
        if is_valid:
            # Generate the HTML page
            document_size = result
            html_content = generate_html_page(document_size)
            response = (
                f"HTTP/1.1 200 OK\r\n"
                f"Content-Type: text/html\r\n"
                f"Content-Length: {document_size}\r\n"
                f"\r\n"
                f"{html_content}"
            )
        else:
            response = f"HTTP/1.1 {result}\r\n\r\n{result.split(':', 1)[1].strip()}"

        # Send the response
        print(f"Sending response to {address}: \n{response}")
        client_socket.sendall(response.encode("utf-8"))
    except Exception as e:
        print(f"Error handling client {address}: {e}")
    finally:
        client_socket.close()


def parse_and_validate_uri(request_line):
    try:
        # Get the URI
        parts = request_line.split()

        # Check if the URI format is valid
        if (
            len(parts) != 3
            or not parts[1].startswith("/")
            or not parts[1][1:].isdigit()
        ):
            return False, "400 Bad Request: Malformed or invalid URI"

        # Convert to int and control the size range
        document_size = int(parts[1][1:])
        if not (100 <= document_size <= 20000):
            return False, "400 Bad Request: Size out of range"

        # Check if the method is a standard HTTP method
        # curl -v -X FOO http://localhost:8080/500
        if parts[0] not in STANDARD_HTTP_METHODS:
            return False, "400 Bad Request: Invalid HTTP method"

        # check the GET method
        if parts[0] != "GET":
            return False, "501 Not Implemented: Only GET method is supported"

        # If valid, return the size
        return True, document_size

    except Exception as e:
        return False, f"400 Bad Request: {str(e)}"


def generate_html_page(document_size):
    head = f"<HEAD><TITLE>I am {document_size} bytes long</TITLE></HEAD>"
    body_start = "<BODY>"
    body_end = "</BODY>"

    # Calculate the remaining size needed for the body content
    fixed_size = (
        len("<HTML>") + len(head) + len(body_start) + len(body_end) + len("</HTML>")
    )
    remaining_size = document_size - fixed_size

    # Generate the body content
    body_content = BASE_SENTENCE * ((remaining_size // len(BASE_SENTENCE)))
    body_content += BASE_SENTENCE[: remaining_size % len(BASE_SENTENCE)]
    body = f"{body_start}{body_content}{body_end}"

    response_html = f"<HTML>{head}{body}</HTML>"
    # print(f"Generated HTML page of size {len(response_html)} bytes")
    return response_html


# Define the number of worker threads in the thread pool
MAX_WORKERS = 50  # You can adjust this number based on your needs

# Initialize the ThreadPoolExecutor
executor = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

print(f"Server listening on {HOST}:{PORT}")

try:
    while True:
        client_socket, client_address = server_socket.accept()
        # Submit the handle_client task to the thread pool
        executor.submit(handle_client, client_socket, client_address)
except KeyboardInterrupt:
    print("\nShutting down the server gracefully...")
finally:
    server_socket.close()
    executor.shutdown(wait=True)
    print("Server has been shut down.")
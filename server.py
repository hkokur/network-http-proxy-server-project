import socket, threading, argparse

# Check active IP addresses on your local machine by:
# MacOS/Linux: ifconfig
# Windows: ipconfig
HOST = "127.0.0.1"
PORT = 8080  # Default port number

parser = argparse.ArgumentParser()
parser.add_argument("port", type=int, help="Port number")
args = parser.parse_args()
PORT = args.port


def handle_client(client_socket, address):
    print(f"New connection from {address}")

    # Receive the request from the client
    try:
        request = client_socket.recv(1024).decode("utf-8")
        if not request:
            client_socket.close()
            return

        # Parse the request line (the first line of the request)
        request_line = request.splitlines()[0]
        is_valid, result = parse_and_validate_uri(request_line)

        # Handle the response based on validation
        if is_valid:
            response = f"HTTP/1.1 200 OK\r\n\r\nDocument size: {result} bytes"
        else:
            response = f"HTTP/1.1 {result}\r\n\r\n{result.split(':', 1)[1].strip()}"

        # Send the response
        client_socket.sendall(response.encode("utf-8"))
    except Exception as e:
        print(f"Error handling client {address}: {e}")
    finally:
        client_socket.close()


def parse_and_validate_uri(request_line):
    try:
        # Get the URI
        parts = request_line.split()
        print(parts)

        # Check if the URI format is valid
        if len(parts) < 2 or not parts[1].startswith("/") or not parts[1][1:].isdigit():
            return False, "400 Bad Request: Malformed or invalid URI"

        # Convert to int and control the size range
        document_size = int(parts[1][1:])
        if not (100 <= document_size <= 20000):
            return False, "400 Bad Request: Size out of range"

        # check the GET method
        if parts[0] != "GET":
            return False, "510 Not Implemented: Only GET method is supported"

        # If valid, return the size
        return True, document_size

    except Exception as e:
        return False, f"400 Bad Request: {str(e)}"


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

print(f"Server listening on {HOST}:{PORT}")

while True:
    client_socket, client_address = server_socket.accept()
    thread = threading.Thread(
        target=handle_client, args=(client_socket, client_address)
    )
    thread.start()

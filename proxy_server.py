import socket

# Check active IP addresses on your local machine by:
# MacOS/Linux: ifconfig
# Windows: ipconfig
HOST = "127.0.0.1"
PORT = 8888  # Default port number
WEB_SERVER_PORT = 8000


def proxy_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        try:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((HOST, PORT))
            print(f"Proxy server is running on {HOST}:{PORT}")

            server_socket.listen(10)  # Allows up to 10 connections

            while True:
                try:
                    client_socket, client_address = server_socket.accept()
                    print(f"Connection received from {client_address}")
                    handle_client(client_socket)
                except Exception as e:
                    print(f"Error during client handling: {e}")

        except KeyboardInterrupt:
            print("\nShutting down the proxy server.")
        except Exception as e:
            print(f"Error: {e}")


def handle_client(client_socket):
    try:
        # Receive the request from the client
        request = client_socket.recv(1024).decode("utf-8")
        if not request:
            client_socket.close()
            return

        # parse the request
        request_line = request.splitlines()[0]
        is_valid, document_size = parse_and_validate_uri(request_line)

        if is_valid:
            response = send_request_to_server(request)
        else:
            response = f"HTTP/1.1 {document_size}\r\n\r\n{document_size.split(':', 1)[1].strip()}"

        client_socket.sendall(response.encode("utf-8"))

    except KeyboardInterrupt:
        print("\nShutting down the proxy server.")
    except Exception as e:
        print(f"Error handling client: {e}")

    finally:
        client_socket.close()


def parse_and_validate_uri(request_line):
    try:
        method, relative_url, http_version = request_line.split()

        # Check if the URI format is valid
        if not relative_url.startswith("/") or not relative_url[1:].isdigit():
            return False, "400 Bad Request: Malformed or invalid URI"

        # Convert to int and control the size range
        document_size = int(relative_url[1:])
        if document_size >= 9999:
            return False, "414 Request-URI Too Long: file size is too large"

        # check the GET method
        if method != "GET":
            return False, "510 Not Implemented: Only GET method is supported"

        # If valid, return the size
        return True, document_size

    except Exception as e:
        return False, f"400 Bad Request: {str(e)}"


def send_request_to_server(request):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.connect(("127.0.0.1", WEB_SERVER_PORT))
            server_socket.sendall(request.encode("utf-8"))
            response = server_socket.recv(1024).decode("utf-8")
            print(f"Received response from the web server: \n{response}")
            return response
    except ConnectionRefusedError:
        return "HTTP/1.1 404 Not Found\r\n\r\nWeb server is not running"


proxy_server()

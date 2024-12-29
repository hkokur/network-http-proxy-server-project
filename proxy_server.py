import socket
import threading
import signal
import argparse
from urllib.parse import urlparse
from cache import Cache

# Check active IP addresses on your local machine by:
# MacOS/Linux: ifconfig
# Windows: ipconfig
HOST = "127.0.0.1"
PORT = 8888  # Default port number
WEB_SERVER_PORT = 8080
CACHE_DIR = "./proxy_cache"

signal.signal(signal.SIGTSTP, signal.SIG_IGN)


def proxy_server(cache_size):
    cache = Cache(CACHE_DIR, cache_size)  # Cache initialized for every instance
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
                    client_thread = threading.Thread(
                        target=handle_client, args=(client_socket, cache)
                    )
                    client_thread.start()
                except Exception as e:
                    print(f"Error during client handling: {e}")

        except KeyboardInterrupt:
            print("\nShutting down the proxy server.")
        except Exception as e:
            print(f"Error: {e}")


def handle_client(client_socket, cache):
    try:
        # Receive the request from the client
        request = client_socket.recv(1024).decode("utf-8")
        if not request:
            client_socket.close()
            return
        print(f"Received request: \n{request}")

        host_line = [
            line
            for line in request.splitlines()
            if line.startswith("Host:") or line.startswith("host:")
        ][0]

        if "127.0.0.1" in host_line or "localhost" in host_line:
            response = send_request_to_web_server(request, cache)
            print(f"Sending response to client: \n{response}\n\n")
            client_socket.sendall(response.encode("utf-8"))
        else:
            send_request_to_server(request, host_line, client_socket)

    except Exception as e:
        print(f"Error handling client: {e}")
        error_response = f"HTTP/1.1 500 Internal Server Error\r\n\r\n{str(e)}"
        client_socket.sendall(error_response.encode("utf-8"))
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


def send_request_to_web_server(request, cache):
    try:
        request_line = request.splitlines()[0]
        is_valid, response = parse_and_validate_uri(request_line)

        parsed_url = urlparse(request_line.split(" ")[1])
        web_server_host = parsed_url.hostname or "127.0.0.1"
        web_server_port = parsed_url.port or WEB_SERVER_PORT
        relative_path = parsed_url.path or "/"

        if not is_valid:
            cache.put(parsed_url.geturl(), response.encode("utf-8"))  # Cache the error response
            return f"HTTP/1.1 {response}\r\n\r\n{response.split(':', 1)[1].strip()}"

        # Conditional GET: Check if cached response exists and is unmodified
        if cache.exists(parsed_url.geturl()):
            cached_response = cache.get(parsed_url.geturl())  # Retrieve cached response
            cached_response_decoded = cached_response.decode("utf-8")
            if int(parsed_url.geturl().lstrip('/')) % 2 == 1:  # Determine if content is unmodified
                print("Conditional GET: Using cached response (unmodified).")
                return cached_response_decoded  # Serve cached response
            else:
                print("Conditional GET: Cached response invalidated (modified).")

        # Modify the request to use relative URI and correct Host header
        modified_request_lines = []
        for line in request.splitlines():
            if line.lower().startswith("host:"):
                modified_request_lines.append(
                    f"Host: {web_server_host}:{web_server_port}"
                )  # Update Host header
            elif line == request_line:
                modified_request_lines.append(
                    f"{request_line.split(' ')[0]} {relative_path} {request_line.split(' ')[2]}"
                )  # Use relative path in request line
            else:
                modified_request_lines.append(line)  # Keep other headers unchanged
        modified_request = "\r\n".join([modified_request_lines]) + "\r\n\r\n"

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.connect(("127.0.0.1", WEB_SERVER_PORT))
            server_socket.sendall(modified_request.encode("utf-8"))
            response = server_socket.recv(1024).decode("utf-8")

            cache.put(parsed_url.geturl(), response.encode("utf-8"))

            return response
    except Exception as e:
        return "HTTP/1.1 404 Not Found\r\n\r\nWeb server is not running"


def send_request_to_server(request, host_line, client_socket):
    # If HTTPS request get, then connect to the server
    # If HTTP request get, then send the request to directly the server
    host_name = host_line.split(":")[1].strip()
    request_line = request.splitlines()[0]

    if request_line.startswith("CONNECT"):  # HTTPS request
        port = int(host_line.split(":")[2].strip())
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.connect((host_name, port))
            client_socket.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")

            # Relay data between client and server
            client_socket.setblocking(False)
            server_socket.setblocking(False)

            while True:
                try:
                    data = client_socket.recv(4096)
                    if data:
                        server_socket.sendall(data)
                        print(
                            f"Sending request for {host_name} to server: \n{data}\n\n"
                        )
                except BlockingIOError:
                    pass

                try:
                    data = server_socket.recv(4096)
                    if data:
                        client_socket.sendall(data)
                        print(
                            f"Sending response for {host_name} to client: \n{data}\n\n"
                        )
                except BlockingIOError:
                    pass
    else:  # HTTP request
        # Extract the host and port from the request
        port = 80  # Default HTTP port
        request = request.replace("http://", "", 1).replace(host_name, "", 1)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.connect((host_name, port))
            server_socket.sendall(request.encode("utf-8"))
            while True:
                data = server_socket.recv(4096)
                if not data:
                    break
                client_socket.sendall(data)
                print(f"Sending response for {host_name} to client: \n{data}\n\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a simple HTTP proxy server.")
    parser.add_argument(
        "cache_size",
        type=int,
        help="Maximum number of entries in the cache (required)",
    )
    args = parser.parse_args()

    proxy_server(args.cache_size)

import socket

# Check active IP addresses on your local machine by:
# MacOS/Linux: ifconfig
# Windows: ipconfig
HOST = "127.0.0.1"
PORT = 8888  # Default port number

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
        
        except OSError as e:
            print(f"OS Error: {e}")
        except KeyboardInterrupt:
            print("\nShutting down the proxy server.")
        except Exception as e:
            print(f"Error: {e}")


def handle_client(client_socket):
    try:
        # Receive the request from the client
        request = client_socket.recv(4096).decode('utf-8')
        print(f"Request received:\n{request}")

        # Placeholder
        response = "HTTP/1.0 200 OK\r\nContent-Type: text/plain\r\n\r\nProxy server is working!"

        client_socket.sendall(response.encode('utf-8'))
    
    except Exception as e:
        print(f"Error handling client: {e}")
    
    finally:
        # Close the client connection
        client_socket.close()

proxy_server()
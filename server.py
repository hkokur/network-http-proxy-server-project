import socket, threading

# Check active ip addresses on your local machine by:
# MacOs/Linux: ifconfig
# Windows: ipconfig 
HOST = "127.0.0.1"
PORT = 8080

def handle_client(client_socket, address):
    print(f"New connection from {address}")
    client_socket.sendall(b"Welcome to the server!\n")
    client_socket.close()


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

print(f"Server listening on {HOST}:{PORT}")

while True:
    client_socket, client_address = server_socket.accept()
    thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    thread.start()
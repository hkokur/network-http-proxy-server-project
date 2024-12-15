from http.server import HTTPServer, BaseHTTPRequestHandler

# Check active ip addresses on your local machine by:
# MacOs/Linux: ifconfig
# Windows: ipconfig 
HOST = "127.0.0.1"
PORT = 8080

class HTTP(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Length", "0")
        self.end_headers()


server = HTTPServer((HOST, PORT), HTTP)
server.serve_forever()
server.server_close()
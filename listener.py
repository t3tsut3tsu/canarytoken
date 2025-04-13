from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        open_time = datetime.now()
        client_ip = self.client_address[0]
        self.send_response(200)
        self.send_header("Content-type", "image/png")
        self.end_headers()

class Listener:
    def __init__(self, listen_address, listen_port):
        self.listen_address = listen_address
        self.listen_port = listen_port

    def listener(self, server_class=HTTPServer, handler_class=Handler):
        server_address = (self.listen_address, self.listen_port)
        httpd = server_class(server_address, handler_class)
        print(f'Starting server on {self.listen_address}:{self.listen_port}')
        httpd.serve_forever()

if __name__ == "__main__":
    listener = Listener("127.0.0.1", 4444)
    listener.listener()

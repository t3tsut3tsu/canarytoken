from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer # ThreadingHTTPServer для разделения request по потокам
from datetime import datetime

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        #open_time = datetime.now()
        #client_ip = self.client_address[0]
        self.send_response(200)
        self.send_header("Content-type", "image/png")
        self.end_headers()

class Listener:
    def __init__(self, server, port):
        self.server = server
        self.port = port

    def listener(self, server_class=ThreadingHTTPServer, handler_class=Handler):
        server_address = (self.server, self.port)
        httpd = server_class(server_address, handler_class)
        print(f'Starting server on {self.server}:{self.port}')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer is shutting down (by ctrl+c)")
        finally:
            httpd.server_close()
            print("Servero finallio")

if __name__ == "__main__":
    listener = Listener("127.0.0.1", 4444)
    listener.listener()

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer # ThreadingHTTPServer для разделения request по потокам
from datetime import datetime


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        open_time = datetime.now()
        client_ip = self.client_address[0]
        self.send_response(200)
        self.send_header('Content-type', 'image/png')
        self.end_headers()

class Listener:
    def __init__(self, http_server, http_port):
        self.http_server = http_server
        self.http_port = http_port

    def listener(self, server_class=ThreadingHTTPServer, handler_class=Handler):
        server_address = (self.http_server, self.http_port)
        httpd = server_class(server_address, handler_class)
        print(f'Starting server on {self.http_server}:{self.http_port}')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('Servero finallio (by ctrl+c)')
        finally:
            httpd.server_close()

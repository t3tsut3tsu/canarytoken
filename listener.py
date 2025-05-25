from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer # ThreadingHTTPServer для разделения request по потокам
from datetime import datetime
from urllib.parse import urlparse, parse_qs

class Handler(BaseHTTPRequestHandler):
    def __init__(self, *args, db=None, **kwargs):
        self.db = db
        super().__init__(*args, **kwargs)

    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        open_time = datetime.now()
        ip_addr = self.client_address[0]

        self.send_response(200)
        self.send_header('Content-type', 'image/png')
        self.end_headers()

        if 'token' in query_params:
            token_value = query_params['token'][0]
            print(f'Token received: {token_value} from IP: {ip_addr} at {open_time}')
            try:
                self.db.db_insert_from_listener(token_value, ip_addr, open_time)
            except Exception as e:
                print(f'Error writing to database: {e}')
        else:
            print('It seems someone trying to trick us...')

class Listener:
    def __init__(self, http_server, http_port, db):
        self.http_server = http_server
        self.http_port = http_port
        self.db = db

    def listener(self):
        server_address = (self.http_server, self.http_port)

        def handler_factory(*args, **kwargs):
            return Handler(*args, db=self.db, **kwargs)

        httpd = ThreadingHTTPServer(server_address, handler_factory)

        print(f'Starting server on {self.http_server}:{self.http_port}')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('Servero finallio (by ctrl+c)')
        finally:
            httpd.server_close()

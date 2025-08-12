import logging
import logger

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer # ThreadingHTTPServer для разделения request по потокам
from datetime import datetime
from urllib.parse import urlparse, parse_qs


logger.logger()

class Handler(BaseHTTPRequestHandler):
    def __init__(self, *args, db=None, **kwargs):
        self.db = db
        super().__init__(*args, **kwargs)

    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        open_time = datetime.now()
        ip_addr = self.client_address[0]

        host = self.headers['Host']
        full_link = f'http://{host}{self.path}'

        self.send_response(200)

        if 'token' in query_params:
            token_value = query_params['token'][0]
            try:
                if self.db.db_is_token_exist(token_value):
                    print(f'Token was received: {token_value} from IP: {ip_addr} at {open_time}')
                    self.db.db_insert_good_listener(token_value, ip_addr, open_time)
                    logging.debug(f'{token_value} FROM {ip_addr}')
                else:
                    print('It seems someone\'s trying to trick us...')
                    print(f'Token was received: {token_value} from IP: {ip_addr} at {open_time}')
                    self.db.db_insert_unknown_listener(token_value, ip_addr, open_time, false_token=1)
                    logging.warning(f'{token_value} FROM {ip_addr}')
            except Exception as e:
                print(f'Error writing to database: {e}')
        else:
            print('It seems someone\'s trying to threat us!!!')
            print(f'Link was received: {full_link} from IP: {ip_addr} at {open_time}')
            try:
                self.db.db_insert_unknown_listener(full_link, ip_addr, open_time, false_token=0)
            except Exception as e:
                print(f'Error writing to database: {e}')

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

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('Servero finallio (by ctrl+c)')
        finally:
            httpd.server_close()

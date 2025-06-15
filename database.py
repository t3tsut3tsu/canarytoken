import sqlite3
import threading

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.lock = threading.Lock()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def db_creating(self):
        with self.lock:
            conn = self.get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS TOTAL (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT,
                    token VARCHAR(255),
                    sender VARCHAR(255),
                    recipient VARCHAR(255),
                    ip_addr VARCHAR(16),
                    get_time DATETIME,
                    open_time DATETIME
                )
                ''')
                conn.commit()

                cursor.execute('''
                CREATE TABLE IF NOT EXISTS GOOD (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT,
                    token VARCHAR(255),
                    sender VARCHAR(255),
                    recipient VARCHAR(255),
                    ip_addr VARCHAR(16),
                    get_time DATETIME,
                    open_time DATETIME,
                    open_num INT
                )
                ''')
                conn.commit()

                cursor.execute('''
                CREATE TABLE IF NOT EXISTS BAD (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT,
                    sender VARCHAR(255),
                    recipient VARCHAR(255)
                )
                ''')
                conn.commit()
            finally:
                conn.close()

    def db_insert(self, good_emails, bad_emails, sender, tokens, description):
        with self.lock:
            conn = self.get_connection()
            try:
                cursor = conn.cursor()
                for (email, token) in zip(good_emails, tokens):
                    cursor.execute(f'INSERT INTO TOTAL (token, recipient, sender, description) VALUES (?, ?, ?, ?)', (token, email, sender, description))
                    cursor.execute(f'INSERT INTO GOOD (token, recipient, sender, description) VALUES (?, ?, ?, ?)', (token, email, sender, description))
                for email in bad_emails:
                    cursor.execute(f'INSERT INTO BAD (recipient, sender, description) VALUES (?, ?, ?)', (email, sender, description))
                conn.commit()
            finally:
                conn.close()

    def db_insert_from_listener(self, token, ip_addr, open_time):
        with self.lock:
            conn = self.get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute('UPDATE TOTAL SET ip_addr = ?, open_time = ? WHERE token = ?', (ip_addr, open_time, token))
                cursor.execute('SELECT id, open_num FROM GOOD WHERE token = ?', (token,))
                row = cursor.fetchone()
                if row:
                    new_open_num = (row['open_num'] or 0) + 1
                    cursor.execute('UPDATE GOOD SET ip_addr = ?, open_time = ?, open_num = ? WHERE id = ?',(ip_addr, open_time, new_open_num, row['id']))
                else:
                    cursor.execute( 'INSERT INTO GOOD (token, ip_addr, open_time, open_num) VALUES (?, ?, ?, ?)',(token, ip_addr, open_time, 1))
                conn.commit()
            finally:
                conn.close()

    def db_insert_from_smtp(self, token, get_time):
        with self.lock:
            conn = self.get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute('UPDATE TOTAL SET get_time = ? WHERE token = ?',(get_time, token, ))
                cursor.execute('UPDATE GOOD SET get_time = ? WHERE token = ?',(get_time, token, ))
                conn.commit()
            finally:
                conn.close()

    def db_output(self, description):
        with self.lock:
            conn = self.get_connection()
            try:
                cursor = conn.cursor()
                if description:
                    placeholder = ', '.join(['?'] * len(description))
                    query = f'SELECT * FROM GOOD WHERE description IN ({placeholder})'
                    cursor.execute(query, description)
                else:
                    cursor.execute('SELECT * FROM GOOD')
                return cursor.fetchall()
            finally:
                conn.close()

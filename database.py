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

                cursor.execute('''
                CREATE TABLE IF NOT EXISTS UNKNOWN (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip_addr VARCHAR(16),
                    link VARCHAR(255),
                    open_time DATETIME,
                    false_token BOOLEAN DEFAULT 0
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
                    cursor.execute(f'INSERT INTO TOTAL (token, recipient, sender, description) VALUES (?, ?, ?, ?)', (token, email, sender, description)) # 1 в функцию
                    cursor.execute(f'INSERT INTO GOOD (token, recipient, sender, description) VALUES (?, ?, ?, ?)', (token, email, sender, description)) # 1 в функцию
                for email in bad_emails:
                    cursor.execute(f'INSERT INTO BAD (recipient, sender, description) VALUES (?, ?, ?)', (email, sender, description))
                conn.commit()
            finally:
                conn.close()

    def db_insert_good_listener(self, token, ip_addr, open_time):
        with self.lock:
            conn = self.get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute('UPDATE TOTAL SET ip_addr = ?, open_time = ? WHERE token = ?', (ip_addr, open_time, token)) # 2 в функцию
                cursor.execute('SELECT id, open_num FROM GOOD WHERE token = ?', (token,))
                row = cursor.fetchone()
                if row:
                    new_open_num = (row['open_num'] or 0) + 1
                    cursor.execute('UPDATE GOOD SET ip_addr = ?, open_time = ?, open_num = ? WHERE id = ?',(ip_addr, open_time, new_open_num, row['id'])) # 2 в функцию
                else:
                    cursor.execute( 'INSERT INTO GOOD (token, ip_addr, open_time, open_num) VALUES (?, ?, ?, ?)',(token, ip_addr, open_time, 1))
                conn.commit()
            finally:
                conn.close()

    def db_insert_unknown_listener(self, link, ip_addr, open_time, false_token):
        with self.lock:
            conn = self.get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(f'INSERT INTO UNKNOWN (ip_addr, link, open_time, false_token) VALUES (?, ?, ?, ?)',(ip_addr, link, open_time, false_token))
                conn.commit()
            finally:
                conn.close()

    def db_insert_from_smtp(self, token, get_time):
        with self.lock:
            conn = self.get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute('UPDATE TOTAL SET get_time = ? WHERE token = ?',(get_time, token, )) # 3 в функцию
                cursor.execute('UPDATE GOOD SET get_time = ? WHERE token = ?',(get_time, token, )) # 3 в функцию
                conn.commit()
            finally:
                conn.close()

    def db_is_token_exist(self, token):
        with self.lock:
            conn = self.get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM GOOD WHERE token = ?', (token,))
                count = cursor.fetchone()[0]
                return count > 0
            finally:
                conn.close()

    def db_sum_of_tricks(self, description):
        with self.lock:
            conn = self.get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute('SELECT SUM(open_num) FROM GOOD WHERE description = ?', (description, ))
                result = cursor.fetchone()
                count = result[0] if result else 0
                return count
            finally:
                conn.close()

    def db_output_good(self, description):
        with self.lock:
            conn = self.get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM GOOD WHERE description = ?', (description, ))
                return cursor.fetchall()
            finally:
                conn.close()

    def db_output_bad(self, description):
        with self.lock:
            conn = self.get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM BAD WHERE description = ?', (description, ))
                return cursor.fetchall()
            finally:
                conn.close()

    def db_output_unknown(self): # время?
        with self.lock:
            conn = self.get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM UNKNOWN')
                return cursor.fetchall()
            finally:
                conn.close()

    def db_sum_of_mails(self, description, good_emails, bad_emails): # ???
        with self.lock:
            conn = self.get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute('SELECT SUM(recipient) FROM GOOD WHERE description = ?', (good_emails, description))
                cursor.execute('SELECT SUM(recipient) FROM BAD WHERE description = ?', (bad_emails, description))
                return cursor.fetchall()
            finally:
                conn.close()
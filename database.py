import shutil
import os
import sqlite3
import threading

from datetime import datetime


class Database:
    def __init__(self, db_path, db_merged_path, db_backups):
        self.db_path = db_path
        self.db_merged_path = db_merged_path
        self.db_backups = db_backups
        self.lock = threading.Lock()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def creator_main_structure(cursor, conn): # создание правильной структуры БД
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS TOTAL (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT,
            token VARCHAR(255),
            sender VARCHAR(255),
            recipient VARCHAR(255),
            ip_addr VARCHAR(16),
            get_time DATETIME,
            open_time DATETIME,
            file_format VARCHAR(8)
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
            all_ips TEXT,
            get_time DATETIME,
            open_time DATETIME,
            open_num INT,
            user_agent TEXT,
            referer TEXT,
            file_format VARCHAR(8)
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
            user_agent TEXT,
            referer TEXT,
            false_token BOOLEAN DEFAULT 0
        )
        ''')
        conn.commit()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS STATIC (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_addr VARCHAR(16),
            open_time DATETIME,
            open_num INT,
            user_agent TEXT,
            referer TEXT,
            file_format VARCHAR(8)
        )
        ''')
        conn.commit()

    @staticmethod
    def selecting_token(cursor, receiver):
        cursor.execute('SELECT DISTINCT token FROM GOOD WHERE recipient = ? AND get_time IS NULL', (receiver,))

    @staticmethod
    def inserting(cursor, table, token, email, sender, description, file_format):
        cursor.execute(f'INSERT INTO {table} (token, recipient, sender, description, file_format) VALUES (?, ?, ?, ?, ?)', (token, email, sender, description, file_format))

    #@staticmethod
    #def updating(cursor, table, ip_addr, open_time, token):
    #    cursor.execute(f'UPDATE {table} SET ip_addr = ?, open_time = ? WHERE token = ?', (ip_addr, open_time, token))

    def db_creating(self):
        with self.lock:
            conn = self.get_connection()
            try:
                cursor = conn.cursor()
                self.creator_main_structure(cursor, conn)
            finally:
                conn.close()

    def merging(self):
        with self.lock:
            if not os.path.exists(self.db_backups):
                os.makedirs(self.db_backups)
                print(f'Dir for backups: {self.db_backups}')

            filename_db1 = os.path.basename(self.db_path)
            only_name_db1, ext = os.path.splitext(filename_db1)

            filename_db2 = os.path.basename(self.db_merged_path)
            only_name_db2, _ = os.path.splitext(filename_db2)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f'{only_name_db1}-backup-{timestamp}{ext}'
            backup_path = os.path.join(self.db_backups, backup_filename)

            if os.path.exists(self.db_path):
                shutil.copy2(self.db_path, backup_path)
                print(f'Backup is saved to: {backup_path}')
            else:
                print(f'Main database is not found at: {self.db_path}')
                return

            conn = self.get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(f'ATTACH DATABASE "{self.db_merged_path}" AS db2')

                cursor.execute('SELECT MAX(id) FROM TOTAL')
                max_total_id = cursor.fetchone()[0] or 0
                cursor.execute(f'INSERT INTO TOTAL (id, description, token, sender, recipient, ip_addr, get_time, open_time) SELECT id + {max_total_id}, description, token, sender, recipient, ip_addr, get_time, open_time FROM db2.TOTAL')

                cursor.execute('SELECT MAX(id) FROM GOOD')
                max_good_id = cursor.fetchone()[0] or 0
                cursor.execute(f'INSERT INTO GOOD (id, description, token, sender, recipient, ip_addr, get_time, open_time, open_num) SELECT id + {max_good_id}, description, token, sender, recipient, ip_addr, get_time, open_time, open_num FROM db2.GOOD')

                cursor.execute('SELECT MAX(id) FROM BAD')
                max_bad_id = cursor.fetchone()[0] or 0
                cursor.execute(f'INSERT INTO BAD (id, description, sender, recipient) SELECT id + {max_bad_id}, description, sender, recipient FROM db2.BAD')

                cursor.execute('SELECT MAX(id) FROM UNKNOWN')
                max_unknown_id = cursor.fetchone()[0] or 0
                cursor.execute(f'INSERT INTO UNKNOWN (id, ip_addr, link, open_time, false_token) SELECT id + {max_unknown_id}, ip_addr, link, open_time, false_token FROM db2.UNKNOWN')

                conn.commit()

            except Exception as e:
                print(f'Merge error: {e}')
                conn.rollback()
            finally:
                conn.close()

                merged_db_path = os.path.join(os.path.dirname(self.db_path), f'merged-{only_name_db1}-{only_name_db2}{ext}')
                os.rename(self.db_path, merged_db_path)
                print(f'Database renamed to: {merged_db_path}')

    def db_insert(self, good_emails, bad_emails, sender, tokens, description, file_format):
        with self.lock:
            conn = self.get_connection()
            try:
                cursor = conn.cursor()
                for (email, token) in zip(good_emails, tokens):
                    self.inserting(cursor, 'TOTAL', token, email, sender, description, file_format)
                    self.inserting(cursor, 'GOOD', token, email, sender, description, file_format)
                for email in bad_emails:
                    cursor.execute(f'INSERT INTO BAD (recipient, sender, description) VALUES (?, ?, ?)', (email, sender, description))
                conn.commit()
            finally:
                conn.close()

    def db_insert_good_listener(self, token, ip_addr, open_time, user_agent, referer):
        with self.lock:
            conn = self.get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute('UPDATE TOTAL SET ip_addr = ?, open_time = ? WHERE token = ?', (ip_addr, open_time, token)) # 2 в функцию
                cursor.execute('SELECT id, open_num FROM GOOD WHERE token = ?', (token,))
                row = cursor.fetchone()
                if row:
                    new_open_num = (row['open_num'] or 0) + 1
                    cursor.execute('UPDATE GOOD SET ip_addr = ?, open_time = ?, open_num = ?, user_agent = ?, referer = ? WHERE id = ?',(ip_addr, open_time, new_open_num, user_agent, referer, row['id'])) # 2 в функцию
                else:
                    cursor.execute( 'INSERT INTO GOOD (token, ip_addr, open_time, open_num, user_agent, referer) VALUES (?, ?, ?, ?, ?, ?)',(token, ip_addr, open_time, 1, user_agent, referer))
                conn.commit()
            finally:
                conn.close()

    def db_insert_unknown_listener(self, link, ip_addr, open_time, false_token, user_agent, referer):
        with self.lock:
            conn = self.get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(f'INSERT INTO UNKNOWN (ip_addr, link, open_time, false_token, user_agent, referer) VALUES (?, ?, ?, ?, ?, ?)',(ip_addr, link, open_time, false_token, user_agent, referer))
                conn.commit()
            finally:
                conn.close()

    def db_insert_static_listener(self, ip_addr, file_format, open_time, user_agent, referer):
        with self.lock:
            conn = self.get_connection()
            try:
                cursor = conn.cursor()

                cursor.execute('SELECT id, open_num FROM STATIC WHERE ip_addr = ? AND file_format = ?',
                               (ip_addr, file_format))
                row = cursor.fetchone()

                if row:
                    new_open_num = (row['open_num'] or 0) + 1
                    cursor.execute('UPDATE STATIC SET open_time = ?, open_num = ?, user_agent = ?, referer = ? WHERE id = ?',(open_time, new_open_num, user_agent, referer, row['id']))
                else:
                    cursor.execute('INSERT INTO STATIC (ip_addr, file_format, open_time, open_num, user_agent, referer) VALUES (?, ?, ?, ?, ?, ?)',(ip_addr, file_format, open_time, 1, user_agent, referer))
                conn.commit()

            except Exception as e:
                print(f"Error in db_insert_static_listener: {e}")
                if conn:
                    conn.rollback()
                raise

            finally:
                if conn:
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

    def doubled_description(self, description):
        with self.lock:
            conn = self.get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute('SELECT get_time FROM TOTAL WHERE description = ? LIMIT 1', (description, ))
                return cursor.fetchall()
            finally:
                conn.close()
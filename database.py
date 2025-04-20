import sqlite3

class Database:
    def __init__(self, db_path):
        self.db_path = db_path

        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()

    def db_creating(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS TOTAL (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token VARCHAR(255),
                description TEXT NOT NULL,
                ip_addr VARCHAR(16)
            )
        ''')
        self.connection.commit()

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS GOOD (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token VARCHAR(255),
                description TEXT NOT NULL,
                email_from VARCHAR(255),
                email_send VARCHAR(255),
                ip_addr VARCHAR(16),
                get_time DATETIME,
                open_time DATETIME,
                open_num INT
            )
        ''')
        self.connection.commit()

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS BAD (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token VARCHAR(255),
                description TEXT NOT NULL,
                email_send VARCHAR(255),
                ip_addr VARCHAR(16)
            )
        ''')
        self.connection.commit()

    def db_insert(self, emails, description):
        for email in emails:
            self.cursor.execute(f'INSERT INTO TOTAL (description) VALUES (?)', (description,))
            self.cursor.execute(f'INSERT INTO GOOD (email_send, description) VALUES (?, ?)', (email, description))
            self.cursor.execute(f'INSERT INTO BAD (email_send, description) VALUES (?, ?)', (email, description))
        self.connection.commit()

    def db_output(self):
        self.cursor.execute(f'SELECT * FROM TOTAL')
        targets = self.cursor.fetchall()
        for target in targets:
            print(target)

    def db_closing(self):
        self.connection.close()

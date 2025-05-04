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
                description TEXT NOT NULL,
                token VARCHAR(255),
                sender VARCHAR(255),
                recipient VARCHAR(255),
                ip_addr VARCHAR(16),
                get_time DATETIME,
                open_time DATETIME
            )
        ''')
        self.connection.commit()

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS GOOD (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                token VARCHAR(255),
                sender VARCHAR(255),
                recipient VARCHAR(255),
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
                description TEXT NOT NULL,
                sender VARCHAR(255),
                recipient VARCHAR(255)
            )
        ''')
        self.connection.commit()

    def db_insert(self, good_emails, bad_emails, sender, tokens, description):
        for (email, token) in zip(good_emails, tokens):
            self.cursor.execute(f'INSERT INTO TOTAL (token, recipient, sender, description) VALUES (?, ?, ?, ?)', (token, email, sender, description))
            self.cursor.execute(f'INSERT INTO GOOD (token, recipient, sender, description) VALUES (?, ?, ?, ?)', (token, email, sender, description))
        for email in bad_emails:
            self.cursor.execute(f'INSERT INTO BAD (recipient, sender, description) VALUES (?, ?, ?)', (email, sender, description))
        self.connection.commit()

    def db_output(self):
        self.cursor.execute(f'SELECT * FROM TOTAL')
        targets = self.cursor.fetchall()
        for target in targets:
            print(target)

    def db_closing(self):
        self.connection.close()

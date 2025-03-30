import sqlite3

class Database:
    def __init__(self, db_name, table_name):
        self.db_name = db_name
        self.table_name = table_name

        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()

    def db_creating(self):
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uid INTEGER,
                description TEXT NOT NULL,
                email_send VARCHAR(255),
                email_err VARCHAR(255),
                open_tracker BOOLEAN,
                get_time DATETIME,
                open_time DATETIME
            )
        ''')
        self.connection.commit()

    def db_insert(self, emails, description):
        for email in emails:
            self.cursor.execute(f'INSERT INTO {self.table_name} (email_send, description) VALUES (?, ?)', (email, description))
        self.connection.commit()

    def db_output(self):
        self.cursor.execute(f'SELECT * FROM {self.table_name}')
        targets = self.cursor.fetchall()
        for target in targets:
            print(target)

    def db_closing(self):
        self.connection.close()
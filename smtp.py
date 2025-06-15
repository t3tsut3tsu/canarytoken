import smtplib

from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from concurrent.futures import ThreadPoolExecutor, as_completed
from email import encoders
from tqdm import tqdm


class SmtpUnite: # чтобы сформировать письмо
    def __init__(self, smtp_server, smtp_port, smtp_subject, smtp_from_addr, smtp_body, valid_mails, template, name, db, max_threads = 15):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_subject = smtp_subject
        self.smtp_from_addr = smtp_from_addr
        self.smtp_body = smtp_body
        self.valid_mails = valid_mails
        self.template = template
        self.name = name
        self.db = db
        self.max_threads = max_threads

    def file_adding(self, msg, template): # метод формирует вложение в письмо
        part = MIMEBase('application', "octet-stream")
        template.seek(0)
        part.set_payload(template.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{self.name}"')
        msg.attach(part)

    def letter_forming(self, receiver, template): # формирование тела письма + добавление вложений
        msg = MIMEMultipart()
        msg['From'] = self.smtp_from_addr
        msg['To'] = receiver
        msg['Subject'] = self.smtp_subject
        msg.attach(MIMEText(self.smtp_body, 'plain'))
        self.file_adding(msg, template) # добавление вложения
        return msg

    def send_preparing(self, receiver, template):# создание smtp подключения
        msg = self.letter_forming(receiver, template)
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as smtp_obj:
            smtp_obj.sendmail(self.smtp_from_addr, receiver, msg.as_string())

        if self.db is not None:
            get_time = datetime.now()
            token = self.token_by_receiver(receiver)
            self.db.db_insert_from_smtp(token, get_time)

        return receiver, True

    @staticmethod
    def chunks(mails, thread_num):
        chunks = []
        for i in range(0, len(mails), thread_num):
            chunks.append(mails[i: i + thread_num])
        return chunks

    def token_by_receiver(self, receiver):
        cursor = self.db.get_connection().cursor()
        cursor.execute('SELECT DISTINCT token FROM GOOD WHERE recipient = ? AND get_time IS NULL', (receiver,))
        row = cursor.fetchone()
        return row['token'] if row else None

    def sending(self):
        mails_chunks = self.chunks(self.valid_mails, max(len(self.valid_mails) // self.max_threads, 1)) # если список меньше числа потоков

        total_emails = len(self.valid_mails)
        with tqdm(total=total_emails) as pbar:
            with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
                futures = []
                for chunk in mails_chunks:
                    for i, receiver in enumerate(chunk):
                        index = self.valid_mails.index(receiver)
                        template = self.template[index]
                        futures.append(executor.submit(self.send_preparing, receiver, template))

                for future in as_completed(futures):
                    try:
                        future.result()
                        pbar.update(1)
                    except Exception as e:
                        print(f'Error: {e}')

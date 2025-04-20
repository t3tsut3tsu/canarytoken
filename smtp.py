import os
import smtplib

#from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from concurrent.futures import ThreadPoolExecutor
from email import encoders

class SmtpUnite: # чтобы сформировать письмо
    def __init__(self, smtp_server, smtp_port, smtp_subject, smtp_from_addr, smtp_body, handle_file, template, max_threads = 15):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_subject = smtp_subject
        self.smtp_from_addr = smtp_from_addr
        self.smtp_body = smtp_body
        self.handle_file = handle_file
        self.template = template

        self.max_threads = max_threads

    def file_adding(self, msg): # метод формирует вложение в письмо
        part = MIMEBase('application', "octet-stream")  # объект для загрузки файла
        part.set_payload(open(self.template, "rb").read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(self.template)}"')
        msg.attach(part)

    def letter_forming(self, receiver): # формирование тела письма + добавление вложений
        msg = MIMEMultipart()
        msg['From'] = self.smtp_from_addr
        msg['To'] = receiver
        msg['Subject'] = self.smtp_subject
        msg.attach(MIMEText(self.smtp_body, 'plain'))
        self.file_adding(msg) # добавление вложения
        return msg

    def send_preparing(self, receiver):#  создание smtp подключения
        msg = self.letter_forming(receiver)
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as smtp_obj: #########!!!!!!!!!!!
            #smtp_obj.set_debuglevel(1)  # отладочные сообщения
            smtp_obj.sendmail(self.smtp_from_addr, receiver, msg.as_string())
        return receiver, True

    @staticmethod
    def chunks(mails, thread_num):
        chunks = []
        for i in range(0, len(mails), thread_num):
            chunks.append(mails[i: i + thread_num])
        return chunks

    def sending(self):
        mails_chunks = self.chunks(self.handle_file, max(len(self.handle_file) // self.max_threads, 1)) # если список меньше числа потоков
        futures = []
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor: #########!!!!!!!!!!!
            for chunk in mails_chunks:
                for receiver in chunk:
                    futures.append(executor.submit(self.send_preparing, receiver))
                    #future.result()

        for future in futures:
            try:
                future.result()
            except Exception as e:
                print(f'Error: {e}')

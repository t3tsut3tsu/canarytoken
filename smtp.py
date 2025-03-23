import os
import smtplib
import threading

from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

class SmtpUnite: # чтобы сформировать письмо
    def __init__(self, smtp_server, smtp_port, smtp_subject, smtp_from_addr, smtp_body, handle_file, template):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_subject = smtp_subject
        self.smtp_from_addr = smtp_from_addr
        self.smtp_body = smtp_body
        self.handle_file = handle_file
        self.template = template

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

    def send_preparing(self, receiver):  #  создание smtp подключения
        msg = self.letter_forming(receiver)
        smtp_obj = smtplib.SMTP(self.smtp_server, self.smtp_port)
        # smtp_obj.set_debuglevel(1)  # отладочные сообщения
        smtp_obj.sendmail(self.smtp_from_addr, receiver, msg.as_string())
        smtp_obj.quit()

    def sending(self): # потоки
        threads = []
        for receiver in self.handle_file:
            thread = threading.Thread(target=self.send_preparing, args=(receiver,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()
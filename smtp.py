import smtplib

#from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from concurrent.futures import ThreadPoolExecutor
from email import encoders


class SmtpUnite: # чтобы сформировать письмо
    def __init__(self, smtp_server, smtp_port, smtp_subject, smtp_from_addr, smtp_body, valid_mails, template, name, max_threads = 15):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_subject = smtp_subject
        self.smtp_from_addr = smtp_from_addr
        self.smtp_body = smtp_body
        self.valid_mails = valid_mails
        self.template = template
        self.name = name

        self.max_threads = max_threads

    def file_adding(self, msg, name): # метод формирует вложение в письмо
        part = MIMEBase('application', "octet-stream")  # объект для загрузки файла
        self.template.seek(0)
        part.set_payload(self.template.getvalue())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{name}"')
        msg.attach(part)

    def letter_forming(self, receiver): # формирование тела письма + добавление вложений
        msg = MIMEMultipart()
        msg['From'] = self.smtp_from_addr
        msg['To'] = receiver
        msg['Subject'] = self.smtp_subject
        msg.attach(MIMEText(self.smtp_body, 'plain'))
        self.file_adding(msg, self.name) # добавление вложения
        return msg

    def send_preparing(self, receiver):#  создание smtp подключения
        msg = self.letter_forming(receiver)
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as smtp_obj:
            smtp_obj.sendmail(self.smtp_from_addr, receiver, msg.as_string())
        return receiver, True

    @staticmethod
    def chunks(mails, thread_num):
        chunks = []
        for i in range(0, len(mails), thread_num):
            chunks.append(mails[i: i + thread_num])
        return chunks

    def sending(self):
        mails_chunks = self.chunks(self.valid_mails, max(len(self.valid_mails) // self.max_threads, 1)) # если список меньше числа потоков
        futures = []
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            for chunk in mails_chunks:
                for receiver in chunk:
                    futures.append(executor.submit(self.send_preparing, receiver))

        for future in futures:
            try:
                future.result()
            except Exception as e:
                print(f'Error: {e}')

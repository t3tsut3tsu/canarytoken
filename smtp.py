import smtplib
import logging
import logger

from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from concurrent.futures import ThreadPoolExecutor, as_completed
from email import encoders
from rich.progress import Progress


logger.logger()

class SmtpUnite: # чтобы сформировать письмо
    def __init__(self, smtp_server, smtp_port, smtp_subject, smtp_from_addr, smtp_body, valid_mails, template, name, db, description, max_threads = 15):
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
        self.failed_sends = []
        self.description = description

    def file_adding(self, msg, template): # метод формирует вложение в письмо
        part = MIMEBase('application', 'octet-stream')
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

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as smtp_obj:
                smtp_obj.sendmail(self.smtp_from_addr, receiver, msg.as_string())

            if self.db is not None:
                get_time = datetime.now()
                token = self.token_by_receiver(receiver)
                self.db.db_insert_from_smtp(token, get_time) # Подумать

            return receiver, True, None

        except smtplib.SMTPConnectError as e:
            error_code = e.smtp_code if hasattr(e, 'smtp_code') else None
            reason = f'smtp_connect_error_{error_code}' if error_code else 'smtp_connect_error'
            logging.error(f'SMTPConnectError for {receiver}: {e}')
            return receiver, False, reason

        except smtplib.SMTPResponseException as e:
            error_code = e.smtp_code
            error_msg = e.smtp_error.decode() if isinstance(e.smtp_error, bytes) else str(e.smtp_error)

            if error_code == 550:
                reason = 'mailbox_not_found'
            elif error_code == 552:
                reason = 'mailbox_full'
            elif error_code == 553:
                reason = 'mailbox_syntax_error'
            else:
                reason = f'smtp_error_{error_code}'

            logging.error(f'SMTPResponseException for {receiver}: {error_code} - {error_msg}')
            return receiver, False, reason

        except ConnectionRefusedError as e:
            reason = 'connection_refused'
            logging.error(f'Connection error for {receiver}: {e}')
            return receiver, False, reason

        except TimeoutError as e:
            reason = 'timeout'
            logging.error(f'Timeout error for {receiver}: {e}')
            return receiver, False, reason

        except smtplib.SMTPServerDisconnected as e:
            error_msg = str(e)
            reason = 'server_disconnected'

            if 'WinError 10054' in error_msg:
                reason = 'connection_reset_by_peer'
            elif 'WinError 10053' in error_msg:
                reason = 'connection_aborted_by_host'

            logging.error(f'SMTPServerDisconnected for {receiver}: {reason} - {error_msg}')
            return receiver, False, reason

        except Exception as e:
            logging.error(f'Unexpected error for {receiver}: {e}')
            return receiver, False, 'unknown_error'

    def token_by_receiver(self, receiver):
        cursor = self.db.get_connection().cursor()
        self.db.selecting_token(cursor, receiver) # Подумать
        row = cursor.fetchone()
        return row['token'] if row else None

    @staticmethod
    def chunks(mails, thread_num):
        chunks = []
        for i in range(0, len(mails), thread_num):
            chunks.append(mails[i: i + thread_num])
        return chunks

    def sending(self):
        if not self.template: # для неверного формата файла
            return
        logging.debug('Sending will start any second now...')
        mails_chunks = self.chunks(self.valid_mails, max(len(self.valid_mails) // self.max_threads, 1)) # если список меньше числа потоков

        total_emails = len(self.valid_mails)
        self.failed_sends = []

        with Progress() as progress:
            task = progress.add_task('[red]Sending emails...', total=total_emails)
            with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
                futures = []
                for chunk in mails_chunks:
                    for i, receiver in enumerate(chunk):
                        index = self.valid_mails.index(receiver)
                        template = self.template[index]
                        futures.append(executor.submit(self.send_preparing, receiver, template))

                for future in as_completed(futures):
                    try:
                        receiver, success, error_reason = future.result()
                        if not success:
                            if self.db is not None:
                                try:
                                    self.db.db_insert_smtp_failure(
                                        email=receiver,
                                        sender=self.smtp_from_addr,
                                        description=self.description,
                                        reason=error_reason
                                    )
                                except Exception as db_error:
                                    logging.error(f'Failed to record failed email in DB: {db_error}')
                        progress.update(task, advance=1)
                    except Exception as e:
                        logging.error(f'Error processing email: {e}')
                        progress.update(task, advance=1)

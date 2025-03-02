import os
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from validate import Validate
from validate import ConfigAction

class SmtpUnite: # Вообще для того, чтобы сформировать письмо
    def __init__(self): # Для экземпляров классов
        self.validator = Validate()
        self.handle_file = self.validator.handle_file()
        self.extension_identify = self.validator.extension_identify()
        self.validator = ConfigAction()
        self.smtp_server, self.smtp_port, self.smtp_subject, self.smtp_from_addr, self.smtp_body = self.validator.smtp_configure()

    def letter_forming(self):
        from_addr = self.smtp_from_addr
        subject = self.smtp_subject
        receivers = self.handle_file
        body = self.smtp_body

        msg = MIMEMultipart()
        msg['From'] = from_addr
        msg['To'] = receivers
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        template = self.extension_identify
        part = MIMEBase('application', "octet-stream") # объект для загрузки файла
        part.set_payload(open(template, "rb").read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',f'attachment; filename="{os.path.basename(template)}"')
        msg.attach(part)

        smtp_obj = smtplib.SMTP(self.smtp_server, self.smtp_port)
        smtp_obj.set_debuglevel(1)
        for to_addr in self.handle_file:
            smtp_obj.sendmail(from_addr, to_addr, msg.as_string())
        smtp_obj.quit()

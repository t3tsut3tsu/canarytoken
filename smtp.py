import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
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

        smtp_obj = smtplib.SMTP(self.smtp_server, self.smtp_port)
        smtp_obj.set_debuglevel(1)

        msg = MIMEMultipart()
        msg['From'] = from_addr
        msg['To'] = receivers
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        template = self.extension_identify
            #to_addr = ""
            #smtp_obj.sendmail(from_addr, to_addr, msg)

        smtp_obj.quit()


import configparser
import smtplib

from validate import Validate
from validate import ConfigAction

class SmtpUnite:
    def __init__(self, **kwargs):
        self.validator = Validate()
        self.validator = ConfigAction()
        self.smtp_server, self.smtp_port = self.validator.smtp_configure()

    def letter_forming(self):
        from_addr = "phishing@marvel.com"

        smtp_obj = smtplib.SMTP(self.smtp_server, self.smtp_port)
        smtp_obj.set_debuglevel(1)

            #to_addr = ""
            #smtp_obj.sendmail(from_addr, to_addr, msg)

        smtp_obj.quit()
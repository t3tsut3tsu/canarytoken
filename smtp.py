import configparser
import smtplib

from validate import Validate
from validate import ConfigAction

class SmtpUnite:
    validator = Validate()

    def letter_forming(self):
        from_addr = "phishing@marvel.com"
        to_addr = ""

        smtp_obj = smtplib.SMTP("localhost")
        smtp_obj.set_debuglevel(1)

            #smtp_obj.sendmail(from_addr, to_addr, msg)

        smtp_obj.quit()
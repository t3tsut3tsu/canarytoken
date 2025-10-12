import argparse
import configparser
import re

from datetime import datetime


class ConfigParse:
    def __init__(self, config_path): # путь до конфига в аргументы переместить
        self.config = configparser.ConfigParser()
        self.config.read(config_path)

    def smtp_configure(self):
        smtp_server = self.config.get('smtp', 'smtp_server')
        smtp_port = self.config.get('smtp', 'smtp_port')
        smtp_subject = self.config.get('smtp', 'subject')
        smtp_from_addr = self.config.get('smtp', 'from_addr')
        smtp_body = self.config.get('smtp', 'body')
        return smtp_server, smtp_port, smtp_subject, smtp_from_addr, smtp_body

    def db_configure(self):
        db_path = self.config.get('database', 'db_path')
        db_merged_path = self.config.get('database', 'db_merged_path')
        db_backups = self.config.get('database', 'db_backups')
        return db_path, db_merged_path, db_backups

    def template_configure(self):
        dir_new_templates = self.config.get('templates', 'dir_new_templates')
        return dir_new_templates

    def smb_configure(self):
        smb_server = self.config.get('smb', 'smb_server')
        return smb_server

    def http_configure(self):
        http_server = self.config.get('http', 'http_server')
        http_port = self.config.get('http', 'http_port')
        return http_server, int(http_port)

    def rep_configure(self):
        dir_report = self.config.get('report', 'dir_report')
        rep_name = self.config.get('report', 'rep_name')
        return dir_report, rep_name

class ArgParse: # класс для обработки аргументов командной строки
    def __init__(self, emails, extension, server, port, description, name):
        self.emails = emails
        self.extension = extension
        self.server = server
        self.port = port
        self.description = description
        self.name = name

    @staticmethod
    def parser_args():
        parser = argparse.ArgumentParser(prog='canarytoken', description='Sends template to email addresses and '
                                                     'then we\'ll start listening and '
                                                     'waiting for the result until...', epilog='...trust is broken due to honey token.') # объект-обработчик аргументов ArgumentParser
        parser.add_argument('--emails', type=argparse.FileType('r'), help='set the file with an email addresses')
        parser.add_argument('--config', type=str, default='config.ini', help='set the config file')
        parser.add_argument('-d', '--description', action='append', type=str, help='add a description to your research (if None, will specify the date)')
        parser.add_argument('-n', '--name', type=str, default='template.xml', help='set a name for template file')
        parser.add_argument('--mode', type=str, choices=['attack', 'listener', 'send', 'static', 'report', 'merge'], required=True, help=(
                'attack - only attack (listener + send); '
                'listener - only listener; '
                'send - only send; '
                'static - create honey token; '
                'report - generate report; '
                'merge - merging databases to create one common report. '
        )    )

        return parser.parse_args()

class Validate:
    def __init__(self, emails, description):
        self.emails = emails
        self.description = description

    def handle_file(self): # проверка корректности списка почт, поиск дубликатов
        invalid_emails = []
        valid_emails = []
        duplicates = set() # множество для уникальных почт

        try:
            with self.emails as f:
                emails = [email.strip() for email in f]
                if not emails:
                    return valid_emails, invalid_emails
        except Exception as e:
            print(f'Error: {e}')
            return valid_emails, invalid_emails

        regex = re.compile('[A-Za-z0-9._!$^*%+-]+@[A-Za-z0-9._!$^*%+-]+[A-Za-z-0-9]{2,}')
        for email in emails:
            if email in duplicates:  # проверка на дублирование из множества
                invalid_emails.append(email)
            else:
                duplicates.add(email)
                if re.fullmatch(regex, email):
                    valid_emails.append(email)
                else:
                    invalid_emails.append(email)

        return valid_emails, invalid_emails

    def description_checking(self): # вместо описания | возможно, лучше убрать и сделать description обязательным аргументом
        if not self.description:
            self.description = datetime.now().isoformat(sep=' ', timespec='seconds')
        return self.description

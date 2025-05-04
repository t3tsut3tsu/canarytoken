import argparse
import configparser
#import os
import re

from datetime import datetime


class ConfigParse:
    def __init__(self): #, config_path): # путь до конфига в аргументы
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

    def smtp_configure(self):
        smtp_server = self.config.get('smtp', 'smtp_server')
        smtp_port = self.config.get('smtp', 'smtp_port')
        smtp_subject = self.config.get('smtp', 'subject')
        smtp_from_addr = self.config.get('smtp', 'from_addr')
        smtp_body = self.config.get('smtp', 'body')
        return smtp_server, smtp_port, smtp_subject, smtp_from_addr, smtp_body

    def db_configure(self):
        db_path = self.config.get('database', 'db_path')
        return db_path

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

class ArgParse: # класс для обработки аргументов командной строки
    def __init__(self, mail_list, extension, server, port, description, name):
        self.mail_list = mail_list
        self.extension = extension
        self.server = server
        self.port = port
        self.description = description
        self.name = name

    @staticmethod
    def parser_args():
        parser = argparse.ArgumentParser(description='Sends template to email addresses and '
                                                     'then we\'ll start listening and '
                                                     'waiting for the result until...', epilog='...trust is broken due to honey token.') # объект-обработчик аргументов ArgumentParser
        parser.add_argument('mail_list', type=argparse.FileType('r'), help='set the file with an email addresses')
        parser.add_argument('-e', '--extension', choices=['docx', 'pdf', 'xlsx', 'xml'], default='xml', help='set the template\'s extension')
        parser.add_argument('-d', '--description', type=str, help='add a description to your research (if None, will specify the date)')
        parser.add_argument('-n', '--name', type=str, default='template.xml', help='set a name for template file')
        parser.add_argument('--mode', type=int, choices=range(1, 6), required=True, help=(
                '1 - only attack (listener + send); '
                '2 - only listener; '
                '3 - only send; '
                '4 - static (create honey token); '
                '5 - report. '
        )    )

        return parser.parse_args()

class Validate:
    def __init__(self,  mail_list, description): # здесь был **kwargs |
        self.mail_list = mail_list
        self.description = description

    def handle_file(self): # проверка корректности списка почт, поиск дубликатов
        invalid_emails = []
        valid_emails = []
        duplicates = set() # множество для уникальных почт

        try:
            with self.mail_list as f:
                emails = [email.strip() for email in f]
                if not emails:
                    print("EMPTY")
                    return valid_emails, invalid_emails
        except Exception as e:
            print(f'Error: {e}')
            return valid_emails, invalid_emails

        regex = re.compile("[A-Za-z0-9._!$^*%+-]+@[A-Za-z0-9._!$^*%+-]+[A-Za-z-0-9]{2,}")
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

    def description_checking(self): # вместо описания
        if not self.description:
            self.description = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return self.description

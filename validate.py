import argparse
import configparser
import os
import re

class ConfigAction: # класс для обработки конфиг файла
    @staticmethod
    def load_config():
        config = configparser.ConfigParser()
        config.read('config.ini')
        return config

    @staticmethod
    def smtp_configure(config):
        smtp_server = config.get('smtp', 'smtp_server')
        smtp_port = config.get('smtp', 'smtp_port')
        smtp_subject = config.get('smtp', 'subject')
        smtp_from_addr = config.get('smtp', 'from_addr')
        smtp_body = config.get('smtp', 'body')
        return smtp_server, smtp_port, smtp_subject, smtp_from_addr, smtp_body
    # Далее другие static методы для обработки разделов конфиги
class Parse: # класс для обработки аргументов командной строки
    @staticmethod
    def parser_args():
        parser = argparse.ArgumentParser(description="Sends template to email addresses and "
                                                     "then we'll start listening and "
                                                     "waiting for the result until...", epilog="...trust is broken due to honey token.") # объект-обработчик аргументов ArgumentParser
        parser.add_argument('mail_list', type=argparse.FileType('r'), help="set file with email addresses")# позиционный арг., содержит путь к файлу с адресами
        parser.add_argument('--extension', choices=['docx', 'pdf', 'xlsx', 'xml'], default='docx', help="set template's extension") # опциональный арг., содержит формат файла-шаблона для отправки
        return parser.parse_args() # возвращает объект с доступом к значениям аргументов

class Validate:
    def __init__(self,  mail_list=None, extension=None): # инициализатор для аргументов | здесь был **kwargs
        self.mail_list = mail_list
        self.extension = extension

    def handle_file(self): # обработчик почт
        try:
            with self.mail_list as f: # файл, переданный как аргумент
                emails = [email.strip() for email in f]
            regex = re.compile(r'[A-Za-z0-9]+([._!$^*-]|[A-Za-z0-9])+@[A-Za-z0-9]+([._!$^*-]|[A-Za-z0-9])+[.]+[a-z]{2,}')
            valid_emails = []
            for email in emails:
                if re.fullmatch(regex, email):
                    valid_emails.append(email)
                else:
                    print(f"Invalid: {email}") # отладка
            return valid_emails
        except FileNotFoundError:
            print("No such file")
        except IOError:
            print("EoF Err")

    def extension_identify(self):
        if self.extension == 'docx':
            return os.path.join('templates','template.docx')#, "\n docx extension selected"
        elif self.extension == 'xml':
            return os.path.join('templates','template.xml')
        elif self.extension == 'pdf':
            return self.extension#, "\n pdf extension selected"
        elif self.extension == 'xlsx':
            return self.extension#, "\n xlsx extension selected"

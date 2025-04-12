import argparse
import configparser
import re

from datetime import datetime

class ConfigAction: # класс для обработки конфиг файла
    def __init__(self):
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
        db_name = self.config.get('database', 'db_name')
        table_name = self.config.get('database', 'table_name')
        return db_name, table_name

    def listen_configure(self):
        listen_address = self.config.get('listen', 'listen_address')
        listen_port = self.config.get('listen', 'listen_port')
        return listen_address, listen_port

    def template_configure(self):
        dir_new_templates = self.config.get('templates', 'dir_new_templates')
        return dir_new_templates

class Parse: # класс для обработки аргументов командной строки
    @staticmethod
    def parser_args():
        parser = argparse.ArgumentParser(description="Sends template to email addresses and "
                                                     "then we'll start listening and "
                                                     "waiting for the result until...", epilog="...trust is broken due to honey token.") # объект-обработчик аргументов ArgumentParser
        parser.add_argument('mail_list', type=argparse.FileType('r'), help="set the file with an email addresses")# позиционный арг., содержит путь к файлу с адресами
        parser.add_argument('-e', '--extension', choices=['docx', 'pdf', 'xlsx', 'xml'], default='xml', help="set the template's extension") # опциональный арг., содержит формат файла-шаблона для отправки
        parser.add_argument('-s', '--server', type=str, default='127.0.0.1', help="set an ip address for a tracking")
        parser.add_argument('-p', '--port', type=str,help="set a port for a tracking (if needed)")
        parser.add_argument('-d', '--description', type=str, help="add a description to your research (if None, will specify the date)")
        parser.add_argument('-n', '--name', type=str, default='template.xml', help="set a name for template file")

        return parser.parse_args() # возвращает объект с доступом к значениям аргументов

class Validate:
    def __init__(self,  mail_list=None, extension=None, description=None): # инициализатор для аргументов | здесь был **kwargs |
        self.mail_list = mail_list
        self.extension = extension
        self.description = description

    def handle_file(self): # обработчик почт
        try:
            with self.mail_list as f: # файл, переданный как аргумент
                emails = [email.strip() for email in f]
            regex = re.compile("[A-Za-z0-9._!$^*%+-]+@[A-Za-z0-9._!$^*%+-]+[A-Za-z-0-9]{2,}") #(r'[A-Za-z0-9]+([._!$^*-]|[A-Za-z0-9])+@[A-Za-z0-9]+([._!$^*-]|[A-Za-z0-9])+[.]+[a-z]{2,}'))
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

    def description_checking(self):
        if not self.description:
            self.description = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self.description

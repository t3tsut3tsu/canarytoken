import argparse
import configparser
import re

from datetime import datetime
#from importlib.metadata import pass_none


class ConfigParse: # класс для обработки конфиг файла
    def __init__(self): #, config_path):
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

    #def listen_configure(self): # параметры слушателя теперь передаются из командной строки
    #    listen_address = self.config.get('listen', 'listen_address')
    #    listen_port = self.config.get('listen', 'listen_port')
    #    return listen_address, listen_port

    def template_configure(self):
        dir_new_templates = self.config.get('templates', 'dir_new_templates')
        return dir_new_templates

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
        parser = argparse.ArgumentParser(description="Sends template to email addresses and "
                                                     "then we'll start listening and "
                                                     "waiting for the result until...", epilog="...trust is broken due to honey token.") # объект-обработчик аргументов ArgumentParser
        parser.add_argument('mail_list', type=argparse.FileType('r'), help="set the file with an email addresses")
        parser.add_argument('-e', '--extension', choices=['docx', 'pdf', 'xlsx', 'xml'], default='xml', help="set the template's extension")
        parser.add_argument('-s', '--server', type=str, default='127.0.0.1', help="set an ip address for a tracking")
        parser.add_argument('-p', '--port', type=int, help="set a port for a tracking")
        parser.add_argument('-d', '--description', type=str, help="add a description to your research (if None, will specify the date)")
        parser.add_argument('-n', '--name', type=str, default='template.xml', help="set a name for template file")

        return parser.parse_args() # возвращает объект с доступом к значениям аргументов

class Validate:
    def __init__(self,  mail_list, description): # инициализатор для аргументов | здесь был **kwargs |
        self.mail_list = mail_list
        self.description = description

    def handle_file(self): # обработчик почт
        invalid_emails = []
        try:
            with self.mail_list as f: # файл, переданный как аргумент #########!!!!!!!!!!!
                emails = [email.strip() for email in f]
            regex = re.compile("[A-Za-z0-9._!$^*%+-]+@[A-Za-z0-9._!$^*%+-]+[A-Za-z-0-9]{2,}")
            valid_emails = []
            for email in emails:
                if re.fullmatch(regex, email):
                    valid_emails.append(email)
                else:
                    invalid_emails.append(email) #print(f"Invalid: {email}") # отладка
            return valid_emails, invalid_emails
        except FileNotFoundError:
            print("No such file")
        except IOError:
            print("EoF Err")
        except Exception as e:
            print(f'Error: {e}')

    def description_checking(self):
        if not self.description:
            self.description = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self.description

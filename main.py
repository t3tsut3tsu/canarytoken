import argparse
import configparser
import re

class ConfigAction: # класс для обработки конфиг файла, который пока что ничего не обрабатывает
    def values_print(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        for key in config['smtp']:
            print(f"{key} = {config['smtp'][key]}")
class Parse: # класс для обработки аргументов командной строки
    def parser_args(self):
        parser = argparse.ArgumentParser(description="Sends template to email addresses and "
                                                     "then we'll start listening and "
                                                     "waiting for the result until...", epilog="...trust is broken due to honey token.") # объект-обработчик аргументов ArgumentParser
        parser.add_argument('mail_list', type=argparse.FileType('r'), help='set file with email addresses')# позиционный арг., содержит путь к файлу с адресами
        parser.add_argument('--extension', choices=['docx', 'pdf', 'xlsx'], default='docx', help="set template's extension") # опциональный арг., содержит формат файла-шаблона для отправки
        parser.add_argument('-p', '--port', type=int, default=25,help="set SMTP-port for sending") # опциональный арг., выбор порта для отправки письма по SMTP | пока нет обработки
        parser.add_argument('--sender', type=str, default='test@example', help='set sender email address') # опциональный арг., выбор почтового адреса отправителя | пока нет обработки
        parser.add_argument('--server', type=str, default='smtp.example', help='set sender server address') # опциональный арг., выбор адреса почтового сервера отправителя | пока нет обработки
        return parser.parse_args() # возвращает объект с доступом к значениям аргументов

class Validate:
    def __init__(self, **kwargs): # инициализатор для аргументов
        self.mail_list = kwargs.get('mail_list')
        self.extension = kwargs.get('extension')
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
            return "\ndocx extension selected"


args = Parse().parser_args()
valid = Validate(mail_list=args.mail_list, extension=args.extension) # экземпляр класса Validate
conf = ConfigAction()

valid_mails = valid.handle_file()
file_format = valid.extension_identify()

print(valid_mails)
print(file_format)
print(conf)

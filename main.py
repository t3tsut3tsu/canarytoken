import argparse
import re

print('Canary token v.0\n')
# класс для обработки аргументов командной строки
class Parse:
    def parser_args(self):
        parser = argparse.ArgumentParser(description="Takes the templates and sends them to the \
        addresses. Then we'll start listening and waiting for the result until...", epilog="...trust is broken due to honeytoken.") #объект-обработчик аргументов ArgumentParser
        parser.add_argument('mail_list', type=argparse.FileType('r'), help='Set the file with the email addresses') #позиционный арг., содержит путь к файлу с адресами
        return parser.parse_args() #возвращает объект с доступом к значениям введенных пользователем аргументов

class Validate:
    def __init__(self, mail_list): #инициализатор для файла со списком
        self.mail_list = mail_list
    def handle_file(self): #обработчик почт
        #файл, переданный как аргумент
        with self.mail_list as f:
            emails = [email.strip() for email in f]
        regex = re.compile(r'[A-Za-z0-9]+([._!$^*-]|[A-Za-z0-9])+@[A-Za-z0-9]+([._!$^*-]|[A-Za-z0-9])+[.]+[a-z]{2,}')
        valid_emails = []
        for email in emails:
            if re.fullmatch(regex, email):
                valid_emails.append(email)
            else:
                print(f"Invalid: {email}") #отладка
        return valid_emails

args = Parse().parser_args()
valid = Validate(args.mail_list)
valid_emails = valid.handle_file()
print(valid_emails)
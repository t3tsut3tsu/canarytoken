import argparse
import re

print('Canary token v.0\n')

parser = argparse.ArgumentParser()
parser.add_argument('load_file', type=argparse.FileType('r'))
args = parser.parse_args()

class Menu:
    def handle_file(self):
        regex = re.compile(r'[A-Za-z0-9]+([._!$^*-]|[A-Za-z0-9])+@[A-Za-z0-9]+([._!$^*-]|[A-Za-z0-9])+[.]+[a-z]{2,}')
        #файл, переданный как аргумент
        with args.load_file as f:
            emails = [email.strip() for email in f]
        valid_emails = []
        for email in emails:
            #print(f"Check: {email}") #отладка
            if re.fullmatch(regex, email):
                #print(f"Valid: {email}") # отладка
                valid_emails.append(email)
            else:
                print(f"Invalid: {email}") #отладка
        return valid_emails

menu = Menu()
valid_emails = menu.handle_file()
print(valid_emails)
import time

from database import Database
from validate import ConfigAction, Validate, Parse
from smtp import SmtpUnite
from time_tracker import execution_time

def main():
    start_time = time.perf_counter() # отсчет времени

    valid = Validate(mail_list=Parse.parser_args().mail_list, extension=Parse.parser_args().extension, description=Parse.parser_args().description) # экземпляр класса Validate
    start_time = execution_time(start_time, "create valid") # отсчет времени

    conf = ConfigAction() # экземпляр класса ConfigAction
    start_time = execution_time(start_time, "create config") # отсчет времени

    valid_mails = valid.handle_file() # файл с валидными почтами
    start_time = execution_time(start_time, "valid_mails") # отсчет времени

    file_format = valid.extension_identify() # расширение файла
    start_time = execution_time(start_time, "file_format") # отсчет времени

    description = valid.description_checking()
    start_time = execution_time(start_time, "description") # отсчет времени

    conf_smtp = conf.smtp_configure() # конфиг файл
    start_time = execution_time(start_time, "conf_smtp") # отсчет времени

    conf_db = conf.db_configure()
    db = Database(*conf_db)
    db.db_creating()
    db.db_insert(valid_mails, description)
    db.db_closing()
    start_time = execution_time(start_time, "db insert") # отсчет времени

    print(valid_mails)

    send = SmtpUnite(*conf_smtp, valid_mails, file_format)
    send.sending()

    start_time = execution_time(start_time, "after sending") # отсчет времени

if __name__ == "__main__":
    main()
import time

from database import Database
from validate import ConfigAction, Validate, Parse
from smtp import SmtpUnite
from time_tracker import execution_time

start_time = time.perf_counter()

valid = Validate(mail_list=Parse.parser_args().mail_list, extension=Parse.parser_args().extension, description=Parse.parser_args().description) # экземпляр класса Validate
start_time = execution_time(start_time, "create valid")

conf = ConfigAction() # экземпляр класса ConfigAction
start_time = execution_time(start_time, "create config")

valid_mails = valid.handle_file() # файл с валидными почтами
start_time = execution_time(start_time, "valid_mails")

file_format = valid.extension_identify() # расширение файла
start_time = execution_time(start_time, "file_format")

description = valid.description_checking()
start_time = execution_time(start_time, "description")

conf_smtp = conf.smtp_configure() # конфиг файл
start_time = execution_time(start_time, "conf_smtp")

conf_db = conf.db_configure()
db = Database(*conf_db)
db.db_creating()
db.db_insert(valid_mails, description)
db.db_closing()
start_time = execution_time(start_time, "db insert")

print(valid_mails)

send = SmtpUnite(*conf_smtp, valid_mails, file_format)
send.sending()

start_time = execution_time(start_time, "after sending")
import time
import signal
import sys

from multiprocessing import Process
from database import Database
from validate import ConfigParse, Validate, ArgParse
from template import Template
from smtp import SmtpUnite
from listener import Listener
from time_tracker import execution_time

def listening(server, port):
    listen = Listener(server, port)
    listen.listener()

def main(server, port, mail_list, description, extension, name):
    start_time = time.perf_counter() # отсчет времени

    valid = Validate(mail_list, description=description) # экземпляр класса Validate
    #start_time = execution_time(start_time, "create valid") # отсчет времени

    conf = ConfigParse() # экземпляр класса ConfigParse
    #start_time = execution_time(start_time, "create config") # отсчет времени

    conf_template = conf.template_configure()

    template = Template(server, port, name=name, dir_new_templates=conf_template) # экземпляр класса Template

    if extension == 'xml':
        file_format = template.link_changing_xml()
    elif extension == 'docx':
        file_format = template.link_changing_docx()
    elif extension == 'xlsx':
        file_format = template.link_changing_xlsx()
    elif extension == 'pdf':
        file_format = template.link_changing_pdf()
    else:
        return False

    valid_mails, invalid_mails = valid.handle_file() # файл с валидными почтами
    print(f"Valid: {valid_mails}")
    print(f"Invalid: {invalid_mails}")
    #start_time = execution_time(start_time, "valid_mails") # отсчет времени

    description = valid.description_checking()
    #start_time = execution_time(start_time, "description") # отсчет времени

    conf_smtp = conf.smtp_configure() # конфиг файл
    #start_time = execution_time(start_time, "conf_smtp") # отсчет времени

    conf_db = conf.db_configure()
    db = Database(conf_db)
    db.db_creating()
    db.db_insert(valid_mails, description)
    db.db_closing()
    #start_time = execution_time(start_time, "db insert") # отсчет времени

    send = SmtpUnite(*conf_smtp, valid_mails, file_format)
    send.sending()

    start_time = execution_time(start_time, "after sending") # отсчет времени

if __name__ == "__main__":
    args = ArgParse.parser_args() #в listener и main нужны server, port | чтобы не дублировать

    mail_list = args.mail_list
    extension = args.extension
    description = args.description
    server = args.server
    port = args.port
    name = args.name

    listener_proc = Process(target=listening, args=(server, port))
    listener_proc.start()

    main(server, port, mail_list, description, extension, name)

    try:
        listener_proc.join()
    except KeyboardInterrupt:
        listener_proc.terminate()
        listener_proc.join()

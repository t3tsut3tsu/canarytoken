import time

from multiprocessing import Process, Value
from database import Database
from validate import ConfigParse, Validate, ArgParse
from template import Template
from smtp import SmtpUnite
from listener import Listener
from time_tracker import execution_time

def listening(http_server, http_port, listener_activity):
    listen = Listener(http_server, http_port)
    if listener_activity.value == 0:
        print("Listener is not running")
    else:
        listen.listener()

def main(http_server, http_port, smb_server, mail_list, description, extension, name, listener_activity):
    start_time = time.perf_counter() # отсчет времени

    valid = Validate(mail_list, description=description)

    conf = ConfigParse()

    conf_template = conf.template_configure()

    template = Template(
        http_server,
        http_port,
        smb_server,
        name=name,
        dir_new_templates=conf_template
    )

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

    valid_mails, invalid_mails = valid.handle_file()
    print(f"    Valid: {valid_mails}\n")
    print(f"    Invalid: {invalid_mails}")

    if not valid_mails:
        print("No valid, all invalid!!!")
        listener_activity.value = 0
        return

    description = valid.description_checking()

    conf_smtp = conf.smtp_configure() # конфиг файл

    conf_db = conf.db_configure()
    db = Database(conf_db)
    db.db_creating()
    db.db_insert(valid_mails, description)
    db.db_closing()

    send = SmtpUnite(*conf_smtp, valid_mails, file_format)
    send.sending()

    start_time = execution_time(start_time, "after sending") # отсчет времени

if __name__ == "__main__":
    args = ArgParse.parser_args() #в listener и main нужны server, port | чтобы не дублировать

    mail_list = args.mail_list
    extension = args.extension
    description = args.description
    http_server = args.http_server
    http_port = args.http_port
    smb_server = args.smb_server
    name = args.name

    listener_activity = Value('i', 1)
    listener_proc = Process(target=listening, args=(http_server, http_port, listener_activity))
    listener_proc.start()

    main(http_server, http_port, smb_server, mail_list, description, extension, name, listener_activity)

    try:
        listener_proc.join()
    except KeyboardInterrupt:
        listener_proc.terminate()
        listener_proc.join()

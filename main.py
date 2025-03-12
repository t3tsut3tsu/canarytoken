from validate import ConfigAction, Validate, Parse
from smtp import SmtpUnite

valid = Validate(mail_list=Parse().parser_args().mail_list, extension=Parse().parser_args().extension) # экземпляр класса Validate
conf = ConfigAction() # экземпляр класса ConfigAction

valid_mails = valid.handle_file() # файл с валидными почтами
file_format = valid.extension_identify() # расширение файла
conf_smtp = conf.smtp_configure() # конфиг файл

print(valid_mails)
#print(file_format)
#print(conf_smtp)

send = SmtpUnite(*conf_smtp, valid_mails, file_format)
send.sending()
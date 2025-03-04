from validate import ConfigAction, Validate, Parse
from smtp import SmtpUnite

args = Parse().parser_args() # экземпляр класса Parse
valid = Validate(mail_list=args.mail_list, extension=args.extension) # экземпляр класса Validate
conf = ConfigAction() # экземпляр класса ConfigAction

valid_mails = valid.handle_file() # файл с валидными почтами
file_format = valid.extension_identify() # расширение файла
conf_file = conf.smtp_configure() # конфиг файл

print(valid_mails)
print(file_format)
print(conf_file)

send = SmtpUnite(*conf_file, valid_mails, file_format)
send.sending()
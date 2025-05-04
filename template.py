import base64
import io
import os

from lxml import etree


class Encode:
    def __init__(self, valid_mails):
        self.valid_mails = valid_mails

    def encoding(self):
        encoded = []
        for i in self.valid_mails:
            encoded.append(base64.b64encode(i.encode()).decode())
        return encoded

    @staticmethod
    def decoding(encoded):
        decoded = []
        for i in encoded:
            decoded.append(base64.b64decode(i.encode()).decode())
        return decoded

class Template:
    def __init__(self, http_server, http_port, smb_server, name, dir_new_templates):
        self.http_server = http_server
        self.http_port = http_port
        self.smb_server = smb_server
        self.name = name
        self.dir_new_templates = dir_new_templates

    def link_changing_xml(self, valid_mails=None, save=False):
        file_path = os.path.join('templates','template.xml')

        tree = etree.parse(file_path)
        root = tree.getroot()

        new_smb = f'smb://{self.smb_server}/canary.png'
        new_http = f'http://{self.http_server}:{self.http_port}/canary.png'

        #if not save:
        #for email in valid_mails:
            #new_smb = f'smb://{self.smb_server}?={email}/canary.png'
            #new_http = f'http://{self.http_server}:{self.http_port}?={email}/canary.png'

        for relationship in root.findall('.//{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'):
            target = relationship.get('Target')
            if target ==  'smb://127.0.0.1:4444/canary.png':
                relationship.set('Target', new_smb)
            elif target == 'http://127.0.0.1:4444/canary.png':
                relationship.set('Target', new_http)

        buffer = io.BytesIO()
        tree.write(buffer, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        buffer.seek(0)

        if save:
            output_path = os.path.join(self.dir_new_templates, self.name)
            with open(output_path, 'wb') as f:
                f.write(buffer.getvalue())
            print(f'File was save to {self.dir_new_templates}')
            return output_path
        else:
            return buffer

    def link_changing_docx(self):
        pass

    def link_changing_xlsx(self):
        pass

    def link_changing_pdf(self):
        pass

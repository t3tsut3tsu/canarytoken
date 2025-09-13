import base64
import io
import os
import uuid
import zipfile

from lxml import etree


class Encode:
    def __init__(self, valid_mails):
        self.valid_mails = valid_mails

    def encoding(self):
        encoded = []
        for i in self.valid_mails:
            unique_id = str(uuid.uuid4())
            encoded_email = f'{unique_id}:{base64.b64encode(i.encode()).decode()}'
            encoded.append(encoded_email)
        return encoded

    @staticmethod
    def decoding(encoded):
        decoded = []
        for i in encoded:
            unique_id, encoded_email = i.split(':', 1)
            decoded.append(base64.b64decode(encoded_email.encode()).decode())
        return decoded

class Template:
    def __init__(self, http_server, http_port, smb_server, name, dir_new_templates):
        self.http_server = http_server
        self.http_port = http_port
        self.smb_server = smb_server
        self.name = name
        self.dir_new_templates = dir_new_templates

    def link_changing_xml(self, encoded=None, save=False):
        #if not encoded: # для пустого списка почт
        #    return None # эта херня сломала мне static, переделать

        xml_data_list = []
        file_path = os.path.join('templates', 'template.xml')

        if not save:
            for mail in encoded:
                tree = etree.parse(file_path)
                root = tree.getroot()
                for relationship in root.findall('.//{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'):
                    target = relationship.get('Target')
                    if target == 'smb://127.0.0.1:4444/canary.png':
                        relationship.set('Target', f'smb://{self.smb_server}?token={mail}')
                    elif target == 'http://127.0.0.1:4444/canary.png':
                        relationship.set('Target', f'http://{self.http_server}:{self.http_port}?token={mail}')

                xml_bytes = io.BytesIO()
                tree.write(xml_bytes, pretty_print=True, xml_declaration=True, encoding='UTF-8')
                xml_bytes.seek(0)
                xml_data_list.append(xml_bytes)

            return xml_data_list

        else:
            tree = etree.parse(file_path)
            root = tree.getroot()
            for relationship in root.findall('.//{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'):
                target = relationship.get('Target')
                if target == 'smb://127.0.0.1:4444/canary.png':
                    relationship.set('Target', f'smb://{self.smb_server}/canary.png')
                elif target == 'http://127.0.0.1:4444/canary.png':
                    relationship.set('Target', f'http://{self.http_server}:{self.http_port}/canary.png')

            output_path = os.path.join(self.dir_new_templates, f'{self.name}')
            tree.write(output_path, pretty_print=True, xml_declaration=True, encoding='UTF-8')
            print(f'File was saved to {self.dir_new_templates}')

            return output_path

    def link_changing_docx(self, encoded=None, save=False):
        # менять word/_rels/document.xml.rels

        docx_path = os.path.join('templates', 'template.docx')
        docx_files = []

        if not save:
            for mail in encoded:
                temp_docx_bytes = io.BytesIO()
                with zipfile.ZipFile(docx_path, 'r') as zip_ref:
                    with zipfile.ZipFile(temp_docx_bytes, 'w') as temp_zip_ref:
                        for item in zip_ref.infolist():
                            if item.filename == 'word/_rels/document.xml.rels':
                                with zip_ref.open(item.filename) as file:
                                    target = file.read().decode('utf-8')
                                    target = target.replace('smb://127.0.0.1:4444/canary.png', f'smb://{self.smb_server}?token={mail}')
                                    target = target.replace('http://127.0.0.1:4444/canary.png', f'http://{self.http_server}:{self.http_port}?token={mail}')
                                    temp_zip_ref.writestr(item.filename, target)
                            else:
                                temp_zip_ref.writestr(item, zip_ref.read(item.filename))

                temp_docx_bytes.seek(0)
                docx_files.append(temp_docx_bytes)

            return docx_files

        else:
            output_path = os.path.join(self.dir_new_templates, f'{self.name}')
            with zipfile.ZipFile(docx_path, 'r') as zip_ref:
                with zipfile.ZipFile(output_path, 'w') as temp_zip_ref:
                    for item in zip_ref.infolist():
                        if item.filename == 'word/_rels/document.xml.rels':
                            with zip_ref.open(item.filename) as file:
                                target = file.read().decode('utf-8')
                                target = target.replace('smb://127.0.0.1:4444/canary.png',f'smb://{self.smb_server}/canary.png')
                                target = target.replace('http://127.0.0.1:4444/canary.png',f'http://{self.http_server}:{self.http_port}/canary.png')
                                temp_zip_ref.writestr(item.filename, target)
                        else:
                            temp_zip_ref.writestr(item, zip_ref.read(item.filename))

            print(f'File was saved to {self.dir_new_templates}')

            return output_path

    def link_changing_xlsx(self):
        pass

    def link_changing_pdf(self):
        pass

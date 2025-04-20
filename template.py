import os

from lxml import etree

class Template:
    def __init__(self, server, port, name, dir_new_templates):
        self.server = server
        self.port = port
        self.name = name

        self.dir_new_templates = dir_new_templates

    def link_changing_xml(self):
        file_path = os.path.join('templates','template.xml')

        tree = etree.parse(file_path)
        root = tree.getroot()

        new_smb = f'smb://{self.server}/canary.png'
        new_http = f'http://{self.server}:{self.port}/canary.png'

        if not self.port:
            new_http = f'http://{self.server}:1337/canary.png'

        for relationship in root.findall(".//{http://schemas.openxmlformats.org/package/2006/relationships}Relationship"):
            target = relationship.get('Target')
            if target == 'smb://127.0.0.1:4444/canary.png':
                relationship.set('Target', new_smb)
            elif target == 'http://127.0.0.1:4444/canary.png':
                relationship.set('Target', new_http)

        output_path = os.path.join(self.dir_new_templates, self.name)
        tree.write(output_path, pretty_print=True, xml_declaration=True, encoding='UTF-8')

        return output_path

    def link_changing_docx(self):
        pass

    def link_changing_xlsx(self):
        pass

    def link_changing_pdf(self):
        pass

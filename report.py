import os
from collections import defaultdict

class RepGenerate:
    def __init__(self, descriptions, dir_report, rep_name, open_num_counts):
        self.descriptions = descriptions
        self.dir_report = dir_report
        self.rep_name = rep_name
        self.open_num_counts = open_num_counts

        if not os.path.exists(self.dir_report):
            os.makedirs(self.dir_report)

    def gen(self, data):
        grouped = defaultdict(list)
        for row in data:
            grouped[row[f'description']].append(row)

        html_parts = []

        html_parts.append('<html>')
        html_parts.append(f'<head><meta charset="UTF-8"><title>{self.rep_name}</title></head>')
        html_parts.append('''
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Ubuntu+Mono:ital,wght@0,400;0,700;1,400;1,700&display=swap');

                body {
                    background-color: #151515;
                    font-family: "Ubuntu Mono", monospace;
                    font-size: 20px;
                    color: #gray;
                }
            
                tbody td:nth-child(odd) {
                    background-color: #e3e5e6;
                }
                
                tbody td:nth-child(even) {
                    background-color: #f3f4f5;
                }
                
                table {
                    width: 80%;
                    border-collapse: collapse;
                    border-radius: 20px;
                    overflow: hidden;
                    margin: auto;
                    margin-bottom: 10px;
                }
                
                th, td {
                    background-color: #a9b2ba;
                    border: 1px solid #000;
                    padding: 8px;
                    text-align: center;
                }
                
                h1 {
                    color: #f3f4f5;
                    text-align: center;
                }
                
                h2 {
                    color: #f3f4f5;
                    margin-left: 10%;
                }
                
                li {
                    color: #f3f4f5;
                    margin-left: 12%;
                    margin-bottom: 5px;
                }
                
                hr {
	                margin: -30px auto 50px;
	                padding: 0;
                    height: 50px;
                    border: none;
                    border-bottom: 1px solid #cb2424;
                    width: 70%;
                }
                
                .red {
                    color: #cb2424;
                }
            </style>
        ''')
        html_parts.append('<body>')

        if len(self.descriptions) > 1:
            descriptions_string = '», «'.join(self.descriptions)
            html_parts.append(f'<h1>Сводный отчет по запускам «{descriptions_string}»</h1><br>')
        for description in self.descriptions:
            if description in grouped:
                rows = grouped[description]
                html_parts.append(f'<h1><span class="red"> » </span>Отчет по запуску «{description}»</h1>')
                html_parts.append(f'<h2>Информация о запуске:</h2>')

                sender = rows[0]['sender']
                launch_time = rows[0]['get_time']
                html_parts.append('<ul type="circle">')
                html_parts.append(f'<li>Отправитель: {sender}</li>'
                                f'<li>Начало запуска: {launch_time}</li>')
                html_parts.append('</ul>')

                html_parts.append(f'<h2>Общее число открытий: {self.open_num_counts[description]}</h2>')
                html_parts.append(f'<h2>Список сработок:</h2>')
                html_parts.append('<table>')
                html_parts.append('<tr><th>Получатель</th><th>IP</th><th>Время отправки</th><th>Время открытия</th><th>Число открытий</th></tr>')
                for row in rows:
                    if row['open_time']:
                        html_parts.append(
                            '<tr>'
                            f'<td>{row["recipient"]}</td>'
                            f'<td>{row["ip_addr"]}</td>'
                            f'<td>{row["get_time"]}</td>'
                            f'<td>{row["open_time"]}</td>'
                            f'<td>{row["open_num"]}</td>'
                            '</tr>'
                        )
                html_parts.append('</table>')
                if len(self.descriptions) > 1:
                    html_parts.append('<hr>')
        html_parts.append('</body>')
        html_parts.append('</html>')

        path = os.path.join(self.dir_report, self.rep_name)

        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(html_parts))

        print(f'File was saved to {self.dir_report}.')

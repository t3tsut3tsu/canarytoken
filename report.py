import os
from collections import defaultdict

class RepGenerate:
    def __init__(self, description, dir_report, rep_name):
        self.description = description
        self.dir_report = dir_report
        self.rep_name = rep_name

    def gen(self, data):
        grouped = defaultdict(list)
        for row in data:
            grouped[row[f'description']].append(row)

        html_parts = []

        html_parts.append('<html>')
        html_parts.append(f'<head><title>{self.description}</title></head>')
        html_parts.append('<body>')
        html_parts.append('<h1>Отчет по оценке защищенности</h1>')

        for description, rows in grouped.items():
            html_parts.append(f'<h2>{description}</h2>')
            html_parts.append('<table border="1" cellpadding="5" cellspacing="0">')
            html_parts.append(
                '<tr><th>ID</th><th>Token</th><th>Sender</th><th>Recipient</th><th>IP</th><th>Get Time</th><th>Open Time</th></tr>')

            for row in rows:
                html_parts.append(
                    '<tr>'
                    f'<td>{row["id"]}</td>'
                    f'<td>{row["token"]}</td>'
                    f'<td>{row["sender"]}</td>'
                    f'<td>{row["recipient"]}</td>'
                    f'<td>{row["ip_addr"]}</td>'
                    f'<td>{row["get_time"]}</td>'
                    f'<td>{row["open_time"]}</td>'
                    '</tr>'
                )
            html_parts.append('</table><br>')

        html_parts.append('</body>')
        html_parts.append('</html>')

        path = os.path.join(self.dir_report, self.rep_name)

        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(html_parts))

        print(f'File was saved to {self.dir_report}')

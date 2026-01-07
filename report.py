import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import defaultdict
import logging
import logger


logger.logger()

class Plots:
    def __init__(self, valid_mails, invalid_mails):
        self.valid_mails = valid_mails
        self.invalid_mails = invalid_mails

    def pie_plot(self, file_path):
        plt.figure(figsize=(3, 3), facecolor='lightgray')

        plt.rcParams['font.family'] = 'Courier New'
        plt.rcParams['font.size'] = 8

        data = [self.valid_mails, self.invalid_mails]
        labels = ['Отправлено', 'Не отправлено']
        wedges, texts, autotexts = plt.pie(data, labels=labels, autopct='%1.1f%%', shadow=True)

        for text in texts:
            text.set_fontsize(10)
            text.set_fontweight('bold')
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_fontweight('bold')

        plt.title('Доля отправленных\nи не отправленных писем', fontsize=12, fontweight='bold')

        plt.savefig(file_path, bbox_inches='tight')
        plt.close()

class RepGenerate:
    def __init__(self, descriptions, dir_report, rep_name, open_num_counts):
        self.descriptions = descriptions
        self.dir_report = dir_report
        self.rep_name = rep_name
        self.open_num_counts = open_num_counts

        self.report_dir = os.path.join(self.dir_report, str(self.rep_name).rstrip('.html'))  # папка для каждого отчета + графиков

        if not os.path.exists(self.dir_report):
            os.makedirs(self.dir_report)
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)

    def gen(self, good_data, bad_data):
        grouped = defaultdict(list)
        grouped_bad = defaultdict(list)

        for row in good_data:
            grouped[row['description']].append(row)

        for row in bad_data:
            grouped_bad[row['description']].append(row)

        html_parts = []

        html_parts.append('<html>')
        html_parts.append(f'<head><meta charset=\'UTF-8\'><link rel=\'stylesheet\' href=\'../custom/styles.css\'><title>{self.rep_name}</title></head>')

        html_parts.append('<body>')

        if len(self.descriptions) > 1:
            descriptions_string = '», «'.join(self.descriptions)
            html_parts.append(f'<h1>Сводный отчет по запускам «{descriptions_string}»</h1><br>')

        for description in self.descriptions:
            if description in grouped:
                rows = grouped[description]

                current_good_data = grouped.get(description, [])
                current_bad_data = grouped_bad.get(description, [])

                valid_recipients = len(set(row['recipient'] for row in current_good_data))
                invalid_recipients = len(set(row['recipient'] for row in current_bad_data))

                #plot_file_path = os.path.join(self.report_dir, f'pie_{description}.png')

                #plots = Plots(valid_recipients, invalid_recipients)
                #plots.pie_plot(plot_file_path)
                #abs_plot_path = os.path.abspath(plot_file_path)

                html_parts.append(f'<h1><span class="red"> » </span>Отчет по запуску «{description}»</h1>')
                html_parts.append(f'<h2>Информация о запуске:</h2>')

                sender = rows[0]['sender']
                launch_time = rows[0]['get_time']
                file_format = rows[0]['file_format']
                html_parts.append('<ul type="circle">')
                html_parts.append(f'<li>Отправитель: {sender}</li>'
                                  f'<li>Начало запуска: {launch_time}</li>'
                                  f'<li>Используемый формат шаблона: {file_format}</li>')
                html_parts.append('</ul>')

                #html_parts.append('<div class ="image-container">')
                #html_parts.append(f'<img src="{abs_plot_path}" alt="Pie Chart">')
                #html_parts.append('</div>')

                html_parts.append(f'<h2>Общее число открытий: {self.open_num_counts[description]}</h2>')
                html_parts.append(f'<h2>Список сработок:</h2>')

                html_parts.append('<table>')
                html_parts.append('<tr><th>Получатель</th><th>IP</th><th>Время отправки</th><th>Время открытия</th><th>User-Agent</th><th>Число открытий</th></tr>')
                for row in rows:
                    if row['open_time']:
                        html_parts.append(
                            '<tr>'
                            f'<td>{row["recipient"]}</td>'
                            f'<td>{row["ip_addr"]}</td>'
                            f'<td>{row["get_time"]}</td>'
                            f'<td>{row["open_time"]}</td>'
                            f'<td>{row["user_agent"]}</td>'
                            f'<td>{row["open_num"]}</td>'
                            '</tr>'
                        )
                html_parts.append('</table>')
                html_parts.append('<hr>')

        #if bad_data:
        #    html_parts.append('<h2>Вложения не были отправлены:</h2>')
        #    html_parts.append('<table>')
        #    html_parts.append('<tr><th>ID</th><th>Запуск</th><th>Получатель</th></tr>')
        #    for row in bad_data:
        #        html_parts.append(
        #            '<tr>'
        #            f'<td>{row[\'id\']}</td>'
        #            f'<td>{row[\'description\']}</td>'
        #            f'<td>{row[\'recipient\']}</td>'
        #            '</tr>'
        #        )
        #    html_parts.append('</table>')

        html_parts.append('</body>')
        html_parts.append('</html>')

        path = os.path.join(self.report_dir, self.rep_name)

        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(html_parts))

        print(f'File was saved to {self.report_dir}')
        logging.info(f'Report \'{self.rep_name}\' has been generated')

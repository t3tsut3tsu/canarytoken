import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import defaultdict
import logging
import logger


logger.logger()

class Plots:
    def __init__(self, reason_stats):
        self.reason_stats = reason_stats

    def pie_plot_errors(self, file_path):
        if not self.reason_stats:
            return False

        fig = plt.figure(figsize=(12, 5), facecolor='lightgray')
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['font.size'] = 11

        reasons = list(self.reason_stats.keys())
        counts = list(self.reason_stats.values())

        colors = plt.cm.Set3(range(len(reasons)))

        ax = fig.add_subplot(111)

        wedges, texts, autotexts = ax.pie(
            counts,
            labels=None,
            autopct=lambda pct: f'{pct:.1f}%' if pct > 3 else '',
            startangle=90,
            colors=colors,
            textprops={'fontsize': 12, 'fontweight': 'bold'},
            wedgeprops={'edgecolor': 'white', 'linewidth': 1.5}
        )

        for autotext in autotexts:
            autotext.set_color('dimgray')
            autotext.set_fontweight('bold')

        legend_labels = [f'{reason} ({count})' for reason, count in self.reason_stats.items()]

        legend = ax.legend(
            wedges,
            legend_labels,
            title="Причины ошибок",
            title_fontsize=13,
            fontsize=12,
            loc="center left",
            bbox_to_anchor=(1.02, 0.5),
            frameon=True,
            fancybox=True,
            shadow=False,
            borderpad=1,
            labelspacing=1.2
        )

        legend.get_frame().set_facecolor('white')
        legend.get_frame().set_alpha(0.9)

        fig.suptitle(
            'Причины неудачных отправок',
            fontsize=16,
            fontweight='bold',
            y=0.95,
            x=0.4,
            color='dimgray'
        )
        ax.axis('equal')
        ax.axis('off')

        plt.tight_layout(rect=[0, 0, 0.82, 0.95])

        plt.savefig(
            file_path,
            bbox_inches='tight',
            dpi=130,
            facecolor='lightgray',
            pad_inches=0.2,
            transparent=False,
        )
        plt.close()
        return True

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

    def _translate_reason(self, reason):
        translations = {
            'invalid_format or duplicate': 'Неверный формат email или дубликат',

            'connection_refused': 'Соединение отклонено',
            'timeout': 'Таймаут',
            'connection_reset_by_peer': 'Удаленный хост разорвал соединение',
            'connection_aborted_by_host': 'Хост разорвал соединение',
            'server_disconnected': 'Почтовый сервер отключился',

            'mailbox_not_found': 'Почтовый ящик не найден',
            'mailbox_full': 'Почтовый ящик переполнен',
            'mailbox_syntax_error': 'Ошибка синтаксиса адреса',

            'smtp_connect_error': 'Ошибка подключения к SMTP',
            'smtp_connect_error_xxx': 'Ошибка подключения к SMTP (код {code})',

            'smtp_error_550': 'Почтовый ящик не найден',
            'smtp_error_552': 'Почтовый ящик переполнен',
            'smtp_error_553': 'Ошибка синтаксиса адреса',
            'smtp_error_xxx': 'SMTP ошибка {code}',

            'unknown_error': 'Неизвестная ошибка',
        }

        if reason.startswith('smtp_connect_error_'):
            code = reason.replace('smtp_connect_error_', '')
            if code.isdigit():
                return f'Ошибка подключения к SMTP (код {code})'
            return translations.get('smtp_connect_error', reason)

        elif reason.startswith('smtp_error_'):
            code = reason.replace('smtp_error_', '')

            if reason in translations:
                return translations[reason]
            elif code.isdigit():
                return f'SMTP ошибка {code}'
            else:
                return translations.get('smtp_error_xxx', reason).format(code=code)

        return translations.get(reason, reason)

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

                #current_good_data = grouped.get(description, [])
                current_bad_data = grouped_bad.get(description, [])

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
                html_parts.append('<hr>')
                html_parts.append(f'<h2>Общее число срабатываний: {self.open_num_counts[description]}</h2>')
                html_parts.append(f'<h2>Список срабатываний:</h2>')

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

                if current_bad_data:
                    html_parts.append('<h2>Вложения не были отправлены:</h2>')
                    reason_stats = defaultdict(int)
                    for row in current_bad_data:
                        reason = row['reason'] if 'reason' in row.keys() else 'unknown_error'
                        reason_stats[reason] += 1

                    if reason_stats:
                        plot_file_path = os.path.join(self.report_dir, f'errors_pie_{description}.png')
                        plots = Plots(reason_stats)
                        if plots.pie_plot_errors(plot_file_path):
                            abs_plot_path = os.path.abspath(plot_file_path)

                            html_parts.append('<div class="image-container">')
                            html_parts.append(f'<img src="{abs_plot_path}" alt="Pie Chart of Errors">')
                            html_parts.append('</div>')

                    #html_parts.append('<h2>Детальный список ошибок:</h2>')
                    #html_parts.append('<table>')
                    #html_parts.append('<tr><th>ID</th><th>Запуск</th><th>Получатель</th><th>Причина</th></tr>')

                    #current_bad_data_sorted = sorted(current_bad_data,
                    #                                 key=lambda x: (x['id'] if 'id' in x.keys() else 0,
                    #                                                x['reason'] if 'reason' in x.keys() else '',
                    #                                                x['recipient'] if 'recipient' in x.keys() else ''))

                    #for row in current_bad_data_sorted:
                    #    reason = row['reason'] if 'reason' in row.keys() else 'unknown_error'
                    #    reason_translated = self._translate_reason(reason)

                    #    html_parts.append(
                    #        '<tr>'
                    #        f'<td>{row["id"]}</td>'
                    #        f'<td>{row["description"]}</td>'
                    #        f'<td>{row["recipient"]}</td>'
                    #        f'<td>{reason_translated}</td>'
                    #        '</tr>'
                    #    )
                    #html_parts.append('</table>')
                    html_parts.append('<hr>')

        html_parts.append('</body>')
        html_parts.append('</html>')

        path = os.path.join(self.report_dir, self.rep_name)

        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(html_parts))

        print(f'File was saved to {self.report_dir}')
        logging.info(f'Report \'{self.rep_name}\' has been generated')

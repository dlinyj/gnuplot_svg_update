#!/usr/bin/env python

import sys
import os
import getopt
import base64
import tempfile


def create_file_to_plot(data_for_plot):
    datafile = ''
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as tmp:
        datafile = tmp.name
        tmp.write(data_for_plot)
    return datafile


def get_remote_data():
    # Здесь мы каким-то образом получаем удалённые данные
    # Но в данном случае будут передаваться текст фиксированных данных.
    return ''';Обычный студент;Отличник;Ботаник;Проплатил
Начало семестра;0;0;0;0
Первый месяц;1;1;1;0
Второй месяц;1;2;2;0
Третий месяц;1;3;3;0
Четвёртый месяц;1;4;4;0
АААА... Уже 10 дней до экзамена;2;5;5;0
Ну ещё неделя до экзамена есть;2;6;6;0
3 дня до экзамена;3;3;5;0
1 день до экзамена;2;"1,5";5;0
Ночь перед экзаменом;5;0;5;0
Оценка на экзамене;4;5;6;5
Каникулы;1;0;5;0
Начало семестра...;0;0;5;0'''


def set_ytics_label():
    return {0: "А что?", 1: "А смысл приходить", 2: "Неуд", 3: "Удв",
            4: "Хор", 5: "Отл", 6: "Автомат"}


def plot_graph(datafile, ylabel='', title=''):
    from subprocess import Popen, PIPE, STDOUT

    # Делаем маркировку по оси Y
    ytics_label = ''
    if len(ylabel) != 0:
        ytics_label = 'set ytics ('
        for mark_ylabel in ylabel:
            ytics_label += f'"{ylabel[mark_ylabel]}" "{mark_ylabel}", '
        ytics_label = ytics_label.rstrip(' ,') + ')'

    cmd = f'''
set terminal svg enhanced mousing size 1024,768
set output "output.svg"

set encoding utf8
set datafile separator ";"
set xtics rotate by 45 right

set title "{{/:Bold {title} }}" font ",30"

set key noenhanced font ",20"
set grid
set key autotitle columnheader
{ytics_label}
set yrange [0:9]


set style fill transparent solid 0.3
plot for [i=2:5] '{datafile}' using i:xtic(1) \
    smooth mcsplines with filledcurves x1
'''

    p = Popen(['gnuplot'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    output = p.communicate(input=cmd.encode('utf-8'))[0]
    print(output.decode('utf-8'))


def update_svg(svg_filename='output.svg'):
    svg_out = list()
    JS_STR_START = '<script type="text/javascript" xlink:href="'
    JS_STR_END = '"/>'

    IMG_STR_START = "xlink:href='"
    IMG_STR_END = ".png'"

    with open(svg_filename) as f:
        svg_in = f.read().split('\n')
    start = len(JS_STR_START)
    for string in svg_in:
        if JS_STR_START in string:
            end = string.find(JS_STR_END)
            js_path = string[start:end]
            with open(js_path) as js_f:
                svg_out.append('<script type="text/javascript"><![CDATA[' +
                               js_f.read() + ']]></script>')
        elif 'grid.png' in string:
            start = string.find(IMG_STR_START) + len(IMG_STR_START)
            end = string.find(IMG_STR_END) + len(IMG_STR_END)
            img_in_base64 = '''
iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAADFBMVEX///8AAAAAAAAAAAD4jAJN
AAAAA3RSTlMA7Psi0lOqAAAAHElEQVR4AWPABpjgCLsAExMzAjEOMS2MCIQFAABtJADJXH3sOwAA
AABJRU5ErkJggg=='''
            svg_out.append(string[0:start] +
                           'data:image/png;charset=utf-8;base64, ' +
                           img_in_base64 + "'" + string[end:])
        else:
            svg_out.append(string)
    with open('output.svg', 'w') as f:
        f.write('\n'.join(svg_out))


def main():
    data_for_plot = get_remote_data()
    ylabel = set_ytics_label()
    datafile = create_file_to_plot(data_for_plot)
    title = 'Уровень знаний в течение семестра'
    plot_graph(datafile, ylabel, title)
    os.unlink(datafile)
    update_svg()


if __name__ == "__main__":
    main()

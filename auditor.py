#!/usr/bin/python
# coding=utf-8

__author__ = 'Alexandr Prokhorov'

import shelve
import time
import os
import argparse
from auditor_cfg import *
from functions import SendMail
from functions import WriteLog
from updater import Updater

class source:
    def __init__(self, source_name, offset = 0):
        self.name = self.prepareName(source_name, offset)
        if self.name:
            self.exist = True
            self.size = os.stat(self.name).st_size
            self.time = os.stat(self.name).st_mtime
        else:
            self.name = source_name
            self.exist = False
            self.size = False
            self.time = False

    def getSizeStr(self, size = 0):
        """Функция конвертирует целое значение в байтах, в строковое значение в кило, мега и гига байтах
Если передать функции числовое значение, функция вернёт разницу между текущим объёмом файла и переданным числом"""
        if not self.size:
            return False
        elif abs(self.size - size) > 2**30:
            return ('%.2f' % (float(self.size - size)/2**30)) + ' Gb'
        elif abs(self.size - size) > 2**20:
            return ('%.2f' % (float(self.size - size)/2**20)) + ' Mb'
        elif abs(self.size - size) > 2**10:
            return ('%.2f' % (float(self.size - size)/2**10)) + ' Kb'
        elif abs(self.size - size) > 0:
            return ('%.2f' % (float(self.size - size))) + ' byte'
        else:
            return '-'

    def getTimeStr(self):
        """Функция конвертирует абсолютную дату в формат ЧЧ.ММ.ГГГГ ЧЧ:ММ"""
        import time
        if not self.time:
            return False
        else:
            return time.strftime('%d.%m.%Y %H:%M:%S', time.localtime(self.time))

    def __str__(self):
        return 'Source - "%s"\nSource size = "%s"\nModify Time = "%s"' % \
              (self.name, self.getSizeStr(), self.getTimeStr())

    def prepareName(self, source_name, offset = 0):
        """prepareName(str, int) -> String - source name.

Returns converted source name if variables "%day%" or "%date%" included +- offset in day count (optional).
Converts the RU or ENG short name of the day of the week if "%day%" and local date format without time if "%date" """
        import os
        if '%day%' in source_name:
            day = (time.localtime().tm_wday + 1 + offset)
            if os.access(source_name.replace('%day%', self.getDayRU(day)), os.F_OK):
                return source_name.replace('%day%', self.getDayRU(day))
            elif os.access(source_name.replace('%day%', self.getDayEN(day)), os.F_OK):
                return source_name.replace('%day%', self.getDayEN(day))
            else:
                return False
        else:
            if os.access(source_name, os.F_OK):
                return source_name
            else:
                return False

    def getDayRU(self, num = 'None'):
        """getDayRU(int) -> Name of day as string

Returns the Russian name of the day of the week, depending on the protocol number (optional).
If the number of the day of the week is not passed, returns the current day of the week."""
        days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
        if num != 'None':
            return days[num - 1].decode('utf-8')
        return days[time.localtime().tm_wday]

    def getDayEN(self, num = 'None'):
        """getDayEN(int) -> Name of day as string

Returns the English name of the day of the week, depending on the protocol number (optional).
If the number of the day of the week is not passed, returns the current day of the week."""
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        if num != 'None':
            return days[num - 1]
        return days[time.localtime().tm_wday]

class report:
    """report(path) -> html file.

Creates HTML file and is waiting lists to append them to a report table."""
    def __init__(self, path):
        self.__r = open(path, "w")
        self.__r.write('<html>\n<head>\n')
        self.__r.write('\t<meta http-equiv="Content-Type" content="text/html; charset=utf-8">\n')
        self.__r.write('</head>\n<body>\n<table width = "100%">\n')
        self.__closed = False

    def __del__(self):
        self.close()

    def close(self):
        """close() -> None or (perhaps) an integer.

Close the file."""
        if not self.__closed:
            self.__r.write('</table>\n</body>\n</html>')
            self.__r.close()
            self.__closed = True

    def append(self, lst, color = 'Default'):
        """append([list], color = 'HTML code') -> None.

Append a row in the report table, turning it the color passed as the second parameter (optional).
The color should be given in the form of HTML code (such as "FFFFFF" = white color)."""
        result = '\t<tr'
        if color != 'Default':
            result += ' bgcolor = "' + color + '"'
        result += '>\n'
        for element in lst:
            try:
                result += '\t\t<td>' + str(element) + '</td>\n'
            except:
                result += '\t\t<td>' + str(element.encode('utf-8')) + '</td>\n'
        result += '\t</tr>\n'
        self.__r.write(result)

def getPrevDayNum():
    """getYesterdayNum() -> Integer

Функция возвращает номер вчерашнего дня"""
    if (time.localtime().tm_wday + 1) == 1:
        return 7
    else:
        return time.localtime().tm_wday

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--email", default=False, help="Send Email to admin. Default False.")
args = parser.parse_args()

# Проверяем наличие обновлений скрипта и, при необходимости обновляем его
u = Updater(__file__)
WriteLog(u.CreateUpd(), log)
u.ExecUpd()

# Создаём словарь со списком ресурсов для аудита
f = open('auditor.csv', 'r')
sources = {}
for element in f:
    if ('#' not in str(element)) and (element != '\n'):
        lst = list((element.replace('\n', '')).split(';'))
        sources[lst[0]] = {'policy':lst[1].replace(' ', ''), 'regular':lst[2].replace(' ', '')}
f.close()

# Создаём файл отчёта и добавляем в него "шапку"
r = report('auditor.html')
r.append(['<b>Источник</b>', '<b>Размер</b>', '<b>Дата модификации</b>', '<b>Прирост</b>','<b>Примечания</b>'], 'CCCCCC')

# Открываем файл с результатами прошлого аудита
cash = shelve.open('auditor.dat')

# Удаляем из него ресурсы, которые отсутствуют в списке ресурсов
for element in sorted(cash):
    if element not in sources:
        r.append([str(element), '', '', '', 'Удалён из списка ресурсов.'], 'FFFF66')
        del(cash[element])

for element in sorted(sources):
    # Если используется политика Default...
    if sources[element]['policy'] == 'default':
        s = source(element.decode('utf-8'))
    # Если используется политика Container
    elif sources[element]['policy'] == 'container':
        s = source(element.decode('utf-8'), -1)
    # Если задана иная политика...
    else:
        continue

    # Если в параметре "регулярность" в списке ресурсов не задано создание бэкапа в прошедший день...
    if str(getPrevDayNum()) not in sources[element]['regular']:
        continue

    # Если файл существует...
    if s.exist:
        result = [s.name, s.getSizeStr(), s.getTimeStr()]
        # Если файл отсутствует в кэше, добавляем информацию о нём...
        if element not in cash:
            cash[element] = {'oldsize': s.size, 'size':s.size, 'result':'neutral', 'mtime':s.time, \
                             'atime':int(time.time()), 'note':'Информация о файле добавлена в кэш.'}
            r.append(result + ['', cash[element]['note']])
            continue
        # Если проверка сегодня уже проводилась успешно и файл не изменился...
        elif (time.localtime(cash[element]['atime']).tm_wday == time.localtime().tm_wday) \
            and ((cash[element]['result'] == 'ok') or (cash[element]['result'] == 'neutral')) \
            and s.time == cash[element]['mtime']:
            cash[element] = {'oldsize': cash[element]['oldsize'], 'size':s.size,'result':'ok', \
                             'mtime':s.time, 'atime':int(time.time()), 'note':'OK'}
            r.append(result + [s.getSizeStr(cash[element]['oldsize']), cash[element]['note']], '99FF99')
            continue
        # Если дата модификации файла равна дате модификации из кэша...
        elif s.time == cash[element]['mtime']:
            cash[element] = {'oldsize': cash[element]['size'], 'size':s.size, 'result':'bad', \
                             'mtime':s.time, 'atime':cash[element]['atime'], \
                             'note':'Файл не был изменён с прошлой проверки.'}
            r.append(result + ['', cash[element]['note']], 'FFCCCC')
            continue
        # Если размер контейнера изменился...
        elif (sources[element]['policy'] == 'container') and (s.size != cash[element]['size']) \
            and (cash[element]['size'] != 0):
            cash[element] = {'oldsize': cash[element]['size'], 'size':s.size, 'result':'bad', 'mtime':s.time, \
                             'atime':int(time.time()), 'note':'Объём контейнера изменился.'}
            r.append(result + [s.getSizeStr(int(cash[element]['oldsize'])), cash[element]['note']], 'FFCCCC')
            continue
        # Если размер файла уменьшился более чем на 50 процентов...
        elif s.size < (cash[element]['size'] - cash[element]['size']/2):
            cash[element] = {'oldsize': cash[element]['size'], 'size':s.size, 'result':'bad', 'mtime':s.time, \
                             'atime':int(time.time()), 'note':'Файл уменьшился более чем на 50 процентов.'}
            r.append(result + [s.getSizeStr(int(cash[element]['oldsize'])), cash[element]['note']], 'FFCCCC')
            continue
        # Иначе, всё хорошо...
        else:
            cash[element] = {'oldsize': cash[element]['size'], 'size':s.size,'result':'ok', \
                             'mtime':s.time, 'atime':int(time.time()), 'note':'OK'}
            r.append(result + [s.getSizeStr(cash[element]['oldsize']), cash[element]['note']], '99FF99')
            continue
    else:
        cash[element] = {'oldsize': '', 'size':0, 'result':'bad', 'mtime':'', \
                         'atime':int(time.time()), 'note':'Файл не доступен.'}
        r.append([s.name, '', '', '', cash[element]['note']], 'FFCCCC')

r.close()

# Отправка отчёта по электронной почте
if args.email:
    body = open('auditor.html', 'r')
    WriteLog(SendMail(server, port, msg_from, msg_to, msg_subj, body), log)
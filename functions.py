# coding=utf-8

def WriteLog(LogString, LogFile = '', *args):
    """
    Функция записи лог-файла в формате Дата;Время;Событие
    первый параметр - путь и имя лог-файла
    второй параметр - событие(строка) для записи в лог-файл
    третий параметр - имя модуля из которого происходит вызов функции (необязательный)
    если в качестве первого параметра передать пустую строку - '', то запись о событии будет выведено на экран
    без указания модуля, из которого произошёл вызов функции
    """
    from datetime import datetime

    sLog = datetime.now().strftime('%Y-%m-%d' + '\t' + '%H:%M:%S')

    if LogFile == '':
        sLog += '\t' + LogString
        print sLog.decode('utf-8').encode('cp866')
        return '000000'
    sLog += '\t' + LogString
    if args:
        for arg in args:
            sLog  += ' | ' + str(arg)
    sLog += '\n'
    try:
        fLog = open(LogFile, 'a')
        fLog.writelines(sLog)
        fLog.close()
        return '000000'
    except:
        return '000001'

def SendMail(server, port, msg_from, msg_to, msg_subj, msg_body):
    """
    Функция отправки сообщения по электронной почте
    На входе должна обязательно получить  все параметры:
    имя сервера, порт SMTP, от кого, кому, тема сообщения, тело сообщения
    """
    import smtplib
    from email.MIMEText import MIMEText

    if type(msg_body) == list:
        new_msg_body = ''
        for s in msg_body:
            if '\n' not in s: new_msg_body += s + '\n'
            else: new_msg_body += s
        msg_body = new_msg_body

    if type(msg_body) == file:
        new_msg_body = ''
        for s in msg_body:
            new_msg_body += s
        msg_body = new_msg_body

    if type(msg_body) == str:
        if '<html>' in msg_body[0:6]:
            msg_type = 'html'
        else:
            msg_type = ''
        msg = MIMEText(msg_body, msg_type, 'utf-8')
        msg['Subject'] = msg_subj
        msg['From'] = msg_from
        msg['To'] = str(msg_to)

        try:
            s = smtplib.SMTP(server, port)
            s.sendmail(msg_from, msg_to, msg.as_string())
            s.quit()
            return '000003'
        except:
            return '000004'
    else:
        return '000007'

def ErrorHandling(error_handle):
    """ErrorHandling(str) -> Error description.

Функция возвращает определение ошибки по коду"""
    error_list = { \
        '000000': 'Выполнено без ошибок', \
        '000001': 'Не возможно открыть файл для записи', \
        '000002': 'Не возможно открыть файл для чтения', \
        '000003': 'Отправка электронной почты выполнена без ошибок', \
        '000004': 'Не возможно отправить сообщение по электронной почте', \
        '000005': 'Отправка СМС выполнена без ошибок', \
        '000006': 'Не возможно отправить СМС', \
        '000007': 'Тело письма не является строкой или списком', \
        '000008': '000008', \
        '000009': '000009', \
        '000010': '000010'}
    if error_handle in error_list:
        return error_list[error_handle]
    return 'Неопределённая ошибка'

def getDayRU(num = 'None'):
    """getDayRU(int) -> Name of day as string

Returns the Russian name of the day of the week, depending on the protocol number (optional).
If the number of the day of the week is not passed, returns the current day of the week."""
    import time
    days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    if num != 'None':
        return days[num - 1]
    return days[time.localtime().tm_wday]

def getDayENG(num = 'None'):
    """getDayRU(int) -> Name of day as string

Returns the English name of the day of the week, depending on the protocol number (optional).
If the number of the day of the week is not passed, returns the current day of the week."""
    import time
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    if num != 'None':
        return days[num - 1]
    return days[time.localtime().tm_wday]

def getDifPercent(a, b):
    """getDifPercent(a, b) -> Percent

Returns the difference between the first and second percentage of the number in the first number.
That is, what per cent more than the second number of the first."""
    if b > a:
        return (float(b) - float(a)) / float(a) * 100
    return 0.0 - (float(a) - float(b)) / float(a) * 100
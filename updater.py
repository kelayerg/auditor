# -*- coding: utf-8 -*-
__author__ = 'alexandr.prokhorov'

import os
import subprocess

class Updater():

    repo = '../repo/auditor/'  # Адрес репозитария по умолчанию

    def __init__(self, module, alt_repo = ''):
        self.DelOldUpdater()
        self.mod = str(os.path.basename(module))[:os.path.basename(module).rfind('.')]
        self.path = str(os.path.abspath(module)).replace('\\','/')[:os.path.abspath(module).rfind('\\')+1]
        if alt_repo:
            self.repo = alt_repo

    def GetSourceList(self):
        """GetSourceList() -> SourceList[]

Функция возвращает список файлов приложения в репозитории, если он существует
или False если список не удалось получить.
"""
        try:
            self.__sources = open(self.repo + self.mod + '.lst', 'r')
            self.SourceList = []
            for s in self.__sources:
                s = s.replace('\n', '')
                self.SourceList.append(s)
            self.__sources.close()
            return self.SourceList
        except:
            return False

    def DelOldUpdater(self):
        """DelOldUpdater -> Boolean

Функция удаляет старый скрипт обновления upd.py если он присутствует в папке программы
Если скрипт удалён, возвращает True
Если скрипта не существовало, или он не удалён, возвращает False
"""
        if os.access('upd.py', os.F_OK):
            try:
                os.remove('upd.py')
                return True
            except:
                pass
        return False

    def GetStat(self, path):
        """GetStat(path) -> lst[time, size]

Функция возвращает список содержащий дату модификаци и объём файла по переданному пути
или False если файла по переданному пути не существует
"""
        if os.access(path, os.F_OK):
            return [os.stat(path).st_mtime, os.stat(path).st_size]
        return False

    def CheckUpdate(self, module_name):
        """CheckUpdate(module_name) -> Boolean

Функция возвращает True, если для переданного наименования модуля в репозитарии существуют обновления
и False если обновлений не обнаружено.
Наличие обновлений определяется суммой следующих признаков:
    - Файл в репозитории имеет более позднюю дату, относительно локального файла;
    - Объём файла в репозитории не равен объёму локального файла
"""
        local = self.GetStat(module_name)
        remote = self.GetStat(self.repo + module_name)
        if (local and remote) and (local[0] < remote[0]) and (local[1] != remote[1]):
            return True
        elif not local and remote:
            return True
        return False

    def GetUpdateList(self):
        """GetUpdateList() -> UpdateList[]

Функция возвращает список имён файлов для обноления, если обновления для них обнаружены
или False если обновлений не найдено.
"""
        self.UpdateList = []
        sl = self.GetSourceList()
        if sl:
            for element in sl:
                if self.CheckUpdate(element):
                    self.UpdateList.append(element)
            if len(self.UpdateList):
                return self.UpdateList
        return False

    def CreateUpd(self, restart = True):
        """CreateUpd() -> string

Функция создаёт файл обновления upd.py если обновления для вызывающего приложения существуют.
Возвращает строку с результатом работы:
    - Update script "upd.py" created - Скрипт создан
    - Can't create "upd.py" - Нет возможности создать скрипт
    - No updates found - Обновления не найдены
"""
        UpdateList = self.GetUpdateList()
        if UpdateList:
            upd_str = '''# -*- coding: utf-8 -*-
import shutil
import os
import subprocess
from time import sleep

sleep(3)
'''
            for element in UpdateList:
                upd_str += "shutil.copyfile('%s', '%s')\n" % (self.repo + element, self.path + element)
            if restart:
                upd_str += "subprocess.Popen('" + self.mod + ".py', shell='True', stdout=subprocess.PIPE)\n"
            else:
                upd_str += 'os.remove("upd.py")'
            try:
                upd = open('upd.py', 'w')
                upd.write(upd_str)
                return 'Update script "upd.py" created. Found update the following modules: "%s"' % UpdateList
            except:
                return 'Can\'t create "upd.py".'
        return 'No updates found.'

    def ExecUpd(self):
        """ExecUpd -> None

Функция запускает скрипт "upd.py" и завершает работу текущего модуля
"""

        if os.access('upd.py', os.F_OK):
            subprocess.Popen('upd.py', shell='True', stdout=subprocess.PIPE)
            exit()
        return False

    def Update(self, restart = True):
        """Update() -> None

Функция создаёт и запускает скрипт "upd.py", после чего завершает работу текущего модуля
"""
        self.CreateUpd(restart)
        self.ExecUpd()
﻿auditor
======

Скрипт для аудита выполнения бэкапов

Проверяет наличие и изменения объёма и даты модификации указанных в списке ресурсов файлов.
В результате работы формирует разноцветный отчёт в формате HTML и отправляет его на почту администратору.
======
Использование:

auditor.py - выполняется аудит ресурсов, указанных в auditor.csv, и создаётся отчёт auditor.html.

Ключи:

-e True - созданный отчёт отправляется на электронную почту администратора, указанную в файле auditor_cfg.py

-s True - аудит не производится, но создаётся обзорный отчёт из кэша, включающий в себя результаты последнего аудита каждого из ресурсов.
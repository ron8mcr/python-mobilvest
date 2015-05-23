#!/usr/bin/env python
# coding: UTF-8

import requests
from hashlib import md5


class ServerResponsedWithError(Exception):
    pass


class MobilVestApi(object):
    ERRORS = {
        1: 'Не указана подпись',
        2: 'Не указан логин',
        3: 'Не указан текст',
        4: 'Не указан телефон',
        5: 'Не указан отправитель',
        6: 'Не корректная подпись',
        7: 'Не корректный логин',
        8: 'Не корректное имя отправителя',
        9: 'Не зарегистрированное имя отправителя',
        10: 'Не одобренное имя отправителя',
        11: 'В тексте содержатся запрещенные слова',
        12: 'Ошибка отправки СМС',
        13: 'Номер находится в стоп-листе. Отправка на этот номер запрещена',
        14: 'В запросе более 50 номеров',
        15: 'Не указана база',
        16: 'Не корректный номер',
        17: 'Не указаны ID СМС',
        18: 'Не получен статус',
        19: 'Пустой ответ',
        20: 'Номер уже существует',
        21: 'Отсутствует название',
        22: 'Шаблон уже существует',
        23: 'Не указан месяц (Формат: YYYY-MM)',
        24: 'Не указана временная метка',
        25: 'Ошибка доступа к базе',
        26: 'База не содержит номеров',
        27: 'Нет валидных номеров',
        28: 'Не указана начальная дата',
        29: 'Не указана конечная дата',
        30: 'Не указана дата (Формат: YYYY-MM-DD)'
    }
    BASE_URL = 'http://online.mobilvest.ru/get/'

    def __init__(self, login, api_key):
        self.login = login
        self.api_key = api_key

    def _list_to_str(self, lst):
        """ Преобразование списка к строке, где значения разделены запятой
        Такое требование API mobilvest к спискам
        """
        return ','.join(map(str, lst))

    def _get_server_timestamp(self):
        r = requests.get('http://online.mobilvest.ru/get/timestamp.php')
        return int(r.text)

    def _prepare_params(self, params):
        """
        Подготовка данных для запроса: вставка signature, timestamp, login
        params - словарь с параметрами запроса, не касающимися безопасности,
        логина, подписи и т. д.
        Документация:
        Подпись (параметр signature) - md5 хэш, который формируется
        следующим образом:
        Все параметры из запроса нужно отсортировать в алфавитном порядке
        в строку, в конец строки добавить API ключ. При этом
        последовательность параметров непосредственно в
        запросе не имеет значения.
        """
        result = params.copy()
        result['login'] = self.login
        result['timestamp'] = self._get_server_timestamp()
        result['return'] = 'json'
        params_as_string = ''.join(str(result[k]) for k in sorted(result))
        result['signature'] = md5(params_as_string + self.api_key).hexdigest()
        return result

    def _call_api(self, url, params):
        """Вызов одной из API-функций
        url - адрес php страницы
        params - параметры, не относящиеся к безопасности
                                            (login, timestamp, signature)
        возвращает ответ сервера в JSON
        """
        params = self._prepare_params(params)
        response = requests.get(self.BASE_URL + url, params=params).json()
        if not response:
            return None
        if 'error' in response:
            # почему-то пустой ответ у mobilvest - ошибка
            if response['error'] == 19:
                return None
            msg = "{}".format(self.ERRORS[response['error']])
            raise ServerResponsedWithError(msg)
        return response

    def get_balance(self):
        """ Запрос баланса
        Пример ответа:
        {"money" : "69573.1","currency" : "RUR"}
        """
        params = {}
        url = "balance.php"
        return self._call_api(url, params)

    def get_base(self):
        """Запрос списка баз
        Пример ответа:
        {
            "125452": {
                "name": "Valuable clients",
                "time_birth": "12:00:00",
                "day_before": "0",
                "local_time": "1",
                "birth_sender": "",
                "birth_text": "",
                "on_birth": "0",
                "count": "2255",
                "pages": "23"
            },
            "125453": {
                "name": "Partners",
                "time_birth": "12:00:00",
                "day_before": "0",
                "local_time": "1",
                "birth_sender": "",
                "birth_text": "",
                "on_birth": "0",
                "count": "2266",
                "pages": "23"
            },
        }
        """
        params = {}
        url = "base.php"
        return self._call_api(url, params)

    def get_senders(self):
        """Запрос списка отправителей
        Пример ответа:
        {"smstest":"completed","smstest2":"completed"}
        """
        params = {}
        url = "senders.php"
        return self._call_api(url, params)

    def get_phone(self, base, page):
        """ Запрос номеров из базы
        base - ID базы
        page - номер страницы
        пример ответа:
        {
            "79687931116": {
                "name": "",
                "last_name": "",
                "middle_name": "",
                "date_birth": "0000-00-00",
                "male": "",
                "note1": "",
                "note2": "",
                "region": "",
                "operator": ""
            },
            "79874617237": {
                "name": "",
                "last_name": "",
                "middle_name": "",
                "date_birth": "0000-00-00",
                "male": "",
                "note1": "",
                "note2": "",
                "region": "",
                "operator": ""
            }
        }
        """
        url = "phone.php"
        params = {'base': base, 'page': page}
        return self._call_api(url, params)

    def get_status(self, state):
        """ Запрос статусов
        state - ID статуса
        пример ответа:
        {
            "4091297100348873330001" : "not_deliver",
            "4091297100348880230003" : "not_deliver"
        }
        """
        url = "status.php"
        if isinstance(state, list):
            params = {'state': self._list_to_str(state)}
        else:
            params = {'state': state}
        return self._call_api(url, params)

    def send_sms(self, phone, text, sender):
        """ Отправка СМС
        phone - Один номер, или список номеров (не более 50 номеров)
        text - Текст СМС сообщения
        sender - Имя отправителя (одно из одобренных на вашем аккаунте)
        пример ответа:
        {
            "79029134225": {
                "error": "0",
                "id_sms": "4092112510348380960001",
                "cost": "0.5",
                "count_sms": "1"
            }
        }
        """
        url = "send.php"
        params = {'sender': sender, 'text': text}
        if isinstance(phone, list):
            params['phone'] = self._list_to_str(phone)
        else:
            params['phone'] = phone
        return self._call_api(url, params)

    def find_on_stop(self, phone):
        """ Поиск номера в стоп-листе
        phone - Искомый номер
        пример ответа:
        {"time_in" : "2014-08-29 11:07:43","description" : "descr"}
        """
        url = "find_on_stop.php"
        params = {'phone': phone}
        return self._call_api(url, params)

    def add_to_stop(self, phone):
        """ Добавление номера в стоп-лист
        phone - Номер который нужно добавить в стоп-лист
        пример ответа:
        {"id" : "4419373"}
        """
        url = "add2stop.php"
        params = {'phone': phone}
        return self._call_api(url, params)

    def get_template(self):
        """ Запрос списка шаблонов
        Пример ответа:
        {
            "test": "{"
            template ":"
            text ", "
            up_time ":"
            2014 - 08 - 28 15: 22: 25 "}",
            "test22": "{"
            template ":"
            testtt 1321321231321 ", "
            up_time ":"
            2014 - 08 - 28 15: 39: 07 "}"
        }
        """
        params = {}
        url = "template.php"
        return self._call_api(url, params)

    def add_template(self, name, text):
        """ Запрос списка шаблонов
        name - Название шаблона
        text - Текст шаблона
        Пример ответа:
        {"id" : "4419373"}
        """
        params = {'name': name, 'text': text}
        url = "add_template.php"
        return self._call_api(url, params)

    def stat_by_month(self, month):
        """ Общая статистика за месяц по дням
        month - datetime-объект, с установленными месяцем и годом
        Пример ответа:
        {
            "2014-08-01": {
                "deliver": {
                    "cost": "0.500",
                    "parts": "1"
                },
            "2014-08-06": {
                "deliver": {
                    "cost": "0.600",
                    "parts": "1"
                },
                "not_deliver": {
                    "cost": "0.600",
                    "parts": "1"
                }
        }
        """
        params = {'month': month.strftime("%Y-%m")}
        url = "stat_by_month.php"
        return self._call_api(url, params)

    def get_operator(self, phone):
        """ Запрос оператора по номеру
        phone - Номер абонента
        Пример ответа:
        {"operator" : "AT&T"}
        """
        params = {'phone': phone}
        url = "operator.php"
        return self._call_api(url, params)

    def get_incoming(self, date):
        """ Запрос входящих СМС
        date - datetime-объект
        Пример ответа:
        {{"5597" : {"date":"2014-10-27 05:47:24", "sender":"79029734720",
                    "prefix":"51632", "text":"51632 TEST"}}}
        """
        params = {'date': date.strftime("%Y-%m-%d")}
        url = "incoming.php"
        return self._call_api(url, params)

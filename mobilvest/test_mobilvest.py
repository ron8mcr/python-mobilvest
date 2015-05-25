#!/usr/bin/env python
# coding: UTF-8
import unittest
import responses
import mobilvest
import urlparse
import datetime
from hashlib import md5


class TestsMobilVest(unittest.TestCase):

    def setUp(self):
        responses.add(responses.GET,
                      'http://online.mobilvest.ru/get/timestamp.php',
                      body='1432359515')

        self.valid_api_key = '123'
        self.mapi = mobilvest.MobilVestApi('user', self.valid_api_key)

    @responses.activate
    def test_request_params(self):
        def check_request(request):
            params = urlparse.parse_qs(urlparse.urlparse(
                request.path_url).query)
            params = {k: params[k][0] for k in params}
            self.assertIn('login', params,
                          "Parameter 'login' wasn't passed")
            self.assertIn('timestamp', params,
                          "Parameter 'timestamp' wasn't passed")
            self.assertIn('signature', params,
                          "Parameter 'signature' wasn't passed")

            recieved_signature = params.pop('signature')
            params_as_string = ''.join(str(params[k]) for k in sorted(params))
            valid_signature = md5(
                params_as_string + self.valid_api_key).hexdigest()
            self.assertEqual(recieved_signature, valid_signature)
            return (200, {}, {})

        responses.add_callback(
            responses.GET, 'http://online.mobilvest.ru/get/balance.php',
            callback=check_request,
            content_type='application/json',
        )
        self.mapi.get_balance()

    @responses.activate
    def test_rise_exception(self):
        responses.add(responses.GET,
                      'http://online.mobilvest.ru/get/balance.php',
                      body='{"error": 7}')
        self.assertRaises(mobilvest.ServerResponsedWithError,
                          self.mapi.get_balance)

    @responses.activate
    def test_empty_response(self):
        """ Если ответ пустой, сервер возвращает код ошибки 19.
        Ожидается, что в таком случае просто вернется None,
        а исключение не будет брошено
        """
        responses.add(responses.GET,
                      'http://online.mobilvest.ru/get/balance.php',
                      body='{"error": 19}')
        balance = self.mapi.get_balance()
        self.assertIsNone(balance)

    @responses.activate
    def test_get_balance(self):
        responses.add(responses.GET,
                      'http://online.mobilvest.ru/get/balance.php',
                      body='{"money" : "69573.1","currency" : "RUR"}')

        balance_json = self.mapi.get_balance()
        self.assertIn('money', balance_json)

    @responses.activate
    def test_get_base(self):
        responses.add(responses.GET,
                      'http://online.mobilvest.ru/get/base.php',
                      body='''{
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
                                  }
                              }''')

        base_json = self.mapi.get_base()
        for base in base_json.values():
            self.assertIn('name', base)
            self.assertIn('count', base)

    @responses.activate
    def test_get_senders(self):
        responses.add(responses.GET,
                      'http://online.mobilvest.ru/get/senders.php',
                      body='{"smstest":"completed","smstest2":"completed"}')

        senders = self.mapi.get_senders()
        self.assertIsNotNone(senders)

    @responses.activate
    def test_get_phone(self):
        responses.add(responses.GET,
                      'http://online.mobilvest.ru/get/phone.php',
                      body='{"error": 19}')

        base_id = "125452"
        page = 1
        phones_json = self.mapi.get_phone(base_id, page)
        self.assertIsNone(phones_json)

    @responses.activate
    def test_get_status(self):
        responses.add(responses.GET,
                      'http://online.mobilvest.ru/get/status.php',
                      body='''
                            {
                                "4091297100348873330001" : "not_deliver"
                            }
                            ''')

        sms_id = "4091297100348873330001"
        statuses_json = self.mapi.get_status(sms_id)
        self.assertIn(sms_id, statuses_json)

    @responses.activate
    def test_get_multiple_statuses(self):
        responses.add(responses.GET,
                      'http://online.mobilvest.ru/get/status.php',
                      body='''
                            {
                                "4091297100348873330001" : "not_deliver",
                                "4091297100348880230003" : "not_deliver"
                            }
                            ''')

        sms_ids = ["4091297100348873330001", "4091297100348880230003"]
        statuses_json = self.mapi.get_status(sms_ids)
        for i in sms_ids:
            self.assertIn(i, statuses_json)

    @responses.activate
    def test_send_sms(self):
        responses.add(responses.GET,
                      'http://online.mobilvest.ru/get/send.php',
                      body='''
                        {
                            "79029134225": {
                                "error": "0",
                                "id_sms": "4092112510348380960001",
                                "cost": "0.5",
                                "count_sms": "1"
                            }
                        }''')

        phone = "79029134225"
        text = "Hello world!"
        sender = "web.web"
        result_json = self.mapi.send_sms(phone, text, sender)
        self.assertIn(phone, result_json)
        self.assertIn('id_sms', result_json[phone])

    @responses.activate
    def test_send_multiple_sms(self):
        responses.add(responses.GET,
                      'http://online.mobilvest.ru/get/send.php',
                      body='''
                        {
                            "79029134225": {
                                "error": "0",
                                "id_sms": "4092112510348380960001",
                                "cost": "0.5",
                                "count_sms": "1"
                            },
                            "79029134226": {
                                "error": "0",
                                "id_sms": "4092112510348380970001",
                                "cost": "0.5",
                                "count_sms": "1"
                            }
                        }''')

        phones = ["79029134225", "79029134226"]
        text = "Hello world!"
        sender = "web.web"
        result_json = self.mapi.send_sms(phones, text, sender)
        for p in phones:
            self.assertIn(p, result_json)

    @responses.activate
    def test_find_on_stop(self):
        responses.add(responses.GET,
                      'http://online.mobilvest.ru/get/find_on_stop.php',
                      body='{"error": 19}')

        # запрошенного номера нет в стоп-листе
        on_stop_json = self.mapi.find_on_stop('79324354123')
        self.assertIsNone(on_stop_json)

    @responses.activate
    def test_add_to_stop(self):
        responses.add(responses.GET,
                      'http://online.mobilvest.ru/get/add2stop.php',
                      body='{"id" : "4419373"}')

        response = self.mapi.add_to_stop('79324354123')
        self.assertIn('id', response)

    @responses.activate
    def test_get_template(self):
        responses.add(responses.GET,
                      'http://online.mobilvest.ru/get/template.php',
                      body="""{
                                "test": {
                                    "template": "text",
                                    "up_time": "2014-08-28 15:22:25"
                                }
                            }""")

        templates = self.mapi.get_template()
        for i in templates.values():
            self.assertIn('template', i)

    @responses.activate
    def test_add_template(self):
        responses.add(responses.GET,
                      'http://online.mobilvest.ru/get/add_template.php',
                      body='{"id" : "4419373"}')

        name = 'template_1'
        text = "Hello, World!"
        response = self.mapi.add_template(name, text)
        self.assertIn('id', response)

    @responses.activate
    def test_stat_by_month(self):
        responses.add(responses.GET,
                      'http://online.mobilvest.ru/get/stat_by_month.php',
                      body='{"error": 19}')

        # пустая статистика за текущий месяц
        now = datetime.datetime.now()
        response = self.mapi.stat_by_month(now)
        self.assertIsNone(response)

    @responses.activate
    def test_get_operator(self):
        responses.add(responses.GET,
                      'http://online.mobilvest.ru/get/operator.php',
                      body='{"operator" : "AT&T"}')

        phone = '7821345312'
        response = self.mapi.get_operator(phone)
        self.assertIn('operator', response)

    @responses.activate
    def test_get_incoming(self):
        responses.add(responses.GET,
                      'http://online.mobilvest.ru/get/incoming.php',
                      body='''
                            {
                                "5597": {
                                    "date": "2014-10-27 05:47:24",
                                    "sender": "79022754620",
                                    "prefix": "51632",
                                    "text": "51632 TEST"
                                }
                            }
                        ''')

        now = datetime.datetime.now()
        incomings = self.mapi.get_incoming(now)
        for i in incomings.values():
            self.assertIn('sender', i)
            self.assertIn('text', i)

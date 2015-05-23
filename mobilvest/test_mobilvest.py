#!/usr/bin/env python
# coding: UTF-8
import unittest
import responses
import mobilvest
import urlparse
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
    def test_get_balance(self):
        responses.add(responses.GET,
                      'http://online.mobilvest.ru/get/balance.php',
                      body='{"money" : "69573.1","currency" : "RUR"}')

        balance_json = self.mapi.get_balance()
        self.assertIn('money', balance_json)

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


python-mobilvest
===============
[![Code Health](https://landscape.io/github/ron8mcr/python-mobilvest/master/landscape.svg?style=flat)](https://landscape.io/github/ron8mcr/python-mobilvest/master)
[![Build Status](https://travis-ci.org/ron8mcr/python-mobilvest.svg?branch=master)](https://travis-ci.org/ron8mcr/python-mobilvest)
[![Coverage Status](https://coveralls.io/repos/ron8mcr/python-mobilvest/badge.svg?branch=master)](https://coveralls.io/r/ron8mcr/python-mobilvest?branch=master)

https://github.com/ron8mcr/python-mobilvest

What's that
-----------

*python-mobilvest is a application for working with API of [mobilvest.ru](http://mobilvest.ru) - service for sending SMS 

API documentation is availbe at [http://online.mobilvest.ru/api/](http://online.mobilvest.ru/api/) (need authorization)

Dependence
-----------

- `requests` # for http communication
- `responses` # for tests

Getting started
---------------
* Install python-mobilvest:

``pip install -e git+https://github.com/ron8mcr/python-mobilvest
``

Examples
--------
```python
import mobilvest
from time import sleep

# Create an instance of MobilVestAPI
# using login and api_key
# (you can find it out at http://online.mobilvest.ru/api/)
mapi = mobilvest.MobilVestApi(login='user',
    api_key='da39a3ee5e6b4b0d3255bfef95601890afd80709')

# check balance
response = mapi.get_balance()
balance = response['money']

# if we have enough money, send some sms
if balance > 0.5:
    phone = '79998887766'
    response = mapi.send_sms(phone=phone,
                             text='Hello from web!', sender='web.ru')
    # check the state of sms
    sms_id = response[0][phone]['id_sms']

    # Server can't process id_sms for so fast
    sleep(5)
    while True:
        try:
            response = mapi.get_status(sms_id)
            break
        except mobilvest.CantGetStatus:
            sleep(1)
            continue

    if response[sms_id]['status'] == 'deliver':
        print "Message delivered!"
    else:
        print "Message wasn't delivered: {}".format(response[sms_id]['status'])

```

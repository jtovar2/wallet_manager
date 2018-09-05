import jwt
import json
import requests
import os

PRIVATE_ENCRYPTION_KEY = os.environ['ENCRYPTION_KEY']


request_body = {}
request_body['action'] = 'getbalance'
request_body['account'] = 'javier'
request_body['currency'] = 'digibyte'

encoded = jwt.encode(request_body, PRIVATE_ENCRYPTION_KEY, algorithm='HS256')

response = requests.post('http://127.0.0.1:5000/crypto_cli', data=encoded)
print response.text


import jwt
import json
import requests
import os

PRIVATE_ENCRYPTION_KEY = os.environ['ENCRYPTION_KEY']
PRIVATE_ENCRYPTION_KEY = "a;lkjasdfm,nx.cvhpuioqwerkjbl,absdf"

request_body = {}
request_body['action'] = 'getbalance'
request_body['account'] = 'main'
request_body['currency'] = 'dogecoin'

encoded = jwt.encode(request_body, PRIVATE_ENCRYPTION_KEY, algorithm='HS256')

response = requests.post('http://10.0.0.123:5000/crypto_cli', data=encoded)
#response = requests.post('http://24.98.193.43:5000/crypto_cli', data=encoded)
print response.text


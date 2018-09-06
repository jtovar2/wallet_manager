import jwt
import json
import requests
import os


WALLET_MANAGER_PRIVATE_KEY = None
private_key_file_path = os.environ['WALLET_MANAGER_PRIVATE_KEY_PATH']

with open(private_key_file_path, 'r') as private_key_file:
    WALLET_MANAGER_PRIVATE_KEY = private_key_file.read()


request_body = {}
request_body['action'] = 'getbalance'
request_body['account'] = 'main'
request_body['currency'] = 'dogecoin'

encoded = jwt.encode(request_body, WALLET_MANAGER_PRIVATE_KEY, algorithm='RS256')

response = requests.post('http://10.0.0.123:5000/crypto_cli', data=encoded)
#response = requests.post('http://24.98.193.43:5000/crypto_cli', data=encoded)
print response.text


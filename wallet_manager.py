from flask import Flask, request
import json
import jwt
import subprocess
import os

application = Flask(__name__)
LCP = os.environ['LCP']
PUBLIC_ENCRYPTION_KEY = os.environ['ENCRYPTION_KEY']


final_route_string = '/crypto_cli'

supported_currencies_to_exec_map = {}


supported_currencies_to_exec_map['digibyte'] = '/home/javier/digibyte-6.16.2/bin/digibyte-cli'

supported_currencies_to_exec_map['dogecoin'] = '/home/javier/dogecoin-1.10.0/bin/dogecoin-cli'

supported_actions = ['getbalance','getnewaddress', 'move', 'sendfrom', 'gettransaction']



@application.route(final_route_string, methods=['POST'])
def command_line_executer():
        encrypted_request_string = request.data

        json_dict = jwt.decode( encrypted_request_string, PUBLIC_ENCRYPTION_KEY, algorithm='HS256')


        currency = json_dict['currency']
        action = json_dict['action']
        account = json_dict['account']

        if action not in supported_actions:
            return abort(403,'action not supported')

        if currency is not None or action is not None and account is not None or currency != ""or action != "" or account != "":
            command = supported_currencies_to_exec_map[ currency ]
            response = subprocess.check_output([command, action, account])
            
            return str(response)

        else:
            abort(404, 'malformed request')

if __name__ == "__main__":
    application.run(host='0.0.0.0')

from flask import Flask, request
import json
import jwt
import subprocess
import os

#for GAE do this shit
#from jwt.contrib.algorithms.pycrypto import RSAAlgorithm
#jwt.register_algorithm('RS256', RSAAlgorithm(RSAAlgorithm.SHA256))


application = Flask(__name__)
LCP = os.environ['LCP']

WALLET_MANAGER_PUBLIC_KEY = None
public_key_file_path = os.environ['WALLET_MANAGER_PUBLIC_KEY_PATH']

with open(public_key_file_path, 'r') as public_key_file:
        WALLET_MANAGER_PUBLIC_KEY = public_key_file.read()

final_route_string = '/crypto_cli'

supported_currencies_to_exec_map = {}


supported_currencies_to_exec_map['digibyte'] = '/home/javier/digibyte-6.16.2/bin/digibyte-cli'

supported_currencies_to_exec_map['dogecoin'] = '/home/javier/dogecoin-1.10.0/bin/dogecoin-cli'

supported_actions = ['getbalance','getnewaddress', 'move', 'sendfrom', 'gettransaction']



@application.route(final_route_string, methods=['POST'])
def command_line_executer():
        encrypted_request_string = request.data

        json_dict = jwt.decode( encrypted_request_string, WALLET_MANAGER_PUBLIC_KEY, algorithm='RS256')


        currency = json_dict['currency']
        action = json_dict['action']
        account = json_dict['account']

        if action not in supported_actions:
            return abort(403,'action not supported')


        shell_command_format = []
        if action in ['move', 'sendfrom']:
            account = None
            to_acct = None
            amount = None
            comment = None

            if 'account' not in json_dict or json_dict['account'] == "":
                return abort(403,'account not in request')
            else:
                account = json_dict['account']
            if 'to_acct' not in json_dict or json_dict['to_acct'] == "":
                return abort(403,'to_acct not in request')
            else:
                to_acct = json_dict['to_acct']
            ##check for vars and format command
            if 'amount' not in json_dict or json_dict['amount'] == "":
                return abort(403,'amount not in request')
            else:
                amount = json_dict['amount']
        if action in ['gettransaction']:
            ##cehck for vars and format command
        if actin in ['getbalance', 'getnewaddress']:
            ###check for vars and format command

        if currency is not None or action is not None and account is not None or currency != ""or action != "" or account != "":
            command = supported_currencies_to_exec_map[ currency ]
            response = subprocess.check_output([command, action, account])
            
            return str(response)

        else:
            abort(404, 'malformed request')

if __name__ == "__main__":
    application.run(host='0.0.0.0')

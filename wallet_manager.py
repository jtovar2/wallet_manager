from flask import Flask, request, abort
import json
import jwt
import subprocess
import os



application = Flask(__name__)
LCP = os.environ['LCP']

WALLET_MANAGER_PUBLIC_KEY = None
public_key_file_path = os.environ['WALLET_MANAGER_PUBLIC_KEY_PATH']

with open(public_key_file_path, 'r') as public_key_file:
        WALLET_MANAGER_PUBLIC_KEY = public_key_file.read()

crypto_wallet_route_string = '/crypto_cli'

supported_currencies_to_exec_map = {}


supported_currencies_to_exec_map['dogecoin'] = '/usr/bin/dogecoin-cli -conf=/etc/dogecoin/dogecoin.conf '

supported_actions = ['getbalance','getnewaddress', 'move', 'sendfrom', 'gettransaction']




@application.route("/")
def command_line_executer2():
    return "HELLO WORLD"

@application.route(crypto_wallet_route_string, methods=['POST'])
def command_line_executer():
        encrypted_request_string = request.get_data()

        json_dict = jwt.decode( encrypted_request_string, WALLET_MANAGER_PUBLIC_KEY, algorithm='RS256')


        currency = json_dict['currency']
        action = json_dict['action']
        command = None

        if action not in supported_actions:
            return abort(403,'action not supported')

        if currency is not None or action is not None and account is not None or currency != ""or action != "" or account != "":
            command = supported_currencies_to_exec_map[ currency ]

        else:
            abort(404, 'malformed request')


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

            shell_command_format = [command, action, account, to_acct, amount]
            if 'comment' in json_dict and json_dict['comment'] != "":
		comment = json_dict['comment']
		shell_command_format.append(comment)

        if action in ['gettransaction']:
            txn_id = None
            if 'account' not in json_dict or json_dict['account'] == "":
                return abort(403,'account not in request')
            else:
                account = json_dict['account']
            shell_command_format = [command, action,txn_id]
            ##cehck for vars and format command
        if action in ['getbalance', 'getnewaddress']:
            account = None
            if 'account' not in json_dict or json_dict['account'] == "":
                return abort(403,'account not in request')
            else:
                account = json_dict['account']
            shell_command_format = [command, action,account]

            
        response = subprocess.check_output(shell_command_format)
        return str(response)


if __name__ == "__main__":
    application.run(host='0.0.0.0',debug=True, port=8080)

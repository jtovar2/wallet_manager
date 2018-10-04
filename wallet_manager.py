from flask import Flask, request, abort
import json
import jwt
import subprocess
import os
import textract

import datastore_manager
from google.cloud import storage
from google.cloud import vision

#for GAE do this shit
#from jwt.contrib.algorithms.pycrypto import RSAAlgorithm
#jwt.register_algorithm('RS256', RSAAlgorithm(RSAAlgorithm.SHA256))


application = Flask(__name__)
LCP = os.environ['LCP']

WALLET_MANAGER_PUBLIC_KEY = None
public_key_file_path = os.environ['WALLET_MANAGER_PUBLIC_KEY_PATH']

with open(public_key_file_path, 'r') as public_key_file:
        WALLET_MANAGER_PUBLIC_KEY = public_key_file.read()

crypto_wallet_route_string = '/crypto_cli'
text_processor_route_string = '/texextract/<bucket_id>/<blob_id>'

supported_currencies_to_exec_map = {}


supported_currencies_to_exec_map['digibyte'] = '/home/javier/digibyte-6.16.2/bin/digibyte-cli'

supported_currencies_to_exec_map['dogecoin'] = '/home/javier/dogecoin-1.10.0/bin/dogecoin-cli'

supported_actions = ['getbalance','getnewaddress', 'move', 'sendfrom', 'gettransaction']


##stuff of text extractor
project = os.environ['PROJECT_ID']
storage_client = storage.Client()
vision_client = vision.ImageAnnotatorClient()
blobs_to_be_processed_kind = 'blobs_processed_{LCP}'.format(LCP=LCP)

blob_processor_dm = datastore_manager.DatastoreManager(project, blobs_to_be_processed_kind, lcp=LCP)




@application.route(text_processor_route_string, methods=['GET'])
def text_extractor(bucket_id, blob_id):
    bucket = storage_client.get_bucket(bucket_id)

    blob = storage.blob.Blob(blob_id, bucket)


    content = blob.download_as_string()
    with open(blob_id, 'wb') as file_obj:
        blob.download_to_file(file_obj)


    local_text = None
    try:
        text = textract.process(blob_id)
        print("local**********************")
        print(text)
        local_text = text
        local_text = local_text.replace('\f', '').replace('\n', '')

        print("local*******************")
    except:
        print("textract fucked up")


    image = vision.types.Image(content=content)
    gcp_document_text_response = vision_client.document_text_detection(image=image)
    handWriting_image_context = vision.types.ImageContext(
        language_hints=['en-t-i0-handwrit'])


    gcp_text_response = vision_client.text_detection(image=image)
    gcp_handwriting_response = vision_client.document_text_detection(image=image,
                                              image_context=handWriting_image_context)

    os.remove(blob_id)
    
    if (gcp_document_text_response.full_text_annotation.text is not None and gcp_document_text_response.full_text_annotation.text != "") or ( local_text is not None and local_text != "") or ( gcp_handwriting_response is not None and gcp_handwriting_response != "") or ( gcp_text_response is not None and gcp_text_response != ""):
        gcp_document_text = gcp_document_text_response.full_text_annotation.text.encode('ascii', 'ignore')
        gcp_handwriting_text = gcp_handwriting_response.full_text_annotation.text.encode('ascii', 'ignore')
        gcp_text = gcp_handwriting_response.full_text_annotation.text.encode('ascii', 'ignore')

        responses = [gcp_handwriting_text, gcp_text, gcp_document_text, local_text]

        for response in responses:
            if response is None:
                responses.remove(response)

        responses.sort(key=len, reverse=True)

        json_dict = {}
        json_dict['local_text'] = local_text
        json_dict['gcp_document_text'] = gcp_document_text
        json_dict['gcp_handwriting_text'] = gcp_handwriting_text
        json_dict['gcp_text'] = gcp_text
        json_dict['bucket'] = bucket_id
        json_dict['id'] = str(blob_id)
        json_dict['official_response'] = responses[0]

        key = blob_processor_dm.add_entity_with_id(json_dict)
        print(key)
        return "OK" + str(key)


    return abort(403,'unable_to_process_blob')



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
    application.run(host='0.0.0.0')

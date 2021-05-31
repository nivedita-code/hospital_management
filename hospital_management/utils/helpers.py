import base64
import inspect
import os
import traceback
from datetime import datetime
from http import HTTPStatus
import jwt
from Crypto.Cipher import AES
from flask import current_app, session, request, jsonify, g


dirname = os.path.dirname(__file__)
CRYPTO_KEY = 'testtesttesttesttesttest'
CRYPTO_INITIALIZATION_VECTOR = 'testtesttesttest'
AUTH_KEY = "fgnuoies84930njio1"


def catch_exception(e):
    """

    :param e:
    :return:
    """
    try:
        variable_trace = {}
        for line in inspect.trace():
            variable_trace[line[3]] = str(line[0].f_locals)
        current_app.logger.exception(e)
        error_time = datetime.utcnow().strftime("%m/%d/%Y, %H:%M:%S")
        session_json = {}
        for key in session.keys():
            session_json[key] = session[key]
        current_app_config_json = {}
        for config_key in current_app.config.keys():
            current_app_config_json[config_key] = current_app.config[config_key]

        data = {
            'traceback': traceback.format_exc().splitlines(),
            'error_time': error_time,
            'request_origin': request.environ.get('REMOTE_ADDR'),
            'debug': request.headers.get('Debug', False),
            'request_path': request.path,
            'request_type': request.method,
            'request_data': session['request_details']['payload'] if session.get('request_details') else request.json,
            'authorization_exists': False,
            'error_message': str(e),
            'base_url': request.host,
            'user_agent': str(request.user_agent),
            'function_variables': variable_trace,
            'last_modified_time': datetime.utcnow().strftime("%m/%d/%Y, %H:%M:%S"),
            'session': session_json,
            'current_app_config': current_app_config_json
        }
        if session['Authorization']:
            data['user_id'] = session['user_id']
            data['token'] = session['Authorization']
            data['account_id'] = session['account_id']
            data['email'] = session.get('email') or session.get('email_id')
            data['authorization_exists'] = True
        if not g.db.session.has_ended:
            g.db.session.abort_transaction()
            g.db.session.end_session()
        if isinstance(e, dict):
            return jsonify(e)
        return jsonify(
            {'status_id': 0, 'reason': 'Something went wrong. Please try again.', 'response': str(e)})
    except Exception as error:
        current_app.logger.exception(error)
        return jsonify({'status_id': 0,
                        'reason': 'Unexpected Error Occurred. Please Try Again.'}), HTTPStatus.INTERNAL_SERVER_ERROR


def catch_write_conflict_exception(e):
    """

    :param e:
    :return:
    """
    if e._OperationFailure__details.get("errorLabels"):
        if "TransientTransactionError" in e._OperationFailure__details.get("errorLabels"):
            if not g.db.session.has_ended:
                g.db.session.abort_transaction()
                g.db.session.end_session()
            return jsonify({'status_id': 0, 'reason': 'Another Operation is in Progress, Please Try Again.'})
        else:
            return catch_exception(e)
    else:
        return catch_exception(e)


def catch_response_exception(e):
    if not g.db.session.has_ended:
        g.db.session.abort_transaction()
        g.db.session.end_session()
    catch_exception(e)
    if isinstance(e, dict):
        return jsonify(e)
    return jsonify({'status_id': 0, 'reason': str(e)})


def decrypt_data(encrypted_pw):
    decryption_suite = AES.new(CRYPTO_KEY, AES.MODE_CFB, CRYPTO_INITIALIZATION_VECTOR)
    return decryption_suite.decrypt(encrypted_pw)


def _encrypt_data(password):
    cipher = AES.new(CRYPTO_KEY, AES.MODE_CFB, CRYPTO_INITIALIZATION_VECTOR)
    return cipher.encrypt(password)


def decrypt_auth_token(encoded_token):
    """
    :param encoded_token: Token
    :rtype: object
    """
    encrypted_token = base64.urlsafe_b64decode(encoded_token)
    token = decrypt_data(encrypted_token)
    return jwt.decode(token, AUTH_KEY)


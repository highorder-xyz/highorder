import json
from callpy.web.response import (
    jsonify
)

def bad_request(error_type:str, error_msg:str = '', code:int = 400):
    rv = jsonify({'ok':False, 'error_type': error_type, 'error_msg': error_msg})
    rv.status_code = code
    return rv

def server_error(error_type:str, error_msg:str = '', code:int = 500):
    rv = jsonify({'ok':False, 'error_type': error_type, 'error_msg': error_msg})
    rv.status_code = code
    return rv

def client_invalid(msg:str = ''):
    return bad_request('ClientInvalid', msg or '', 400)

def session_invalid(msg: str = ''):
    return bad_request('SessionInvalid', msg or 'session invalid or expired', 400)
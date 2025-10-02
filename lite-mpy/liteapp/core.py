
import umqtt
import request
import ujson

try:
    import usys as sys
except ImportError:
    import sys

from usr.config import HIGHORDER_SERVICE, APPLICATION_ID
import modem
import SecureData
import urandom as random
import ucollections

ASCII_LETTER_DIGITS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
ASCII_LETTER_LOWER = 'abcdefghkmnpqrstuvwxyz'
ASCII_DIGITS = '1234567890'

class Device:
    def __init__(self, device_id):
        self.device_id = device_id
        self.device_type = 'dashboard'
        self.imei = modem.getDevImei()
        self.device_model = modem.getDevModel()
        self.device_sn = modem.getDevSN()
        self.firm_version = modem.getDevFwVersion()

    def to_dict(self):
        return dict(
            device_id = self.device_id,
            device_type = self.device_type,
            imei = self.imei,
            device_model = self.device_model,
            device_sn = self.device_sn,
            firm_version = self.firm_version
        )


class DataStore:
    APP_ID_INDEX = 1
    LOCAL_ID_INDEX = 2
    USER_ID_INDEX = 9
    SESSION_TOKEN_INDEX = 10

    def __init__(self, app_id):
        self.app_id = app_id
        self.local_id = ''
        self.user_id = ''
        self.session_token = ''
        local_id = self.read_local_id()
        if not local_id:
            self.clear()
            local_id = self.create_local_id()
            self.save_local_id(local_id)
            self.save_app_id(app_id)
        else:
            saved_app_id = self._read_app_id()
            if len(saved_app_id) > 0 and saved_app_id != app_id:
                self.clear_app_id()
                self.clear_user_id()
                self.clear_session_token()
                self.save_app_id(app_id)
            else:
                self.read_user_id()
                self.read_session_token()

    def create_local_id(self):
        gen_ids = []
        for i in range(0, 4):
            gen_ids.append(random.choice(ASCII_LETTER_LOWER))
            for j in range(0, 3):
                gen_ids.append(random.choice(ASCII_DIGITS))
        random_id = ''.join(gen_ids)
        return 'LBPY%s'%(random_id)

    def _read_local_id(self):
        databuf = bytearray(52)
        length = SecureData.Read(self.LOCAL_ID_INDEX, databuf, 100)
        return databuf[:length].decode('utf-8').strip()

    def read_local_id(self):
        local_id = self._read_local_id()
        self.local_id = local_id
        return local_id

    def save_local_id(self, local_id):
        data = local_id.encode('utf-8')
        SecureData.Store(self.LOCAL_ID_INDEX, data, len(data))
        self.local_id = local_id

    def clear_local_id(self):
        SecureData.Store(self.LOCAL_ID_INDEX, ' '*52, 52)
        self.local_id = ''


    def _read_app_id(self):
        databuf = bytearray(52)
        length = SecureData.Read(self.APP_ID_INDEX, databuf, 100)
        return databuf[:length].decode('utf-8').strip()

    def read_app_id(self):
        app_id = self._read_app_id()
        self.app_id = app_id
        return app_id

    def save_app_id(self, app_id):
        data = app_id.encode('utf-8')
        SecureData.Store(self.APP_ID_INDEX, data, len(data))
        self.app_id = app_id

    def clear_app_id(self):
        SecureData.Store(self.APP_ID_INDEX, ' '*52, 52)
        self.app_id = ''


    def _read_user_id(self):
        databuf = bytearray(100)
        length = SecureData.Read(self.USER_ID_INDEX, databuf, 100)
        return databuf[:length].decode('utf-8').strip()

    def read_user_id(self):
        user_id = self._read_user_id()
        self.user_id = user_id
        return user_id

    def save_user_id(self, user_id):
        data = user_id.encode('utf-8')
        SecureData.Store(self.USER_ID_INDEX, data, len(data))
        self.user_id = user_id

    def clear_user_id(self):
        SecureData.Store(self.USER_ID_INDEX, ' '*100, 100)
        self.user_id = ''

    def _read_session_token(self):
        databuf = bytearray(100)
        length = SecureData.Read(self.SESSION_TOKEN_INDEX, databuf, 100)
        return databuf[:length].decode('utf-8').strip()

    def read_session_token(self):
        session_token = self._read_session_token()
        self.session_token = session_token
        return session_token

    def save_session_token(self, session_token):
        data = session_token.encode('utf-8')
        SecureData.Store(self.SESSION_TOKEN_INDEX, data, len(data))
        self.session_token = session_token

    def clear_session_token(self):
        SecureData.Store(self.SESSION_TOKEN_INDEX, ' '*100, 100)
        self.session_token = ''

    def clear(self):
        SecureData.Store(self.LOCAL_ID_INDEX, ' '*52, 52)
        SecureData.Store(self.APP_ID_INDEX, ' '*52, 52)
        SecureData.Store(self.USER_ID_INDEX, ' '*100, 100)
        SecureData.Store(self.SESSION_TOKEN_INDEX, ' '*100, 100)

class HighOrderCore:

    def __init__(self, screen_size = (240, 320), lang='zh-CN'):
        self.screen_size = {
            "width": screen_size[0],
            "height": screen_size[1]
        }
        self.lang = lang
        self.store = DataStore(APPLICATION_ID)
        self.context = self.get_platform_info()
        self.srv_url = HIGHORDER_SERVICE.rstrip('/')
        self.reset_headers()
        self.pages =  ucollections.deque((), 6)

    def reset_headers(self):
        self.headers = {
            "Content-Type": "application/json",
            'X-HighOrder-Application-Id': APPLICATION_ID
        }
        session_token = self.store.session_token
        if session_token:
            self.headers['X-HighOrder-Session-Token'] = session_token


    def get_platform_info(self):
        impl = sys.implementation
        device = Device(self.store.read_local_id())
        return {
            'platform': "lite",
            'route': '/',
            'vendor': sys.platform,
            'os': impl[0],
            'os_version': "%s.%s"%(impl[1][0], impl[1][1]),
            'language': self.lang,
            'screen_size': self.screen_size,
            'page_size': self.screen_size,
            'is_virtual': False,
            'web_version': '0.0',
            'as_device': True,
            'device': device.to_dict()
        }

    def send_request(self, data):
        url = self.srv_url + '/service/hola/lite'
        data['context'] = self.context
        response = request.post(url, data=ujson.dumps(data), headers=self.headers, decode=True)
        return response

    def handle_response(self, response):
        status = response.status_code // 100

        if status == 2:
            ret = response.json()
            commands = ret['data'].get('commands', [])
            for command in commands:
                name = command.get('name')
                args = command.get('args', {})
                if not name:
                    continue
                self.handle_command(name.lower(), args)
        elif status == 4:
            print('got response code: %s'%(response.status_code))
        elif status == 5:
            print('got response code: %s'%(response.status_code))
        else:
            print('got response code: %s'%(response.status_code))

    def handle_command(self, name, args):
        if name == 'set_session':
            self.handle_set_session(args.get('session'), args.get('user'))
        elif name == 'show_page':
            page = args.get('page', {})
            if page:
                self.pages.append(page)

    def handle_set_session(self, session, user):
        if not session:
            self.store.clear_session_token()
            self.store.clear_user_id()
            return
        else:
            self.store.save_session_token(session['session_token'])

        if not user:
            self.store.clear_user_id()
        else:
            self.store.save_user_id(user['user_id'])

        self.reset_headers()

    def session_start(self):
        response = self.send_request({
            "command":"session_start"
        })
        self.handle_response(response)

    def navigate_to(self, route):
        response = self.send_request({
            "command":"route_to", "args":{"route": route}
        })
        self.handle_response(response)
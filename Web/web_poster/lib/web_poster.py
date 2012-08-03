# coding=utf8

from lib.opener import Opener
import json, re

class Web_poster:
    def __init__(self, config={}):
        self.opener = Opener(has_cookie=True, cookie_filename='cookies/cookie.txt')
        self.config = config
        self.content = None

    @property
    def is_logined(self):
        return self.opener.is_logined

    @property
    def charset(self):
        return self.opener.charset

    @charset.setter
    def charset(self, value):
        self.opener.set_charset(value)

    @property
    def headers(self):
        return self.opener.get_headers()

    @headers.setter
    def headers(self, value):
        self.opener.set_headers(value)

    def _decode(self, content, errors='ignore'):
        """ 返回 unicode 字符串. """
        return content.decode(self.charset, errors)

    def _encode(self, content, errors='ignore'):
        """ 返回 bytes 字符串. """
        return content.encode(self.charset, errors)

    def _post_data(self, data=None):
        """  对 post data 进行预处理. """
        if data and re.match(r'^\{|\[|"', data):
            data = json.loads(data)
        return data

    def get_response_info(self):
        return self.opener.get_response_info()

    def get_request_info(self):
        return self.opener.get_request_info()

    def get_content(self, raw_string=False):
        return self.content if not raw_string else self._encode(self.content)

    def clear_content(self):
        self.content = None

    def get_config(self):
        return self.config

    def update_config(self, config):
        self.config.update(config)

    def fetch_content(self):
        try:
            url = self.config['url']
            method = self.config['method'].lower()
            data = None
            if method == 'post':
                data = self.config.get('data', '')
                data = self._post_data(data)
            print(url, method, data)
            self.content = self.opener.open(url, data, success=False, raw_string=False)
            return True
        except Exception as e:
            print(e)
            return False

    def get_code_img(self, url=None):
        try:
            url = url and url or self.config['code_image_url']
            print(url)
            return self.opener.open(url, success=False)
        except Exception as e:
            print(e)
            return None

    def login(self):
        if self.is_logined:
            return True
        try:
            config = self.config['auth']
            login_url = config['auth']['url']
            data = self._post_data(config['auth']['pre_post_data'])
            check_url = config['check_url']
            check_data= config['check_data']
            login_data = {
                config['username_key']: config['username'],
                config['password_key']: config['password']
            }
            if 'code_key' in config:
                data[config['code_key']] = config['code']
            if isinstance(pre_post_data, dict):
                data.update(login_data)
            else:
                data = '%s&%s' % (urllib.parse.urlencode(login_data), data)
            return self.opener.login(login_url, data, check_url, check_data)
        except Exception as e:
            print(e)
            return False

    def logout(self):
        self.opener.logout()

    def search(self, target, content=None, start_pos=None, end_pos=None, case_sensitive=False):
        content = content if content is not None else self.get_content()
        target = target if not case_sensitive else target.lower()
        return content.find(target, start_pos, end_pos)

    def re_test(self, reg, content=None):
        content = content if content is not None else self.get_content()
        return list(reg.finditer(content))

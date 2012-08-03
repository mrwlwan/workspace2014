# coding=utf8
# 仅适用于 Python 3

import os, urllib.request, urllib.parse, http.cookiejar, configparser
from functools import wraps

def coroutine(func):
    @wraps(func)
    def call(*args, **kwargs):
        g = func(*args, **kwargs)
        next(g)
        return g
    return call

##########################################################################

def get_configs(filename, encoding='utf8'):
    configs = {}
    parser = configparser.ConfigParser()
    parser.read(filename, encoding=encoding)
    for section in parser.sections():
        configs[section] = dict(parser.items(section))
    return configs

##########################################################################

class Opener:
    def __init__(self, has_cookie=False, headers={}, cookie_filename=None, charset='utf8'):
        self.has_cookie = has_cookie
        self.cookie_filename = None
        self.charset = charset
        self.opener = urllib.request.build_opener()
        self.cookiejar = None
        self.is_cookie_file_exists = False
        if has_cookie:
            self.set_cookie(cookie_filename)
        #self.opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0')]
        self.set_headers(headers)

        self._sock = None
        self._url = None
        self._data = None
        self.is_logined = False

    def get_response_info(self):
        """ 取得 response 的信息. """
        return self._sock is not None and self._sock.info() or None

    def get_request_info(self):
        return {
            'url': self._url,
            'data': self._data
        }

    def get_headers(self):
        """ 取得 Request Headers, 以 dict 的形式返回. """
        return dict(self.opener.addheaders)

    def set_headers(self, headers):
        """ 设置Request Herders, 参数 headers, 必须是 dict. """
        old_headers = {'User-agent': 'Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0'}
        if headers:
            old_headers.update(headers)
        self.opener.addheaders = list(old_headers.items())

    def set_cookie(self, cookie_filename=None):
        if cookie_filename:
            self.cookie_filename = cookie_filename
            self.cookiejar = http.cookiejar.LWPCookieJar(cookie_filename)
            if os.path.exists(cookie_filename):
                self.cookiejar.load()
                self.is_cookie_file_exists = True
        else:
            self.cookiejar = http.cookiejar.CookieJar()
        cookie_handler = urllib.request.HTTPCookieProcessor(self.cookiejar)
        self.opener.add_handler(cookie_handler)
        self.has_cookie = True

    def set_charset(self, charset):
        self.charset = charset

    def save_cookie_file(self):
        if self.has_cookie and self.cookie_filename:
            self.opener.cookiejar.save()
            self.is_cookie_file_exists = True

    def remove_cookie_file(self):
        if self.is_cookie_file_exists:
            os.remove(self.cookie_filename)
            self.is_cookie_file_exists = False

    def open(self, url, data=None, timeout=None, success=True, raw_string=True):
        self._url = url
        self._data = data
        if data is not None:
            if isinstance(data, dict):
                data = urllib.parse.urlencode(data, encoding=self.charset, errors='ignore')
            if isinstance(data, str):
                data = data.encode(self.charset)
        self._data = data
        while 1:
            try:
                self._sock = self.opener.open(url, data, timeout)
                if self._sock.getcode() == 200:
                    html = self._sock.read()
                    if not raw_string:
                        html = html.decode(self.charset, 'ignore')
                    self._sock.close()
                    return html
                self._sock.close()
            except urllib.request.HTTPError as e:
                if e.code == 404:
                    print('404 http error')
                    return raw_string and b'' or ''
            except Exception as e:
                print(e)
            if not success:
                return None

    def check_login(self, check_url, check_data):
        if self.is_logined:
            print('你已经登录')
            return True
        check_data = check_data.encode(self.charset)
        content = self.opener.open(check_url)
        if content.find(check_data) >= 0:
            self.logined = True
            self.cookiejar.save()
            return True
        else:
            self.logined = False
            return False

    def login(self, login_url, data, check_url, check_data):
        if self.is_logined:
            print('你已经登录')
            return True
        if self.is_cookie_file_exists and self.check_login(check_url, check_data):
            pass
        else:
            self.opener.open(login_url, data)
            self.check_login(check_url, check_data)
        if self.is_logined:
            print('登录成功 :)')
            self.save_cookie_file()
            return True
        else:
            print('登录失败, 请检查用户名或者密码是否正确 :(')
            self.remove_cookie_file()
            return False

    def logout(self):
        if self.has_cookie:
            self.cookiejar.clear()
            self.is_logined = False

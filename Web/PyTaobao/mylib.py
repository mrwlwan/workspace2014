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
    def __init__(self, has_cookie=False, headers=[], cookie_filename=None):
        self.opener = urllib.request.build_opener()
        self.cookiejar = None
        self._cookie_file_exists = False
        if has_cookie:
            if cookie_filename:
                self.cookiejar = http.cookiejar.LWPCookieJar(cookie_filename)
                if os.path.exists(cookie_filename):
                    self.cookiejar.load()
                    self._cookie_file_exists = True
            else:
                self.cookiejar = http.cookiejar.CookieJar()
            cookie_handler = urllib.request.HTTPCookieProcessor(self.cookiejar)
            self.opener.add_handler(cookie_handler)
        self.opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0')] + headers

    def _check_login(self, check_url, check_data='', decoder='utf8'):
        html = self.open(check_url, decoder=decoder)
        if html.find(check_data) >= 0:
            print('登录成功!')
            return True
        else:
            return False

    def open(self, url, data=None, timeout=None, success=True, decoder=None):
        data = data and urllib.parse.urlencode(data).encode('ascii') or None
        while 1:
            try:
                sock = self.opener.open(url, data, timeout)
                if sock.getcode() == 200:
                    html = sock.read()
                    if decoder:
                        html = html.decode(decoder, 'ignore')
                    sock.close()
                    return html
                sock.close()
            except urllib.request.HTTPError as e:
                if e.code == 404:
                    print('404 http error')
                    return decoder and '' or b''
            except Exception as e:
                print(e)
            if not success:
                return None

    def login(self, login_url, data=None, has_validate_img=False, validate_img_url=None, validate_img_query_name='validateimg', saved_img_filename='验证码.bmp', check_url=None, check_data='', decoder='utf8'):
        # 如果未设置验证链接,则用登录的链接代替
        if not check_url:
            check_url = login_url
        # 如果是文件型的cookiejar,则先行验证登录是否成功(测试文件里的Cookie是否还有效)
        is_filecookiejar = issubclass(self.cookiejar.__class__, http.cookiejar.FileCookieJar)
        if self._cookie_file_exists and self._check_login(check_url, check_data, decoder):
            return
        while 1:
            if has_validate_img:
                with open(saved_img_filename, 'bw') as f:
                    f.write(self.open(validate_img_url).read())
                    f.close()
                print('请输入验证码:')
                input_str = input()
                input_str = input_str.strip()
                data.update({validate_img_query_name: input_str})
            html = self.open(login_url, data, decoder=decoder)
            login_check = self._check_login(check_url, check_data, decoder)
            if login_check:
                if is_filecookiejar:
                    self.cookiejar.save()
                return





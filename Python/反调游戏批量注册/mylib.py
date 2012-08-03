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

    def open(self, url, data=None, timeout=None, success=True, decoder=None):
        data = data and urllib.parse.urlencode(data, encoding='gbk', errors='ignore').encode('ascii') or None
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

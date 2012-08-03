# coding=utf8
# 仅适用于 Python 3

import urllib.request
from functools import wraps

def coroutine(func):
    @wraps(func)
    def call(*args, **kwargs):
        g = func(*args, **kwargs)
        next(g)
        return g
    return call

class Opener:
    def __init__(self, has_cookie=False, headers=[]):
        self.opener = urllib.request.build_opener()
        self.cookiejar = None
        if has_cookie:
            cookie_handler = urllib.request.HTTPCookieProcessor()
            self.cookiejar = cookie_handler.cookiejar
            self.opener.add_handler(cookie_handler)
        self.opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0')] + headers

    def open(self, url, data=None, timeout=None, success=True, encode=None):
        while 1:
            try:
                sock = self.opener.open(url, data, timeout)
                if sock.getcode() == 200:
                    html = sock.read()
                    sock.close()
                    if encode:
                        return html.decode(encode, errors='ignore')
                    return str(html)
                sock.close()
            except Exception as e:
                print(e)
            if not success:
                return None

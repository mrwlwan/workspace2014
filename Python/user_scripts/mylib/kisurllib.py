# coding=utf8
""" 适用于py2和py的urllib库. """

import sys, os

is_py3 = tuple(sys.version_info)[0] >= 3

if is_py3:
    from urllib.request import *
    from urllib.parse import *
    from http.cookiejar import LWPCookieJar, DefaultCookiePolicy
    unicode = str
    bytes = bytes
else:
    from urllib import *
    from urllib2 import *
    from urlparse import *
    from cookielib import LWPCookieJar, DefaultCookiePolicy
    unicode = unicode
    bytes = str

_opener = None

def urlopen(url, params=None, data=None, **kwargs):
    """ 简单的HTTP(S)请求. """
    return DefaultOpener().open(url, params=params, data=data, **kwargs)


class DefaultOpener:
    """ 简单的Opener, 主要用于全局的urlopen. """
    def __init__(self):
        global _opener
        if not _opener:
            _opener = build_opener()
        self.opener = _opener

    def open(self, url, params=None, data=None, method=None, headers={}, proxies={}, timeout=None, **kwargs):
        """ 打开目标链接, 返回一个 HttpResponse对象.

        @url(str/Request): 目标链接.
        @param(str/dict/pairs): query string.
        @data(bytes/dict/pairs): post data.
        @headers(dict): http request headers.
        @proxies(dict): 代理, 如:{'http': 'xx.xx.xx.xx:3128', 'https': 'xxx.xxx.xxx.xxx:8080'}.
        @timeout(float): 超时.
        @kwargs(mixed): OpenerDirector的open方法的其它参数
        """
        is_request_obj = isinstance(url, Request)
        if params:
            full_url = is_request_obj and url.get_full_url() or url
            url_parse_dict = urlparse(full_url)._asdict()
            query_param = url_parse_dict.get('query') + (isinstance(params, str) and params or urlencode(params))
            url_parse_dict['query'] = query_param
            full_url = urlunparse(url_parse_dict.values())
            request = Request(full_url)
        else:
            request = is_request_obj and url or Request(url)
        if data:
            if isinstance(data, bytes):
                request.data = data
            else:
                request.data = urlencode(data).encode('utf8')
        if method:
            request.get_method = lambda: method.upper()
        for key, value in headers.items():
            request.add_header(key, value)
        for proxy_type, proxy_host in proxies.items():
            request.set_proxy(proxy_host, proxy_type)
        return self.opener.open(request, timeout=timeout, **kwargs)


class Opener(DefaultOpener):
    """ 高级的Opener对象. """
    def __init__(self, cookie_path=None):
        self.opener = build_opener()
        self.cookiejar = LWPCookieJar(cookie_path)
        cookie_path and os.path.exists(cookie_path) and self.cookiejar.load()
        self.opener.add_handler(HTTPCookieProcessor(self.cookiejar))
        self.opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 5.1; rv:11.0) Gecko/20120101 Firefox/11.0')]

    def set_headers(self, arg={}, **kwargs):
        """ 设置headers.

        @arg(pairs/dict)
        @kwargs(mixed)
        """
        if not arg and not kwargs:
            return
        headers = dict(self.opener.addheaders)
        headers.update(arg)
        headers.update(kwargs)
        self.opener.addheaders = list(headers.items())

    def set_cookies(self, *args, **kwargs):
        """ 设置cookies.

        @args(pairs/dict)
        @kwargs(mixed)
        """
        for arg in args:
            cookie = DefaultCookiePolicy(**dict(arg))
            self.cookiejar.set_cookie(cookie)
        kwargs and self.cookiejar.set_cookie(DefaultCookiePolicy(**kwargs))

    def save_cookies(self, cookie_path=None):
        if cookie_path or self.cookiejar.filename:
            self.cookiejar.save(cookie_path)

# coding=utf8

from urllib.request import build_opener, HTTPCookieProcessor, Request
from urllib.parse import urlparse, urlunparse, urlencode, parse_qs
from http.cookiejar import LWPCookieJar, DefaultCookiePolicy
import os.path

class Opener:
    def __init__(self, cookie_path=None):
        self.opener = build_opener()
        self.cookiejar = LWPCookieJar()
        self.set_cookie_path(cookie_path)
        self.opener.add_handler(HTTPCookieProcessor(self.cookiejar))
        self.opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 5.1; rv:11.0) Gecko/20120101 Firefox/11.0')]
        self.last_request = None
        self.last_response = None

    @property
    def request_info(self):
        pass

    @property
    def response_info(self):
        pass

    def set_cookie_path(self, path):
        self.cookiejar.filename = path
        try:
            os.path.exists(path) and self.cookiejar.load()
        except:
            pass

    def set_headers(self, arg={}, **kwargs):
        if not arg and not kwargs:
            return
        headers = dict(self.opener.addheaders)
        headers.update(arg)
        headers.update(kwargs)
        self.opener.addheaders = list(headers.items())

    def set_cookies(self, *args, **kwargs):
        for arg in args:
            cookie = DefaultCookiePolicy(**arg)
            self.cookiejar.set_cookie(cookie)
        kwargs and self.cookiejar.set_cookie(DefaultCookiePolicy(**kwargs))

    def save_cookies(self, cookie_path=None):
        if cookie_path or self.cookiejar.filename:
            self.cookiejar.save(cookie_path)

    def urlopen(self, url, param=None, data=None, headers={}, proxies={}, timeout=None, encoding='utf8', errors='strict'):
        """ 打开目标链接, 返回一个 HttpResponse对象.

        @url(str/Request): 目标链接.
        @param(str/dict/pairs tuple): query string.
        @data(bytes/str/dict): post data.
        @headers(dict): http request headers.
        @proxies(dict): 代理, 如:{'http': 'xx.xx.xx.xx:3128', 'https': 'xxx.xxx.xxx.xxx:8080'}.
        @timeout(int): http request timeout.
        @encoding/errors(str): url编码.
        """
        if param:
            full_url = isinstance(url, Request) and url.get_full_url() or url
            url_parse_dict = urlparse(full_url)._asdict()
            query_param = url_parse_dict.get('query') + (isinstance(param, str) and param or urlencode(param, encoding, errors))
            url_parse_dict['query'] = query_param
            full_url = urlunparse(url_parse_dict.values())
            request = Request(full_url)
        else:
            request = isinstance(url, Request) and url or Request(url)
        if data:
            if isinstance(data, bytes):
                request.data = data
            elif isinstance(data, str):
                request.data = data.encode(encoding, errors)
            else:
                request.data = urlencode(data).encode(encoding, errors)
        for key, value in headers.items():
            request.add_header(key, value)
        for proxy_type, proxy_host in proxies.items():
            request.set_proxy(proxy_host, proxy_type)
        self.last_request = request
        self.last_response = self.opener.open(request, timeout=timeout)
        return self.last_response

    def clear(self):
        self.last_request = None
        self.last_response = None

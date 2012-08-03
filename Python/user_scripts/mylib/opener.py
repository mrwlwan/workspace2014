# coding=utf8

import urllib.request, urllib.parse, http.client, os

class Opener(urllib.request.OpenerDirector):
    def __init__(self, headers=None, has_cookie=False, cookie_path=None, encoding='utf8'):
        super().__init__()
        self.cookiejar = None
        self._last_request = None
        self._last_response = None
        self._encoding = encoding
        self._add_default_handlers()
        self._add_default_headers(headers)
        if has_cookie or cookie_path:
            self.init_cookie(cookie_path)

    @property
    def headers(self):
        return self.addheaders

    @headers.setter
    def headers(self, headers):
        """ Add request headers, parameter: headers is dict object or a pairs list. """
        if not headers:
            return
        headers = isinstance(headers, dict) and headers.items() or headers
        target_headers = dict(self.addheaders)
        target_headers.update(dict(
            ((key.lower().capitalize(), value) for key, value in headers)
        ))
        self.addheaders = list(target_headers.items())

    def _add_default_headers(self, headers):
        """ Add default request headers. """
        self.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 5.1; rv:11.0) Gecko/20120101 Firefox/11.0')]
        self.headers = headers

    def _add_default_handlers(self):
        """ Some base request handlers. """
        default_classes = [
            urllib.request.ProxyHandler,
            urllib.request.UnknownHandler,
            urllib.request.HTTPHandler,
            urllib.request.HTTPDefaultErrorHandler,
            urllib.request.HTTPRedirectHandler,
            urllib.request.FTPHandler,
            urllib.request.FileHandler,
            urllib.request.HTTPErrorProcessor
        ]
        if hasattr(http.client, "HTTPSConnection"):
            default_classes.append(urllib.request.HTTPSHandler)
        for klass in default_classes:
            self.add_handler(klass())

    def get_response_info(self):
        """ Get the response information. """
        return self._last_response is not None and self._last_response.info() or None

    def get_request_info(self):
        """ Get the request information. """
        if self._last_request is None:
            return {}
        return {
            'URL': self._last_request.get_full_url(),
            'Data': self._last_request.get_data(),
            'Headers': dict(self._last_request.header_items()),
        }

    def set_encoding(self, encoding):
        """ Set the default encoding. """
        self._encoding = encoding

    def init_cookie(self, cookie_path):
        """ Initial the cookie handler. """
        # Empty cookiJar object is False.
        if self.cookiejar is not None:
            print('You alread had the cookie handler.')
            return
        import http.cookiejar
        if cookie_path:
            self.cookiejar = http.cookiejar.LWPCookieJar(cookie_path)
            if os.path.exists(cookie_path):
                self.cookiejar.load()
        else:
            self.cookiejar = http.cookiejar.CookieJar()
        self.add_handler(urllib.request.HTTPCookieProcessor(self.cookiejar))

    def save_cookie(self):
        """ Save the cookiejar to the cookie file. """
        hasattr(self.cookiejar, 'save') and self.cookiejar.save()

    def clear_cookie(self, *args, **kwargs):
        """ Clear some cookies. """
        self.cookiejar.clear(*args, **kwargs)

    def urlopen(self, fullurl, data=None, headers=None, timeout=None, proxies=None, encoding=None, errors='ignore', times=1, is_return_content=True, is_return_unicode=True):
        """
            proxies: {'type': 'host'};
            headers: dict objcet or pairs list;
            if is_return_content=False, return a Response objcet, else return content string;
            if is_return_unicode=False, return raw stirng instead of unicode;
            times: 尝试运行 open 方法的次数, 0表示不限制. 当open返回的status code 为 200 时停止.
        """
        self._last_request = None
        if self._last_response:
            self._last_response.close()
        self._last_response = None
        encoding = encoding or self._encoding or 'utf8'
        # accept a URL or a Request object
        if isinstance(fullurl, str):
            self._last_request = urllib.request.Request(fullurl)
        if data:
            if isinstance(data, dict):
                data = urllib.parse.urlencode(data, encoding=encoding, errors=errors)
            if isinstance(data, str):
                data = data.encode(encoding)
            self._last_request.data = data
        if headers:
            headers = isinstance(headers, dict) and headers.items() or headers
            for header in headers:
                self._last_request.add_header(*header)
        if proxies:
            for proxy_type, proxy_host in proxies.items():
                self._last_request.set_proxy(proxy_host, proxy_type)

        temp_times = times or 1
        while temp_times>0:
            try:
                self._last_response = self.open(self._last_request, timeout=timeout)
                if self._last_response.getcode() == 200:
                    if is_return_content:
                        content = self._last_response.read()
                        return is_return_unicode and content.decode(encoding, errors) or content
                    return self._last_response
                print('http status code: %s' % self._last_response.getcode())
            except urllib.request.HTTPError as e:
                if e.code == 404:
                    print('404 http error')
                    return is_return_unicode and '' or b''
                print(e.code, e)
            except Exception as e:
                print('Another Errors', e)
            temp_times = (temp_times-1) if times else 1

    def _check_login(self, check_url, check_data, times=1, encoding=None, errors='ignore'):
        """ Check is login, used for login() method. """
        encoding = encoding or self._encoding or 'utf8'
        return self.urlopen(check_url, times=times, encoding=encoding, errors=errors).find(check_data) >= 0

    def login(self, login_url, login_data, check_url, check_data, use_cookie=True, times=1, encoding=None, errors='ignore'):
        """ General login action. """
        encoding = encoding or self._encoding or 'utf8'
        login_times = 2
        while login_times>0:
            # Empty cookieJar object is False.
            if self.cookiejar is not None:
                if use_cookie and self._check_login(check_url, check_data=check_data, times=times, encoding=encoding, errors=errors):
                    print(login_times == 2 and 'Use cookie login success!' or 'Login success!')
                    self.save_cookie()
                    return True
                elif login_times == 1:
                    print('Login fail!')
                    return False
                login_times -= 1
                self.urlopen(login_url, data=login_data, times=times, encoding=encoding, errors=errors)
                use_cookie = True

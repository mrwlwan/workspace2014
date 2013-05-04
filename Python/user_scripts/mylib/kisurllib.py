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
import mimetypes, itertools

_opener = None

def mix_str(text, encoding='utf8'):
    if isinstance(text, str):
        return text
    elif isinstance(text, unicode):
        return text.encode(encoding)
    else:
        return text.decode(encoding)

def urlopen(url, params=None, data=None, **kwargs):
    """ 简单的HTTP(S)请求. """
    return DefaultOpener().open(url, params=params, data=data, **kwargs)


class MultiPartForm(object):
    """ Accumulate the data to be used when posting a form."""
    def __init__(self):
        self.form_fields = []
        self.files = []
        self.boundary = "PYTHON_BOUNDARY"

    def get_content_type(self):
        return 'multipart/form-data; boundary=%s' % self.boundary

    def add_field(self, name, value):
        """ Add a simple field to the form data."""
        self.form_fields.append((name, str(value)))
        return

    def add_file(self, fieldname, filename, file_obj, mimetype=None):
        """ Add a file to be uploaded."""
        body = file_obj.read()
        if mimetype is None:
            mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        self.files.append((mix_str(fieldname), mix_str(filename), mix_str(mimetype), mix_str(body)))

    def __str__(self):
        """ Return a string representing the form data, including attached files."""
        # Build a list of lists, each containing "lines" of the
        # request.  Each part is separated by a boundary string.
        # Once the list is built, return a string where each
        # line is separated by '\r\n'.
        parts = []
        part_boundary = '--' + self.boundary
        # Add the form fields
        for name, value in self.form_fields:
            parts.extend([
                part_boundary,
                'Content-Disposition: form-data; name="%s"' % name,
                'Content-Type: text/plain; charset=UTF-8',
                '',
                value,
            ])
        # Add the files to upload
        for field_name, filename, content_type, body in self.files:
            parts.extend([
                part_boundary,
                'Content-Disposition: file; name="%s"; filename="%s"' % (field_name, filename),
                'Content-Type: %s' % content_type,
                'Content-Transfer-Encoding: binary',
                '',
                body,
            ])
        parts.extend(['--' + self.boundary + '--', ''])
        return '\r\n'.join(parts)


class DefaultOpener:
    """ 简单的Opener, 主要用于全局的urlopen. """
    def __init__(self):
        global _opener
        if not _opener:
            _opener = build_opener()
        self.opener = _opener

    def open(self, url, params=None, data=None, files=None, method=None, headers={}, proxies={}, timeout=None, **kwargs):
        """ 打开目标链接, 返回一个 HttpResponse对象.

        @url(str/Request): 目标链接.
        @param(str/dict/pairs): query string.
        @data(unicode/bytes/dict/pairs): post data.
        @files(dict): {fieldname: fileobj, ...} or {fieldname: (filename, fileobj), ...}.
        @method(str): GET, POST, PUT, DELETE, UPDATE, ...
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
        if files:
            # multipart/form-data
            form = MultiPartForm()
            if data:
                if isinstance(data, unicode) or isinstance(data, bytes):
                    data_items = parse_qsl(data_items)
                else:
                    data_items = data.items()
                for key, value in data_items:
                    form.add_field(key, value)
            for key in files:
                filename, file_obj = files.get(key) if isinstance(files.get(key), tuple) else (os.path.split(files.get(key).name)[1], files.get(key))
                form.add_file(key, filename, file_obj)
            request.data = str(form).encode('utf8')
            request.add_header('Content-type', form.get_content_type())
        elif data:
            # application/x-www-form-urlencoded
            if isinstance(data, bytes):
                request.data = data
            elif isinstance(data, unicode):
                request.data = data.encode('utf8')
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

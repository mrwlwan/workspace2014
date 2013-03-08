# coding=utf8

import os, sys, json

# 是否SAE部署.
is_sae = 'SERVER_SOFTWARE' in os.environ
# 是否 Python 3.
is_py3 = tuple(sys.version_info)[0] >= 3

if is_py3:
    import urllib.parse as url_parse_module
    import urllib.request as url_request_module
    from urllib.parse import urlparse
    from urllib.parse import urlunparse

    def urlencode(self, params, encoding='utf8', errors='ignore'):
        if not params or isinstance(bytes):
            return params or None
        elif isinstance(dict):
            params = url_parse_module.urlencode(params)
        return params.encode(encoding, errors)
else:
    import urllib as url_parse_module
    import urllib2 as url_request_module
    urlparse = url_request_module.urlparse.urlparse
    urlunparse = url_request_module.urlparse.urlunparse

    def urlencode(self, params, encoding='utf8', errors='ignore'):
        if not params or isinstance(str):
            return params or None
        elif isinstance(dict):
            params = url_parse_module.urlencode(params)
        return params.encode(encoding, errors)


def urlopen(url, params=None, data=None, timeout=None, encoding='utf8', errors='igonre'):
    """ 处理 http request. """
    params = urlencode(params)
    if params:
        urlparse_obj = urlparse(url)._asdict()
        urlparse_obj['query'] = '%s&%s' % (urlparse_obj.get('query'), params)
        url = urlunparse(url_parse.values())
    data = url_parse_module.urlencode(data).encode('utf8')
    return url_request_module.urlopen(url, data, timeout=timeout).read().decode(encoding, errors)


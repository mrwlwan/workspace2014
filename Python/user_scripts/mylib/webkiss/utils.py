# coding=utf8

import os, sys, json

# 是否SAE部署.
is_ae = 'SERVER_SOFTWARE' in os.environ
is_sae = is_ae
is_bae = is_ae
# 是否 Python 3.
is_py3 = tuple(sys.version_info)[0] >= 3

if is_py3:
    import urllib.parse as url_parse_module
    import urllib.request as url_request_module
    from urllib.parse import urlparse
    from urllib.parse import urlunparse

    def urlencode(params, encoding='utf8', errors='ignore'):
        if not params or isinstance(params, bytes):
            return params or None
        elif isinstance(params, dict):
            params = url_parse_module.urlencode(params)
        return params.encode(encoding, errors)
else:
    import urllib as url_parse_module
    import urllib2 as url_request_module
    urlparse = url_request_module.urlparse.urlparse
    urlunparse = url_request_module.urlparse.urlunparse

    def urlencode(params, encoding='utf8', errors='ignore'):
        if not params or isinstance(params, str):
            return params or None
        elif isinstance(params, dict):
            params = url_parse_module.urlencode(params)
        return params.encode(encoding, errors)


def urlopen(url, params=None, data=None, timeout=None, encoding='utf8', errors='igonre'):
    """ 处理 http request. """
    params = params and urlencode(params)
    if params:
        urlparse_obj = urlparse(url)._asdict()
        urlparse_obj['query'] = '%s&%s' % (urlparse_obj.get('query'), params)
        url = urlunparse(url_parse.values())
    data = data and urlencode(data)
    response = url_request_module.urlopen(url, data, timeout=timeout)
    return response.read().decode(encoding, errors)


if is_ae:
    from bae.api import logging
else:
    import logging
    logging.basicConfig(level=logging.DEBUG)


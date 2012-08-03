# coding=utf8

import pytop.topapi as topapi
import requests
import urllib.parse
import datetime, hashlib, json


class TOPBaseClient:
    """ TOP请求客户端的 base class. """
    OPENER = requests.session()
    # 子类须重设request url.
    REQUEST_URL = ''

    def __init__(self, app_key, app_secret):
        self.url = self.REQUEST_URL
        self.app_key = app_key
        self.app_secret = app_secret
        self.opener = self.OPENER

    def urlencode(self, params, encoding='utf8'):
        return urllib.parse.urlencode(params, encoding=encoding, safe=',')

    def create_param(self, top_request, format='json', **kwargs):
        """ 创建调用参数. """
        pass

    def request(self, top_request, method, data=None, format='json', is_transform=False, **kwargs):
        """ @param kwargs(dict): 全部用于URI query 的拼接. """
        if method.lower() not in {'get', 'post'}:
            raise Exception('不支持的请求方法 %s!' % method)
        if not top_request.check_required():
            raise Exception('缺少必须的参数!')
        # 如用请求需要提交数据, 强制将请求方法设置为 post.
        if data and method=='get': method = 'post'
        if method=='get':
            response = self.opener.get(self.url, params=self.create_param(top_request, format=format, **kwargs))
        else:
            response = self.opener.post(self.url, params=self.create_param(top_request, format=format, **kwargs), data=data)
        return top_request.response(response, format=format, is_transform=is_transform)

    def get(self, top_request, format='json', is_transform=False, **kwargs):
        """ GET 请求. request 的便捷方式. """
        return self.request(top_request, method='get', format=format, is_transform=is_transform, **kwargs)

    def post(self, top_request, data=None, format='json', is_transform=False, **kwargs):
        """ POST 请求. request 的便捷方式. """
        return self.request(top_request, method='post', data=data, format=format, is_transform=is_transform, **kwargs)


class TOPClient(TOPBaseClient):
    """ TOP请求客户端(须签名). """
    REQUEST_URL = 'http://gw.api.taobao.com/router/rest'

    def create_sign(self, params):
        """ 创建签名. """
        sign = '%s%s%s' % (self.app_secret, ''.join(('%s%s' % item for item in sorted(params.items()))), self.app_secret)
        return hashlib.md5(sign.encode('utf8')).hexdigest().upper()

    def create_param(self, top_request, format='json', **kwargs):
        """ 创建调用参数. """
        sys_params = {
            'method': top_request.api,
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'format': format,
            'app_key': self.app_key,
            'v': '2.0',
            'sign_method': 'md5',
            'partner_id': 'top-sdk-php-20120526',
        }
        sys_params.update(top_request)
        sys_params.update(kwargs)
        sys_params['sign'] = self.create_sign(sys_params)
        return self.urlencode(sys_params)


class TOPAuthClient(TOPBaseClient):
    """ TOP请求客户端(免签名). """
    REQUEST_URL = 'https://eco.taobao.com/router/rest'

    def __init__(self, app_key, app_secret, access_token=None, redirect_uri=''):
        self.access_token = access_token
        self.redirect_uri = redirect_uri
        super().__init__(app_key, app_secret)

    def set_access_token(self, access_token):
        self.access_token = access_token

    def set_redirect_uri(self, redirect_uri):
        self.redirect_uri = redirect_uri

    def create_param(self, top_request, format='json', **kwargs):
        """ 创建调用参数. """
        sys_params = {
            'method': top_request.api,
            'format': format,
            'v': '2.0',
            'access_token': self.access_token,
        }
        sys_params.update(top_request)
        sys_params.update(kwargs)
        return self.urlencode(sys_params)

    def create_auth_url(self, kind, **kwargs):
        """ 创建显示给用户的授权页面的 url, kind=server时,必须传入redirect_uri. """
        url = 'https://oauth.taobao.com/authorize'
        kinds = {
            'server': {'response_type': 'code'},
            'client': {'response_type': 'token'},
            'native': {'response_type': 'code', 'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob'},
        }
        sys_args = {
            'client_id': self.app_key,
            'redirect_uri': self.redirect_uri,
        }
        sys_args.update(kinds.get(kind.lower()))
        sys_args.update(kwargs)
        return '%s?%s' % (url, self.urlencode(sys_args))


    def create_native_code_url(self, track_id, state='', scope='', view='web'):
        """ 用于 native application 授权方式, 创建包含有授权码(code)页面的url. """
        url = 'https://oauth.taobao.com/authorize'
        sys_args = {
            'client_id': self.app_key,
            'track_id': track_id,
            'response_type': 'code',
            'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
            'state': state,
            'scope': scope,
            'view': view,
            'agreement': 'true',
        }
        return '%s?%s' % (url, self.urlencode(sys_args))


    def fetch_token(self, kind, code, saved=False, **kwargs):
        """ 由授权码获取访问令牌(access_token). Server-side flow 和 Native Application 才需要通过这方式取得访问令牌, 前者必须正确指定  redirect_uri. """
        url = 'https://oauth.taobao.com/token'
        kinds = {
            'server': {'grant_type': 'authorization_code'},
            'native': {'grant_type': 'authorization_code', 'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob'},
        }
        sys_args = {
            'client_id': self.app_key,
            'client_secret': self.app_secret,
            'code': code,
            'redirect_uri': self.redirect_uri,
        }
        sys_args.update(kinds.get(kind.lower()))
        sys_args.update(kwargs)
        params = self.urlencode(sys_args)
        r = self.opener.post(url, params=params)
        json_obj = json.loads(r.text)
        if saved and 'error' not in json_obj: self.access_token = json_obj.get('access_token')
        return json_obj

    def refresh_tocken(self, refresh_token, saved=False, **kwargs):
        url = 'https://oauth.taobao.com/token'
        sys_params = {
            'client_id': self.app_key,
            'client_secret': self.app_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
        }
        sys_params.update(kwargs)
        params = self.urlencode(sys_params)
        r = self.opener.post(url, params=params)
        json_obj = json.loads(r.text)
        if saved and 'error' not in json_obj: self.access_token = json_obj.get('access_token')
        return json_obj

    def logoff(self, redirect_uri='', view='web'):
        url = 'https://oauth.taobao.com/logoff'
        sys_params = {
            'client_id': self.app_key,
            'redirect_uri': redirect_uri or self.redirect_uri,
            'view': view,
        }
        params = self.urlencode(sys_params)
        self.opener.get(url, params=params)



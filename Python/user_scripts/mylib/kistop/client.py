# coding=utf8

import kisurllib
import hashlib, datetime, json

class Client:
    """ TOP 客户端. """
    AUTHORIZE_URL = 'https://oauth.taobao.com/authorize'
    TOKEN_URL = 'https://oauth.taobao.com/token'
    LOGOFF_URL = 'https://oauth.taobao.com/logoff'
    API_REQUEST_URL = 'https://eco.taobao.com/router/rest'

    def __init__(self, app_key, app_secret, redirect_uri=None, access_token=None, debug=False):
        self.app_key = app_key
        self.app_secret = app_secret
        self.access_token = access_token
        self.redirect_uri = redirect_uri

    def urlopen(self, url, params=None, data=None, **kwargs):
        """ HTTP(S) Request. 返回json. """
        response = kisurllib.urlopen(url, params=params, data=data, **kwargs).read().decode('utf8')
        return json.loads(response)

    def gen_sign(self, **kwargs):
        """ 创建签名. """
        sign = '%s%s%s' % (self.app_secret, ''.join(('%s%s' % item for item in sorted(kwargs.items()))), self.app_secret)
        return hashlib.md5(sign.encode('utf8')).hexdigest().upper()

    def gen_authorize_url(self, **kwargs):
        """ 创建"请求用户授权登录"链接. """
        params = {
            'client_id': self.app_key,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
        }
        params.update(kwargs)
        if not params.get('redirect_uri'): raise Exception('未指定redirect_uri')
        return '%s?%s' % (self.AUTHORIZE_URL, kisurllib.urlencode(params))

    def fetch_token(self, code, **kwargs):
        """ 获取Access token. """
        data = {
            'code': code,
            'client_id': self.app_key,
            'client_secret': self.app_secret,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code',
        }
        data.update(kwargs)
        result = self.urlopen(self.TOKEN_URL, data=data)
        self.access_token = result.get('access_token')
        return result

    def refresh_token(self, **kwargs):
        """ 延长Access token时效. """
        data = {
            'client_id': self.app_key,
            'client_secret': self.app_secret,
            'grant_type': 'refresh_token',
            'refresh_token': self.access_token,
        }
        data.update(kwargs)
        return self.urlopen(self.TOKEN_URL, data=data)

    def logoff(self, **kwargs):
        """ 登出. """
        params = {
            'client_id': self.app_key,
            'redirect_uri': redirect_uri,
        }
        params.update(kwargs)
        return self.urlopen(self.LOGOFF_URL, params=params)

    def gen_params(self, api, **kwargs):
        """ 返回 TOP 请求参数. """
        params = {
            'method': api,
            'format': 'json',
            'v': '2.0',
        }
        if self.access_token:
            params['access_token'] = self.access_token
            params.update(kwargs)
        else:
            params.update({
                'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'app_key': self.app_key,
                'sign_method': 'md5',
                'partner_id': 'top-apitools',
            })
            params.update(kwargs)
            params['sign'] = self.gen_sign(**params)
        return params

    def get(self, api, params={}, **kwargs):
        """ HTTP GET 请求. 返回json对象. """
        temp = self.gen_params(api, **params)
        return self.urlopen(self.API_REQUEST_URL, params=temp, **kwargs)

    def post(self, api, params={}, **kwargs):
        """ HTTP POST 请求. 返回json对象. """
        temp = self.gen_params(api, **params)
        return self.urlopen(self.API_REQUEST_URL, data=temp, **kwargs)


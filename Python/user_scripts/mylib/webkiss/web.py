# coding=utf8

from tornado.web import RequestHandler
from webkiss.db import AccountModel, Session

#class Account:
    #""" 用户account类."""
    #def __init__(self, uid):
        #self.uid = uid
        #self._query_obj = None

    #@property
    #def query_obj(self):
        #return self._query_obj or AccountModel.get(uid)

    #def __getattr__(self, name):
        #query_obj = self.query_obj
        #return getattr(query_obj, name)


class BaseHandler(RequestHandler):
    """ Handlers 的基类, 实现了若干实用的方法和属性. """
    models = Session()

    @property
    def is_ajax(self):
        """ 判断是否为 ajax 请求. """
        return bool(self.request.headers.get('X-Requested-With', ''))

    @property
    def is_json(self):
        """ 是否需要返回 json response. 主是是判断请求参数是否指定 json 为 true 值. """
        return bool(int(self.get_argument('json', 0)))

    def get_current_user(self):
        """ 重写. 取得当前用户. 返回 None 或者 Account 对象. """
        uid = self.get_secure_cookie('sessionid')
        #return uid and Account(uid)
        return uid and self.query(AccountModel).get(uid)

    def get_login_url(self):
        """ 重写. 取得登录地址. """
        return 'https://api.weibo.com/oauth2/authorize?redirect_uri=%s&client_id=%s' % (self.settings.get('redirect_uri'), self.settings.get('app_key'))

    def render(self, template_path, ajax_template_path=None, json_obj=None, **kwargs):
        """ 重写 render 方法, 实现对ajax和json的请求处理. """
        if self.is_json:
            return self.write(json_obj)
        elif self.is_ajax:
            template_path = ajax_template_path or template_path
        return super(BaseHandler, self).render(template_path, **kwargs)

    def weibo_request(self, api, **kwargs):
        """ weibo api 请求调用.
        非请求参数有:
            method(http method, 默认值为get)
            is_json(是否返回json对象, 默认值为True)
        source参数根据情况自动赋值.
        """
        api_url = 'https://api.weibo.com/2/%s.json'
        is_json = kwargs.pop('is_json', None) or True
        api_params = {}
        'access_token' not in kwargs and params.update({'source': self.setting.get('app_key')})
        method = kwargs.pop('method', None) or 'get'
        if method == 'get':
            params = api_params
            data = None
        else:
            params = None
            data = api_params
        content = urlopen(api_url % api, params=params, data=data)
        return is_json and json.loads(content) or content
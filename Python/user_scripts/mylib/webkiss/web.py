# coding=utf8
from .utils import is_py3
from .db import AccountModel, Session, default_session
from tornado.web import RequestHandler

if is_py3:
    from collections import UserList
    from itertools import zip_longest
else:
    from UserList import UserList
    from itertools import izip_longest as zip_longest

from collections import Iterable
import json

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
    models = default_session

    @property
    def is_ajax(self):
        """ 判断是否为 ajax 请求. """
        return bool(self.request.headers.get('X-Requested-With', ''))

    @property
    def is_json(self):
        """ 是否需要返回 json response. 主要是判断请求参数是否指定 json 为 true 值. """
        return bool(int(self.get_argument('json', 0)))

    def get_bodyjson(self, default={}, encoding='utf8', errors='strict'):
        """ 返回json对象, 针对 POST Json 请求. """
        body = self.request.body.strip()
        if body:
            return json.loads(body.decode(encoding, errors))
        else:
            return default

    def get_current_user(self):
        """ 重写. 取得当前用户. 返回 None 或者 Account 对象. """
        uid = self.get_secure_cookie('sessionid')
        #return uid and Account(uid)
        return uid and self.models.query(AccountModel).get(uid)

    def get_login_url(self):
        """ 重写. 取得登录地址. """
        return 'https://api.weibo.com/oauth2/authorize?redirect_uri=%s&client_id=%s' % (self.settings.get('redirect_uri'), self.settings.get('app_key'))

    def render_string(self, template, macro=None, **kwargs):
        """ 重写, 以适应jinja2, 支持macro输出. """
        template_path = self.get_template_path()
        if not template_path:
            frame = sys._getframe(0)
            web_file = frame.f_code.co_filename
            while frame.f_code.co_filename == web_file:
                frame = frame.f_back
            template_path = os.path.dirname(frame.f_code.co_filename)
        with RequestHandler._template_loader_lock:
            if template_path not in RequestHandler._template_loaders:
                loader = self.create_template_loader(template_path)
                RequestHandler._template_loaders[template_path] = loader
            else:
                loader = RequestHandler._template_loaders[template_path]
        namespace = self.get_template_namespace()
        if macro:
            return getattr(loader._create_template(template, globals=namespace).module, macro)(**kwargs)
        else:
            t = loader.load(template)
            namespace.update(kwargs)
            return t.generate(**namespace)

    def render2(self, template_path, ajax_template_path=None, json_obj=None, **kwargs):
        """ 快捷方式, 实现对ajax和json的请求处理. """
        if self.is_json:
            return self.write(json_obj)
        elif self.is_ajax:
            template_path = ajax_template_path or template_path
        return self.render(template_path, **kwargs)

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


class Patterns(UserList):
    """ URL映射. 支持include sub app urls. """
    def __init__(self, initlist=[]):
        self.data = []
        for item in initlist:
            if isinstance(item[1], Iterable):
                item = list(item)
                len(item)<3 and item.append({})
                for appitem in item[1]:
                    appitem = list(appitem)
                    len(appitem)<3 and appitem.append({})
                    appkwargs = dict(appitem[2])
                    appkwargs.update(item[2])
                    self.data.append((item[0]+appitem[0].lstrip('^'), appitem[1], appkwargs))
            else:
                self.data.append(item)

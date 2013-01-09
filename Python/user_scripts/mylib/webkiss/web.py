# coding=utf8
from .utils import is_py3
from .db import AccountModel, Session, default_session
import tornado.web

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


class BaseHandler(tornado.web.RequestHandler):
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

    def render2(self, template_path, ajax_template_path=None, json_obj=None, **kwargs):
        """ 重写 render 方法, 实现对ajax和json的请求处理. """
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


try:
    import jinja2

    class JinjaHandler(BaseHandler):
        """ 使用Jinja template. """
        _jinja_env = jinja2.Environment(autoescape=True)

        @classmethod
        def set_template_path(cls, template_path='templates'):
            """ 设置FileSystemLoader的模板目录. """
            cls._jinja_env.loader = jinja2.FileSystemLoader(template_path)

        @classmethod
        def set_loader(cls, loader):
            """ 设置Loader. """
            cls.__env__ = loader

        @classmethod
        def config_env(cls, **kwargs):
            """ 设置jinja Environment 参数. """
            for key, value in kwargs.items():
                setattr(cls._jinja_env, key, value)

        @classmethod
        def add_filters(cls, *args, **kwargs):
            """ 添加Filters. """
            for arg in args:
                cls._jinja_env.filters[arg.__name__] = arg
            cls._jinja_env.filters.update(kwargs)

        @classmethod
        def add_globals(cls, **kwargs):
            """ 添加globals. """
            cls._jinja_env.globals.update(kwargs)

        def get_template(self, template, parent=None, globals=None):
            """ 返回Jinja Template对象. """
            # 传递Tornado默认的Template Namespace.
            namespace = self.get_template_namespace()
            globals and namespace.update(globals)
            return self._jinja_env.get_template(template, parent, namespace)

        def render_string(self, template, parent=None, globals=None, **kwargs):
            """ 返回Template Unicode. """
            return self.get_template(template, parent, globals).render(**kwargs)

        def render(self, template, parent=None, globals=None, **kwargs):
            """ self.render """
            self.write(self.render_string(template, parent, globals, **kwargs))

        def render_macro_string(self, template, macro, parent=None, globals=None, **kwargs):
            return getattr(self.get_template(template, parent, globals).module, macro)(**kwargs)

        def render_macro(self, template, macro, parent=None, globals=None, **kwargs):
            """ self.render """
            self.write(self.render_macro_string(template, macro, parent, globals, **kwargs))
except:
    print('警告: 未安装Jinja2!')


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

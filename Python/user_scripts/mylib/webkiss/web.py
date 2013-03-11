# coding=utf8
from .utils import is_py3
from .db import AccountModel, Session, default_session, as_dict
from tornado.web import RequestHandler
from sqlalchemy.orm.attributes import InstrumentedAttribute
import requests, time, traceback, functools

if is_py3:
    from collections import UserList
    from itertools import zip_longest
else:
    from UserList import UserList
    from itertools import izip_longest as zip_longest

from collections import Iterable
import json


# Decorators
def with_exception(method):
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        try:
            return method(*args, **kwargs)
        except:
            traceback.print_exc()
            return kwargs.get('error') and {'error': '操作失败'} or None
    return wrapper


class BaseHandler(RequestHandler):
    """ Handlers 的基类, 实现了若干实用的方法和属性. """
    opener = requests.Session()

    def initialize(self):
        self.models = Session()

    def on_finish(self):
        self.models.close()

    @property
    def is_ajax(self):
        """ 判断是否为 ajax 请求. """
        return bool(self.request.headers.get('X-Requested-With', ''))

    @property
    def is_json(self):
        """ 是否需要返回 json response. 主要是判断请求参数是否指定 json 为 true 值. """
        return bool(int(self.get_argument('json', 0)))

    def clone_arguments(self, keys=[], extra={}):
        """ 返回指定keys的dict. """
        result = {}
        for key in keys or self.request.arguments:
            result[key] = self.get_argument(key)
        result.update(extra)
        return result

    def remove_arguments(self, *args):
        """ 删除指定的参数. """
        for arg in args:
            if arg in self.request.arguments: del self.request.arguments[arg]

    def get_bodyjson(self, default={}, encoding='utf8', errors='strict'):
        """ 返回json对象, 针对 POST Json 请求. """
        body = self.request.body.strip()
        if body:
            return json.loads(body.decode(encoding, errors))
        else:
            return default

    def get_current_user(self):
        """ 重写. 取得当前用户. 返回 None 或者 Account 对象. """
        uid = self.get_secure_cookie('uid')
        if not uid:
            return None
        uid = uid.decode('utf8')
        account = self.models.query(AccountModel).get(uid)
        if not account or account.is_expiries:
            return None
        return account

    def get_login_url(self):
        """ 重写. 取得登录地址. """
        return 'https://api.weibo.com/oauth2/authorize?client_id=%s&response_type=code&redirect_uri=%s' % (self.settings.get('app_key'), self.settings.get('login_redirect_uri'))

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

    def _create(self, model, kwargs=None, to_dict=False, error=False, commit=True):
        """ 创建."""
        obj = model()
        self.models.add(obj)
        return self._update(model, obj, kwargs, to_dict, error, commit)

    def _retrieve(self, model, obj, to_dict=False, error=False):
        """ 取回. obj可以是对象也可以是主键值. """
        if obj and not isinstance(obj, model):
            obj = self.models.query(model).get(obj)
        if to_dict and obj: obj = as_dict(obj)
        if error:
            return obj and {'error': 0, 'row': obj} or {'error': '未找到对象'}
        else:
            return obj

    @with_exception
    def _update(self, model, obj, kwargs=None, to_dict=False, error=False, commit=True):
        """ 更新. obj可以是对象也可以是主键值. """
        obj = self._retrieve(model, obj)
        if obj:
            if kwargs:
                for key, value in kwargs.items():
                    if hasattr(obj, key) and isinstance(getattr(model, key), InstrumentedAttribute):
                        print(obj, key, value)
                        setattr(obj, key, value)
            else:
                for key in self.request.arguments:
                    if hasattr(obj, key) and isinstance(getattr(model, key), InstrumentedAttribute):
                        setattr(obj, key, self.get_argument(key))
            commit and self.models.commit()
            if to_dict: obj = as_dict(obj)
            return error and {'error': 0, 'row': obj} or obj
        else:
            return error and {'error': '无效对象'} or None

    @with_exception
    def _delete(self, model, obj, error=False, commit=True):
        """ 更新. obj可以是对象也可以是主键值. """
        obj = self._retrieve(model, obj)
        if obj:
            self.models.delete(obj)
            commit and self.models.commit()
            return error and {'error': 0} or True
        else:
            return error and {'error': '删除的对象不存在'} or False


class WeiboLoginHandler(BaseHandler):
    """ 微博登录处理. """
    def get(self):
        code = self.get_argument('code')
        if code:
            url = 'https://api.weibo.com/oauth2/access_token?client_id=%s&client_secret=%s&grant_type=authorization_code&redirect_uri=%s&code=%s' % (self.settings.get('app_key'), self.settings.get('app_secret'), self.settings.get('login_redirect_uri'), code)
            result = self.opener.post(url).json()
            uid = result.get('uid')
            account = self.models.query(AccountModel).get(uid)
            if account:
                account.code, account.access_token = code, result.get('access_token')
            else:
                self.models.add(AccountModel(
                    int(result.get('uid')),
                    code,
                    result.get('access_token'),
                    int(result.get('expires_in'))+time.time()
                ))
            self.models.commit()
            self.set_secure_cookie('uid', result.get('uid'))
        self.redirect(self.request.headers.get('Referer'))


class WeiboHelper:
    """ 微博接口辅助类. 配合BaseHandler使用. """
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

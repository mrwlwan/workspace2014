# coding=utf8

import pytop.topstruct as topstruct
import xml.etree.ElementTree as etree
import json

class TOPRequest(topstruct.TOPDict):
    """ TOP 请求基类. """
    REQUEST = {}
    RESPONSE = {}
    API = None
    is_alert = True # 设置属性时时否即时显示警告信息. 方便于调试.

    def _befor_init(self, *args, **kwargs):
        # 设置默认值
        dict.__init__(self, ((param_name, param.get('default')) for param_name, param in self.REQUEST.items() if 'default' in param))

    def __setitem__(self, param_name, param):
        if param_name not in self.REQUEST:
            self.is_alert and print('警告: 该调用不支持参数 %s' % param_name)
        else:
            param_type = self.REQUEST.get(param_name).get('type')
            param = param_type(param)
            self.is_alert and 'optional' in self.REQUEST.get(param_name) and  param not in self.REQUEST.get(param_name).get('optional') and print('警告: 参数 %s 无效值 %s' % (param_name, param))
        super().__setitem__(param_name, param)

    @property
    def api(self):
        """ 返回当前api名称. """
        return self.API

    def update(self, *args, **kwargs):
        # 子对象则直接调用dict的__init__.
        if args:
            if isinstance(args[0], self.__class__):
                super().__init__(args[0])
                return
            else:
                kwargs = args[0] if isinstance(args[0], dict) else dict(args)
        for k, v in kwargs.items():
            self[k] = v

    def clean(self):
        """ 清除无效的request 参数. 并给出提示. 其中会对args的值进行类型转换.
        @return dict
        """
        for key, value in self.items():
            if key not in self.REQUEST:
                del self[key]
            elif 'optional' in self.REQUEST.get(key) and value not in self.REQUEST.get(key).get('optional'):
                del self[key]

    def check_required(self):
        """ 检查是否缺少必须的参数. """
        result = True
        for param_name, param in self.REQUEST.items():
            if param.get('is_required') and param_name not in self:
                print('缺少参数 %s!' % param_name)
                result = False
        return result

    def response(self, http_response, format='json', is_transform=False):
        """ 返回一个TOPResponse对象.
        @param: response(requests.Response): requests.Response 对象.
        """
        return TOPResponse(http_response, self.RESPONSE, format=format, is_transform=is_transform)


class TOPResponse:
    """ TOP 请求返回类."""

    def __init__(self, http_response, response_format, format, is_transform=False):
        """ @param http_response(requests.Response): requests 返回的 response 对象.
        @param response_format(dict): 数据结构.
        @param format(string): 'json' or 'xml', 用于 self.response
        @param is_transform(bool): 是否将相应的dict对象转换为TOPObject对象.
        """
        self.http_response = http_response
        self.response_format = response_format
        self.format = format.lower()
        self.is_transform = is_transform
        self._response = None
        # 是否成功的 TOP 调用.
        self.is_error = False

    def _transform(self, json_obj):
        if self.is_error:
            return topstruct.TOPError(json_obj)
        result = {}
        for key, value in json_obj.items():
            obj_type = self.response_format.get(key).get('type')
            is_list = self.response_format.get(key).get('is_list')
            if is_list:
                value = (obj_type(item_value) for item_name, item_value in value.items()[0])
            else:
                value = obj_type(value)
        result[key] = value
        return result

    @property
    def text(self):
        """ TOP调用返回的文本字符串. """
        return self.http_response.text

    @property
    def response(self):
        """ 将TOP调用返回的文本转换为相应的对象(dict 或者 xml). """
        if self._response==None:
            if self.format=='json':
                json_obj = json.loads(self.text)
                self.is_error = 'error_response' in json_obj
                json_obj = json_obj.popitem()[1]
                self._response = json_obj if not self.is_transform else self._transform(json_obj)
            elif self.format=='xml':
                self._response = etree.fromstring(self.text)
                self.is_error = self._response.tag == 'error_response'
        return self._response



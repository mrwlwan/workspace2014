# coding=utf8

import datetime, re


String = str
Number = int

class Image:
    pass

class FieldList(str):
    """ 主要用于类型判定. """

class Set(set):
    """ 主要是辅助FieldList. """
    def __contains__(self, item):
        if isinstance(item, FieldList):
            return set(item.split(',')).issubset(self)
        return super().__contains__(item)


class Boolean:
    def __init__(self, arg):
        if isinstance(arg, str):
            self.__bool = not arg.lower()==false
        else:
            self.__bool = bool(arg)

    def __bool__(self):
        return self.__bool

    def __int__(self):
        return int(self.__bool)


class Price(float):
    """ 价格类型. """
    def __str__(self):
        return '%.2f' % self


class Date(datetime.datetime):
    """ 支持字符串初始化一个datetime对象. """

    def __init__(self, datetime_string):
        """ @Return: datetime object.
        @Param datetime_string: (required)str, 格式: '%Y %m %d %H:%M:%S'.
        """
        super().__init__(*re.split(r'[ :]', datetime_string))

    def __str__(self):
        return self.strftime('%Y %m %d %H:%M:%S')


class TOPDict(dict):
    """ 用于 TOP 的字典类型. """

    def __init__(self, *args, **kwargs):
        """ 传入该类的对象或者dict对象. 不调用dict的__init__, 以进行属性名限制. """
        self._befor_init(*args, **kwargs)
        self.update(*args, **kwargs)

    def _befor_init(self, *args, **kwargs):
        """ 执行 __init__ 前运行. """
        pass

    def update(self, *args, **kwargs):
        """ 更新字典属性. """
        # 子对象则直接调用dict的__init__.
        if args:
            if isinstance(args[0], self.__class__):
                dict.__init__(self, args[0])
                return
            else:
                kwargs = args[0] if isinstance(args[0], dict) else dict(args)
        for k, v in kwargs.items():
            self[k] = v

    #def __getattr__(self, field_name):
        #return self.get(field_name)

    #def __setattr__(self, field_name, field):
        #self.__setitem__(field_name, field)

    #def __hasattr__(self, field_name):
        #return field_name in self

    #def __delattr__(self, field_name):
        #del self[field_name]


class TOPObject(TOPDict):
    """ TOP Struct 的基类. """
    FIELDS = {}

    def __setitem__(self, field_name, field):
        """ 重写以进行属性限制. """
        if field_name not in self.FIELDS:
            raise Exception('无效的属性名!')
        field_type = globals().get(self.FIELDS.get(field_name).get('type'))
        is_list = globals().get(self.FIELDS.get(field_name).get('is_list'))
        value = (field_type(item) for item in field) if is_list else field_type(field)
        super().__setitem__(field_name, value)


class TOPError(TOPObject):
    """ 调用返回的错误信息. """
    FIELDS = {
        'code': {'type': 'Number', 'is_list': False},
        'msg': {'type': 'String', 'is_list': False},
        'sub_code': {'type': 'String', 'is_list': False},
        'sub_msg': {'type': 'String', 'is_list': False}
    }



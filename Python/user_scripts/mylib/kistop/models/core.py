# coding=utf8

class TopMetaclass(type):
    """ TOP Metaclass. 主是添加一个类属性: __fieldnames__, 保存TopModel类的TopField属性名"""
    def __new__(cls, name, bases, attrs):
        instance = type.__new__(cls, name, bases, attrs)
        instance.__fieldnames__ = set([attr_name for attr_name, attr_value in attrs.items() if isinstance(attr_value, TopField)])
        return instance


class TopField:
    """ TOP 数据结构属性基类. """
    def __init__(self, basetype, verbose='', default=None, private=False, choices=[]):
        self.type = basetype
        self.default = default
        self.private = private
        self.choices = [isinstance(item, tuple) and item or (item, item) for item in choices]
        self.value = default

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = v.value if isinstance(v, TopField) else self.type(v)


class IntegerField(TopField):
    """ 整数. """
    def __init__(self, **kwargs):
        super().__init__(int, **kwargs)


class PriceField(TopField):
    """ 价钱. """
    def __init__(self, **kwargs):
        super().__init__(float, **kwargs)

    def __str__(self):
        return '%.2f' % self.value


class StringField(TopField):
    """ 字符串. """
    def __init__(self, **kwargs):
        super().__init__(str, **kwargs)


class BoolField(TopField):
    """ 布尔值. """
    FALSE_VALUE = set(['否', '0', 0, False, 'false', 'False'])
    def __init__(self, choices=[(True, '是'), (False, '否')], **kwargs):
        super().__init__(bool, **kwargs)

    @value.setter
    def value(self, v):
        super().value = v not in self.FALSE_VALUE and v or False


class DateField(TopField):
    """ 日期."""
    def __init__(self, **kwargs):
        super().__init__(datetime.datetime, **kwargs)

    @value.setter
    def value(self, v):
        if isinstance(v, TopField):
            v = v.value
        elif isinstance(v, datetime.datetime):
            pass
        elif isinstance(v, tuple):
            v = datetime.datetime(*v)
        elif isinstance(v, str):
            v = datetime.datetime.strptime(v, '%Y-%m-%d %H:%M:%S')
        else:
            raise Exception('赋值类型错误')
        self._value = v


class ListField(TopField):
    """ List 属性. """
    def __init__(self, **kwargs):
        super().__init__(list, **kwargs)


class ModelField(TopField):
    """ Model 属性. """
    def __init__(self, model, **kwargs):
        super().__init__(model, **kwargs)

    @value.setter
    def value(self, v):
        if isinstance(v, TopField):
            v = v.value
        elif isinstance(v, dict):
            v = self.type(**v)
        elif isinstance(v, TopModel):
            pass
        else:
            raise Exception('赋值类型错误')
        self._value = v



######################################################################################
class TopModel(metaclass=TopMetaclass):
    """ TOP 数据结构基类. """
    def __new__(cls):
        instance = super().__new__(cls)
        for attr_name in cls.__fieldnames__:
            field = getattr(cls, attr_name)
            setattr(instance, attr_name, field.value)
        return instance

    def __init__(self, **kwargs):
        for attr_name in self.__fieldnames__:
            if attr_name in kwargs:
                setattr(self, attr_name, kwargs.get(attr_name))

    def as_dict(self):
        """ 浅度转换为dict对象. """
        result = {}
        for attr_name in self.__fieldnames__:
            result[attr_name] = getattr(self, attr_name)
        return result

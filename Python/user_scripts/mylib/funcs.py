# coding=utf8
# 仅适用于 Python 3

from functools import wraps
import re, datetime

def is_class(obj):
    """ check the obj is a class. """
    return isinstance(obj, type) or hasattr(obj, "__bases__")

def coroutine(func):
    """ 用于generator的装饰器. """
    @wraps(func)
    def call(*args, **kwargs):
        g = func(*args, **kwargs)
        next(g)
        return g
    return call

def shortcut_input(items, title='title', input_msg='请选择: ', multi=False):
    """ 便捷的 input. """
    for index, item in enumerate(items, 1):
        print('%s. %s' % (index, item[title]))
    input_index = input(input_msg)
    input_indexes = [int(i)-1 for i in input_index.strip().split()]
    if multi:
        return input_indexes
    return input_indexes[0] if input_indexes else None

def get_cst():
    from opener import Opener
    reg = re.compile(r'nyear=(?P<year>\d+).*?nmonth=(?P<month>\d+).*?nday=(?P<day>\d+).*?nwday=(\d+).*?nhrs=(?P<hour>\d+).*?nmin=(?P<minute>\d+).*?nsec=(?P<second>\d+)', re.S)

    opener = Opener(encoding='utf8')
    content = opener.urlopen('http://www.beijing-time.org/time.asp', times=0)
    search_obj = reg.search(content)
    return search_obj and datetime.datetime(**dict(((item[0], int(item[1])) for item in search_obj.groupdict().items()))) or datetime.datetime.now()



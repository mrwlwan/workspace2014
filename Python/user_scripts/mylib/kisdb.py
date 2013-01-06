# coding=utf8

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, Date
from collections import OrderedDict
import time, os

Base = declarative_base()
Session = sessionmaker()
default_session = Session()

__default_engine__ = None
__register_models__ = {}

# 必须显式调用此方法来设置数据库
def config(dialect, is_debug=False):
    global Session
    global __default_engine__
    global default_session
    __default_engine__ = create_engine(dialect, echo=is_debug)
    Session.configure(bind=__default_engine__)
    default_session.bind = __default_engine__

# 定义完若干models后调用, 创建数据库
def create_all(engine=None):
    global __default_engine__
    if __default_engine__:
        Base.metadata.create_all(engine or __default_engine__)

# 注册 model, 定义完一个model 类后调用.
def register(model, name=None):
    global __register_models__
    __register_models__[name or model.__name__] = model

def get_model(model_name):
    global __register_models__
    return __register_models__.get(model_name)

#############################################################################################
# 便捷函数

# 将行记录Row对象转换为dict
def as_dict(obj):
    return dict([(column.name, getattr(obj, column.name)) for column in obj.__table__columns])

# 返回当前时间
def now():
    now = datetime.datetime.now()
    return datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)

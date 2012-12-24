# coding=utf8

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, Date
from collections import OrderedDict
import time, os

Base = declarative_base()
Session = sessionmaker()
engine = None
session = Session

__register_models__ = {}

# 必须显式调用此方法来设置数据库
def config(dialect, is_debug=False):
    global Session
    global engine
    global session
    engine = create_engine(dialect, echo=is_debug)
    Session.configure(bind=engine)
    session.bind = engine

# 定义完若干models后调用, 创建数据库
def create_all(engine=None):
    global engine
    if engine or engine:
        Base.metadata.create_all(engin or engine)

# 注册 model, 定义完一个model 类后调用.
def register(model):
    global __register_models__
    __register_models__[model.__name__] = model

def get_model(model_name):
    global __register_models__
    return __register_models__.get(model_name)

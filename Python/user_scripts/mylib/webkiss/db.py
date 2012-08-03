# coding=utf8

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, Date
from collections import OrderedDict
import time, os

Base = declarative_base()
Session = sessionmaker()

__default_engine__ = None
__register_models__ = {}

# 必须显式调用此方法来设置数据库
def config(dialect, is_debug=False):
    global Session
    global default_engine
    default_engine = create_engine(dialect, echo=is_debug)
    Session.configure(bind=default_engine)

# 定义完若干models后调用, 创建数据库
def create_all():
    global default_engine
    if default_engine:
        Base.metadata.create_all(default_engine)

# 注册 model, 定义完一个model 类后调用.
def register(model):
    global __register_models__
    __register_models__[model.__name__] = model

def get_model(model_name):
    global __register_models__
    return __register_models__[model_name]


class AccountModel(Base):
    __tablename__ = 'accounts'

    # uid 同时也是 sessionid.
    uid = Column(Integer, primary_key=True)
    # 授权码.
    code = Column(String(128), nullable=False)
    # access_token.
    access_token = Column(String(128))
    # 过期时间.
    expiry = Column(Integer)
    # 首次登录时间.
    insert_date = Column(Date)

    __columns_format__ = OrderedDict([
        ('uid', {'verbose_name': 'UID', 'type': 'hidden',}),
        ('code', {'verbose_name': '授权码', 'type': 'text', 'nullable': False}),
        ('access_token', {'verbose_name': 'Access Token', 'type': 'text',}),
        ('expiry', {'verbose_name': '过期时间', 'type': 'text',}),
        ('insert_date', {'verbose_name': '注册时间', 'type': 'text',}),
    ])

    @property
    def is_expiries(self):
        return self.expiry < time.time()

    def get_token(self):
        """ 尽量用此方法取得access_token. """
        return None if self.is_expiries else self.expiry

register(AccountModel)

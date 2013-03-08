# coding=utf8

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, Date
from collections import OrderedDict
import time, datetime, os

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


class Helper:
    """ 辅助类, 配合Base类使用. """
    def get_verbose(self, name):
        return self._verbose_name.get(name, name)

#############################################################################################
# 便捷函数

# 将行记录Row对象转换为dict
def as_dict(obj):
    return dict([(column.name, getattr(obj, column.name)) for column in obj.__table__.columns])

# 返回当前时间
def now():
    now = datetime.datetime.now()
    return datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)


#############################################################################################


class AccountModel(Base):
    __tablename__ = 'accounts'

    # uid
    uid = Column(Integer, primary_key=True)
    # 授权码.
    code = Column(String(128), nullable=False)
    # access_token.
    _access_token = Column(String(128))
    # 过期时间.
    expiry = Column(Integer)
    # 首次登录时间.
    insert_date = Column(Date, default=datetime.datetime.now)

    _verbose_name = {'uid': 'UID', 'code': '授权码', 'access_token': 'Access Token', 'expiry': '到期时间', 'insert_date': '注册日期'}

    def __init__(self, uid, code, access_token, expiry):
        self.uid, self.code, self.access_token, self.expiry = uid, code, access_token, expiry

    def __repr__(self):
        return self.uid

    @property
    def is_expiries(self):
        return self.expiry < time.time()

    @property
    def access_token(self):
        """ 尽量用此方法取得access_token. """
        return None if self.is_expiries else self._access_token

    @access_token.setter
    def access_token(self, token):
        self._access_token = token

register(AccountModel, 'account')

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

    # id
    id = Column(Integer, primary_key=True)
    # uid
    uid = Column(Integer, nullable=False)
    # 昵称
    nick = Column(String(128))
    # 头像图片链接
    avatar = Column(String(256))
    # 淘宝店ID
    shop_id = Column(String(16))
    # 淘宝店名
    shop_title = Column(String(256))
    # 授权码.
    code = Column(String(128), nullable=False)
    # access_token.
    access_token = Column(String(128))
    # refresh_token
    refresh_token = Column(String(128))
    # 过期时间.
    expiry = Column(Integer)
    # 首次注册时间.
    insert_date = Column(Date, default=datetime.datetime.now)
    # 登录类型
    login_type = Column(String(64), nullable=False)
    # 权限
    permision = Column(Integer, default=2)

    _verbose_name = {'id': 'ID', 'uid': 'UID', 'nick': '昵称', 'code': '授权码', 'access_token': 'Access Token', 'expiry': '到期时间', 'insert_date': '注册日期'}

    def __repr__(self):
        return self.uid

    @property
    def is_expiries(self):
        return self.expiry is not None and self.expiry < time.time()


register(AccountModel, 'account')

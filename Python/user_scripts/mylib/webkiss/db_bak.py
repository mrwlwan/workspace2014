# coding=utf8

import webkiss.utils as utils
from sqlalchemy_shortcuts import Database
from sqlalchemy import Column, Integer, String, Date
import time, os

Base, Operation = Database.generate()

class AccountModel(Base, Operation):
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

    __columns_format__ = {
        'uid': {'verbose_name': 'UID', 'type': 'hidden',},
        'code': {'verbose_name': '授权码', 'type': 'text', 'nullable': False},
        'access_token': {'verbose_name': 'Access Token', 'type': 'text',},
        'expiry': {'verbose_name': '过期时间', 'type': 'text',},
        'insert_date': {'verbose_name': '注册时间', 'type': 'text',},
    }

    @property
    def is_expiries(self):
        return self.expiry < time.time()

    def get_token(self):
        """ 尽量用此方法取得access_token. """
        return None if self.is_expiries else self.expiry

Database.register(AccountModel)

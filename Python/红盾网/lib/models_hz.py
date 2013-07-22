# coding=utf8

from lib.database_sqlalchemy import Database
from sqlalchemy import Table, Column, Integer, Float, String, Text, Boolean, Date, ForeignKey, desc, and_
from sqlalchemy.orm import relationship, backref
import os

Base, DatabaseInterface = Database.generator('register_corps_dg.sqlite', debug=False)

class CorpModel(Base, DatabaseInterface):
    __tablename__ = 'register_corps'

    id  = Column(Integer, primary_key=True)
    # 企业名称
    name = Column(String, nullable=False)
    # 工商登记号
    register_code= Column(String, default='')
    # 登记机关
    register_department = Column(String, default='')
    # 企业性质
    nature = Column(String, default='')
    # 法人
    representative = Column(String, default='')
    # 注册资本
    capital = Column(String, default='')
    # 经营期限
    period = Column(String, default='')
    # 企业状态
    status = Column(String, default='')
    # 成立日期
    establishment_data= Column(Date, default=None)
    # 经营范围
    scope = Column(String, default='')
    # 地址
    addr = Column(String, default='')
    # 信息来源
    info_from = Column(String, default='')
    # 更新日期
    insert_date = Column(Date, default=None)

class InvalidCodeModel(Base, DatabaseInterface):
    __tablename__ = 'invalid_codes'

    id  = Column(Integer, primary_key=True)
    # 当前无效的企业注册码
    register_code = Column(String, unique=True, nullable=False)

class MaxCodeModel(Base, DatabaseInterface):
    __tablename__ = 'max_codes'

    id  = Column(Integer, primary_key=True)
    # 机关代码
    org_code = Column(String, nullable=False)
    # 企业性质号码
    nature_num = Column(Integer, nullable=False)
    # 当前有效的最大流水号
    ord_num = Column(Integer, nullable=False)


Database.create_all()

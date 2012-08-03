# coding=utf8

from database_sqlalchemy import Database
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship, backref

Base, DatabaseInterface = Database.generator('jobinfo_other.sqlite', debug=False)

class CorpModel(Base, DatabaseInterface):
    __tablename__ = 'corps'

    id  = Column(Integer, primary_key=True)
    # 企业名称.
    name = Column(String, nullable=False, index=True)
    # 企业代码.
    corp_code = Column(String, default='')
    # 地址.
    addr = Column(String, default='')
    # 联系人.
    contact_person = Column(String, default='')
    # 电话号码(default='')
    contact_tel_no = Column(String, default='')
    # 单位性质
    nature = Column(String, default='')
    # 行业
    industry = Column(String, default='')
    # 规模
    scale = Column(String, default='')
    # 信息来源
    info_from = Column(String, nullable=False)
    # 更新时间.
    insert_date = Column(Date, nullable=False)

Database.create_all()

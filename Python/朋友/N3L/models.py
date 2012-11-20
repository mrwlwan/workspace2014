# coding=utf8

from database_sqlalchemy import Database
from sqlalchemy import Column, Integer, String, Date
import datetime

Base, DatabaseInterface = Database.generator('n3l.sqlite', debug=False)

class TinfoModel(Base, DatabaseInterface):
    __tablename__ = 'tinfos'

    id  = Column(Integer, primary_key=True)
    fid = Column(Integer, nullable=False)
    tid = Column(Integer, nullable=False, index=True)
    title = Column(String)
    published = Column(Date)
    insertd_date = Column(Date, default = datetime.date.today)

Database.create_all()

# coding=utf8

import os, sys
from sqlalchemy import Table, Column, Integer, Float, String, Text, Boolean, Date, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class DatabaseInterface:
    _DATABASE_URL = 'sqlite:///' + os.path.abspath('.') + '/stock.sqlite'
    engine = create_engine(_DATABASE_URL, echo=True)
    session = sessionmaker(bind=engine)()


class StockModel(Base, DatabaseInterface):
    __tablename__ = 'stocks'

    id = Column(Integer, primary_key=True)
    no = Column(String)
    name = Column(String)
    market = Column(String)
    price = Column(Float)
    is_valid = Column(Boolean)
    corp_info = relationship('CorpInfoModel', backref=backref('stocks'))
    stock_structure = relationship('StockStructureModel', backref=backref('stocks'))

    def __init__(self, no, name, market, price, is_valid):
        self.no = no
        self.name = name
        self.market = market
        self.price = price
        self.is_valid = is_valid

    def __repr__(self):
        return "<StockModel('%s', '%s', '%s', '%f', '%s')>" % (self.no, self.name, self.market, self.price, self.is_valid)


class CorpInfoModel(Base, DatabaseInterface):
    __tablename__ = 'corp_infos'

    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'))
    stock = relationship(StockModel, backref=backref('corp_infos', order_by=id))
    corp_name = Column(String)
    # 工商注册号
    business_registration_no = Column(String)
    # 注册资本
    registered_capital = Column(Float)
    # 成立日期
    established = Column(Date)
    # 经营范围
    business_scope = Column(Text)
    # 发行日期
    publish_date = Column(Date)
    corp_address = Column(String)
    corp_tel = Column(String)

    def __init__(self, stock_id, corp_name="", business_registration_no="", registered_capital="", established="", business_scope="", publish_date="", corp_address="", corp_tel=""):
        self.stock_id = stock_id
        self.corp_name = corp_name
        self.business_registration_no = business_registration_no
        self.registered_capital = registered_capital
        self.established = established
        self.business_scope = business_scope
        self.publish_date = publish_date
        self.corp_address = corp_address
        self.corp_tel = corp_tel

    def __repr__(self):
        return "<CorpInfoModel('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')>" % (self.corp_name, self.business_registration_no, self.registered_capital, self.established, self.business_scope, self.publish_date, self.corp_address, self.corp_tel)


class StockStructureModel(Base, DatabaseInterface):
    __tablename__ = 'stock_structures'

    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'))
    stock = relationship(StockModel, backref=backref('stock_structures', order_by=id))
    # 总股本
    total_stock = Column(Float)
    # 流通A股
    circulate_stock = Column(Float)
    # 流通A股第一股东
    circulate_stock_holder1 = Column(String)
    # 流通A股第一股东持股量
    circulate_stock_holder_volumn1 = Column(Float)
    # 流通A股第一股东持股百份比
    circulate_stock_holder_percence1 = Column(Float)
    # 流通A股第一股东持股性质
    circulate_stock_holder_character1 = Column(String)

    def __init__(self, stock_id, total_stock=0.0, circulate_stock=0.0, circulate_stock_holder1='', circulate_stock_holder_volumn1=0.0, circulate_stock_holder_percence1=0.0, circulate_stock_holder_character1=''):
        self.stock_id = stock_id
        self.total_stock = total_stock
        self.circulate_stock = circulate_stock
        self.circulate_stock_holder1 = circulate_stock_holder1
        self.circulate_stock_holder_volumn1 = circulate_stock_holder_volumn1
        self.circulate_stock_holder_percence1 = circulate_stock_holder_percence1
        self.circulate_stock_holder_character1 = circulate_stock_holder_character1


class BaseInterface(DatabaseInterface):
    # 子类必须重定义 model 属性
    model = object

    ALL = 1
    VALID = 2
    INVALID = 3

    def _commit(self, is_commit=True):
        if is_commit:
            self.session.commit()

    def _process(self, obj):
        return obj

    def format_stock_no(self, stock_no):
        return '%06d' % int(stock_no)

    def _get_all(self, cls, is_valid=1):
        query_obj = self.session.query(cls)
        if is_valid == self.VALID:
            query_obj = query_obj.filter(StockModel.is_valid==True)
        elif is_valid == self.INVALID:
            query_obj = query_obj.filter(StockModel.is_valid==False)
        return query_obj.all()

    def get_all(self, is_valid=1):
        return self._get_all(self.model, is_valid=is_valid)

    def _get(self, stock, cls):
        # 自动判别传入的Stock是StockModel对象还是stock_no
        stock_no = stock
        if isinstance(stock, StockModel):
            stock_no = stock.no
        if cls == StockModel:
            query_obj = self.session.query(cls).filter(StockModel.no==self.format_stock_no(stock_no))
        else:
            query_obj = self.session.query(cls).join(StockModel).filter(StockModel.no==self.format_stock_no(stock_no))
        if query_obj.count():
            return query_obj.first()
        return None

    def get(self, stock):
        return self._get(stock, self.model)

    # 参数 instance 可以是对象,也可以字典,如果是后者,需要提供 定义_process方法处理函数
    def add_one(self, instance, commit=True):
        cls = self.model
        new_instance = None
        if isinstance(instance, cls):
            new_instance = instance
        else:
            temp = self._process(instance)
            new_instance = cls(**temp)
        print(new_instance)
        self.session.add(new_instance)
        self._commit(commit)

# 生成 CSV 格式报表
    def report(self):
        pass


Base.metadata.create_all(StockModel.engine)

# coding=utf8

from database_sqlalchemy import Database
from excel import *
from sqlalchemy import Table, Column, Integer, Float, String, Text, Boolean, Date, ForeignKey, desc, and_
from sqlalchemy.orm import relationship, backref
import datetime

Base, DatabaseInterface = Database.generator('orders.sqlite', debug=True)
excel_date = excel_date()

class Order(Base, DatabaseInterface, Excel2Database):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    # 款号(唯一)
    sn = Column(String, nullable=False, unique=True)
    # 客户款号
    custom_sn = Column(String)
    # 客户
    custom = Column(String, nullable=False)
    # 规格
    spec = Column(String, nullable=False)
    # 加工单价
    fob = Column(Float)
    # 下单日期
    insert_date = Column(Date, nullable=False, default=datetime.date.today())
    # 下单月份
    insert_month = Column(Integer, nullable=False)
    # 备注
    remarks = Column(Text)

    excel_map = {
        'work_book': '测试.xls',
        'sheet': '生产订单',
        'header_rows': 1,
        'footer_rows': 1,
        'field_map': [
            {'field': 'sn', 'map_field': '款号', 'methods': [int, str]},
            {'field': 'custom_sn', 'map_field': '客户款号', 'methods': [int, str]},
            {'field': 'custom', 'map_field': '客户', 'methods': [str]},
            {'field': 'spec', 'map_field': '规格', 'methods': [str]},
            {'field': 'fob', 'map_field': '报价', 'methods': [float]},
            {'field': 'insert_date', 'map_field': '下单日期', 'methods': [excel_date.send]},
            {'field': 'insert_month', 'map_field': '下单月份', 'methods': [int]},
            {'field': 'remarks', 'map_field': '备注', 'methods': [str]},
        ]
    }

class OrderQuantity(Base, DatabaseInterface, Excel2Database):
    __tablename__ = 'order_quantity'

    id = Column(Integer, primary_key=True)
    # 款号
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    order = relationship('Order', backref=backref('order_quantity'))
    # 颜色
    color = Column(String, nullable=False)
    # 规格1的下单数
    spec1_quantity = Column(Integer, default=0)
    # 规格2的下单数
    spec2_quantity = Column(Integer, default=0)
    # 规格3的下单数
    spec3_quantity = Column(Integer, default=0)
    # 规格4的下单数
    spec4_quantity = Column(Integer, default=0)
    # 规格5的下单数
    spec5_quantity = Column(Integer, default=0)
    # 规格6的下单数
    spec6_quantity = Column(Integer, default=0)
    # 规格7的下单数
    spec7_quantity = Column(Integer, default=0)
    # 规格8的下单数
    spec8_quantity = Column(Integer, default=0)
    # 下单数
    quantity = Column(Integer, default=0)
    # 规格1的实裁数
    spec1_real_quantity = Column(Integer, default=0)
    # 规格2的实裁数
    spec2_real_quantity = Column(Integer, default=0)
    # 规格3的实裁数
    spec3_real_quantity = Column(Integer, default=0)
    # 规格4的实裁数
    spec4_real_quantity = Column(Integer, default=0)
    # 规格5的实裁数
    spec5_real_quantity = Column(Integer, default=0)
    # 规格6的实裁数
    spec6_real_quantity = Column(Integer, default=0)
    # 规格7的实裁数
    spec7_real_quantity = Column(Integer, default=0)
    # 规格8的实裁数
    spec8_real_quantity = Column(Integer, default=0)
    # 实裁数
    real_quantity = Column(Integer, default=0)
    # 裁床日期
    insert_date = Column(Date)
    # 备注
    remarks = Column(Text)

    excel_map = {
        'work_book': '测试.xls',
        'sheet': '下单实裁数',
        'header_rows': 1,
        'footer_rows': 0,
        'field_map': [
            {'field': 'color', 'map_field': '颜色', 'methods': [str]},
            {'field': 'order_id', 'map_field': '款号', 'methods': [int], 'foreign_key': Order.sn},
            {'field': 'spec1_quantity', 'map_field': 'C', 'methods': [int]},
            {'field': 'spec2_quantity', 'map_field': 'D', 'methods': [int]},
            {'field': 'spec3_quantity', 'map_field': 'E', 'methods': [int]},
            {'field': 'spec4_quantity', 'map_field': 'F', 'methods': [int]},
            {'field': 'spec5_quantity', 'map_field': 'G', 'methods': [int]},
            {'field': 'spec6_quantity', 'map_field': 'H', 'methods': [int]},
            {'field': 'spec7_quantity', 'map_field': 'I', 'methods': [int]},
            {'field': 'spec8_quantity', 'map_field': 'J', 'methods': [int]},
            {'field': 'quantity', 'map_field': '下单数', 'methods': [int]},
            {'field': 'spec1_real_quantity', 'map_field': 'L', 'methods': [int]},
            {'field': 'spec2_real_quantity', 'map_field': 'M', 'methods': [int]},
            {'field': 'spec3_real_quantity', 'map_field': 'N', 'methods': [int]},
            {'field': 'spec4_real_quantity', 'map_field': 'O', 'methods': [int]},
            {'field': 'spec5_real_quantity', 'map_field': 'P', 'methods': [int]},
            {'field': 'spec6_real_quantity', 'map_field': 'Q', 'methods': [int]},
            {'field': 'spec7_real_quantity', 'map_field': 'R', 'methods': [int]},
            {'field': 'spec8_real_quantity', 'map_field': 'S', 'methods': [int]},
            {'field': 'real_quantity', 'map_field': '实裁数', 'methods': [int]},
            {'field': 'insert_date', 'map_field': '日期', 'methods': [excel_date.send]},
            {'field': 'remarks', 'map_field': '备注', 'methods': [str]},
        ]
    }

class DeliveryEntity(Base, DatabaseInterface, Excel2Database):
    __tablename__ = 'delivery_entities'
    id = Column(Integer, primary_key=True)
    # 日期
    insert_date = Column(Date, nullable=False)
    # 记账月份
    insert_month = Column(Integer, nullable=False)
    # 单号
    no = Column(String)
    # 款号
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    order = relationship('Order', backref=backref('delivery_entities'))
    # 类型
    category = Column(String)
    # 颜色
    color = Column(String, nullable=False)
    # 出货数
    quantity = Column(Integer, nullable=False)
    # 备注
    remarks = Column(Text)

    excel_map = {
        'work_book': '测试.xls',
        'sheet': '出货单',
        'header_rows': 1,
        'footer_rows': 0,
        'field_map': [
            {'field': 'insert_date', 'map_field': '日期', 'methods': [excel_date.send]},
            {'field': 'insert_month', 'map_field': '月份', 'methods': [int]},
            {'field': 'no', 'map_field': '单号', 'methods': [str]},
            {'field': 'order_id', 'map_field': '款号', 'methods': [int], 'foreign_key': Order.sn},
            {'field': 'category', 'map_field': '类型', 'methods': [str]},
            {'field': 'color', 'map_field': '颜色', 'methods': [str]},
            {'field': 'quantity', 'map_field': '出货数', 'methods': [int]},
            {'field': 'remarks', 'map_field': '备注', 'methods': [str]},
        ]
    }

class ReceivingEntity(Base, DatabaseInterface, Excel2Database):
    __tablename__ = 'receiving_entities'
    id = Column(Integer, primary_key=True)
    # 日期
    insert_date = Column(Date, nullable=False)
    # 记账月份
    insert_month = Column(Integer, nullable=False)
    # 款号
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    order = relationship('Order', backref=backref('receiving_entities'))
    # 颜色
    color = Column(String, nullable=False)
    # 规格
    spec = Column(String)
    # 加工厂
    supplier = Column(String)
    # 收货数
    quantity = Column(Integer, nullable=False)
    # 备注
    remarks = Column(Text)

    excel_map = {
        'work_book': '测试.xls',
        'sheet': '收货单',
        'header_rows': 1,
        'footer_rows': 0,
        'field_map': [
            {'field': 'insert_date', 'map_field': '日期', 'methods': [excel_date.send]},
            {'field': 'insert_month', 'map_field': '月份', 'methods': [int]},
            {'field': 'order_id', 'map_field': '款号', 'methods': [int], 'foreign_key': Order.sn},
            {'field': 'color', 'map_field': '颜色', 'methods': [str]},
            {'field': 'spec', 'map_field': '规格', 'methods': [str]},
            {'field': 'supplier', 'map_field': '加工厂', 'methods': [str]},
            {'field': 'quantity', 'map_field': '数量', 'methods': [int]},
            {'field': 'remarks', 'map_field': '备注', 'methods': [str]},
        ]
    }

class ManufactureOrder(Base, DatabaseInterface, Excel2Database):
    __tablename__ = 'manufacture_orders'
    id = Column(Integer, primary_key=True)
    # 款号
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    order = relationship('Order', backref=backref('manufacture_orders'))
    # 颜色
    color = Column(String)
    # 规格
    spec = Column(String)
    # 发货数
    quantity = Column(Integer)
    # 加工厂
    supplier = Column(String)
    # 单价
    fob = Column(Float)
    # 发货日期
    insert_date = Column(Date)
    # 货期
    incoming_date = Column(Date)
    # 收货日期
    receiving_date = Column(Date)
    # 备注
    remarks = Column(Text)

    excel_map = {
        'work_book': '测试.xls',
        'sheet': '生产进度',
        'header_rows': 1,
        'footer_rows': 1,
        'field_map': [
            {'field': 'order_id', 'map_field': '款号', 'methods': [int], 'foreign_key': Order.sn},
            {'field': 'color', 'map_field': '颜色', 'methods': [str]},
            {'field': 'spec', 'map_field': '规格', 'methods': [str]},
            {'field': 'quantity', 'map_field': '发货数', 'methods': [int]},
            {'field': 'supplier', 'map_field': '加工厂', 'methods': [str]},
            {'field': 'fob', 'map_field': '生产\n单价', 'methods': [float]},
            {'field': 'insert_date', 'map_field': '发货\n日期', 'methods': [excel_date.send]},
            {'field': 'incoming_date', 'map_field': '收货\n期限', 'methods': [excel_date.send]},
            {'field': 'receiving_date', 'map_field': '收货\n日期', 'methods': [excel_date.send]},
            {'field': 'remarks', 'map_field': '备注', 'methods': [str]},
        ]
    }

class BOM(Base, DatabaseInterface, Excel2Database):
    __tablename__ = 'boms'
    id = Column(Integer, primary_key=True)
    # 款号
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    order = relationship('Order', backref=backref('boms'))
    # 类型
    category = Column(String)
    # 名称
    name = Column(String)
    # 单位
    unit = Column(String)
    # 应收数
    quantity = Column(Integer)
    # 实收数
    real_quantity = Column(Integer)
    # 日期
    insert_date = Column(Date)
    # 备注
    remarks = Column(Text)

    excel_map = {
        'work_book': '测试.xls',
        'sheet': '物料清单',
        'header_rows': 1,
        'footer_rows': 1,
        'field_map': [
            {'field': 'order_id', 'map_field': '款号', 'methods': [int], 'foreign_key': Order.sn},
            {'field': 'category', 'map_field': '类型', 'methods': [str]},
            {'field': 'name', 'map_field': '名称', 'methods': [str]},
            {'field': 'unit', 'map_field': '单位', 'methods': [str]},
            {'field': 'quantity', 'map_field': '应收数', 'methods': [int]},
            {'field': 'real_quantity', 'map_field': '实收数', 'methods': [int]},
            {'field': 'insert_date', 'map_field': '日期', 'methods': [excel_date.send]},
            {'field': 'remarks', 'map_field': '备注', 'methods': [str]},
        ]
    }

Database.create_all()

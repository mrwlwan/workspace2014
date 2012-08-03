# coding=utf8

from sqlalchemy import create_engine, and_, desc, asc
#from sqlalchemy import Table, Column, Integer, Float, String, Text, Boolean, Date, ForeignKey,  desc
#from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os, csv, datetime, re

Base = declarative_base()

class Database:
    """ 调用 generator 生成的DatabaseInterface 类将会追加到 __Generators__ 中. """
    __Generators__ = []

    @classmethod
    def create_all(cls):
        """ 调用此方法以建立所有的数据库和表. Model 定义完成后须显式调用此方法. """
        for Generator in cls.__Generators__:
            Generator.Base.metadata.create_all(Generator.engine)

    @classmethod
    def generator(cls, database_url=None, debug=False):
        """ 返回一个全新的 Base 类和与之绑定的 DatabaseInterface 类. """
        class DatabaseInterface:
            """ Model 可继承的接口. """
            Base = declarative_base()
            DATABASE_URL = 'sqlite:///%s' % (database_url or os.path.join(os.getcwd(), 'database.sqlite'))
            engine = create_engine(DATABASE_URL, echo=debug)
            session = sessionmaker(bind=engine)()

            @staticmethod
            #def _str2date(date_str, default_year=None):
            def _str2date(date_str, date_reg=r'(?P<year>\d+)-(?P<month>\d+)-(?P<day>\d+)'):
                """ 便捷方法, 将字符串转换成日期. 对于省略年份的, 自动添加当前年份. """
                if not date_str:
                    return None
                #items = date_str.split('-')
                #if len(items)<2:
                    #return None
                #if len(items)<3:
                    #items.insert(0, default_year or datetime.datetime.now().year)
                #return datetime.date(int(items[0]), int(items[1]), int(items[2]))
                search_obj = re.search(date_reg, date_str)
                try:
                    if search_obj:
                        date_dict = search_obj.groupdict()
                        for key in date_dict:
                            date_dict[key] = int(date_dict[key])
                        return datetime.date(**date_dict)
                except Exception as e:
                    print(e)
                return None

            @classmethod
            def _process(self, obj):
                """ 子类继承方法, 添加记录前进行的处理. """
                return obj

            @classmethod
            def _get_all(cls):
                """ order_by 为排序的字段名. """
                return cls.session.query(cls)

            @classmethod
            def sort(cls, query_obj, order_by=None, order='desc'):
                if order_by and hasattr(cls, order_by):
                    return query_obj.order_by(globals()[order](getattr(cls, order_by)))
                return query_obj

            @classmethod
            def commit(cls, is_commit=True):
                """ session 的 commit 方法. """
                if is_commit:
                    cls.session.commit()

            @classmethod
            def rollback(cls):
                """ session 的 rollback 方法. """
                cls.session.rollback()

            @classmethod
            def get_all(cls, is_list=False):
                """ 返回所有记录; order_by 为排序的字段名. """
                query_obj = cls._get_all()
                if is_list:
                    return query_obj.all()
                return query_obj

            @classmethod
            def get(cls, id):
                return cls.session.query(cls).filter(cls.id == id).first()

            @classmethod
            def filter(cls, *args):
                """ 返回 Query 对象. """
                #return self.session.query(self.model).filter(and_(*args)).all()
                return cls.session.query(cls).filter(and_(*args))

            @classmethod
            def filter_by(cls, **kargs):
                """ 返回 Query 对象. """
                return cls.session.query(cls).filter_by(**kargs)

            @classmethod
            def exists(cls, **kargs):
                """ 判断记录是否存在. """
                return bool(cls.filter(**kargs).first())

            @classmethod
            def exists_by(cls, **kargs):
                """ 判断记录是否存在. """
                return bool(cls.filter_by(**kargs).first())

            @classmethod
            def delete(cls, *args, is_commit=True):
                """ 删除指定记录. """
                query_obj = cls.filter(*args)
                query_obj and query_obj.delete()
                cls.commit(is_commit)

            @classmethod
            def delete_by(cls, is_commit=True, **kargs):
                """ 删除指定记录. """
                query_obj = cls.filter_by(**kargs)
                query_obj and query_obj.delete()
                cls.commit(is_commit)

            @classmethod
            def delete_by(cls, obj, is_commit=True):
                """ 删除记录对象. """
                cls.session.delete(obj)
                cls.commit(is_commit)

            @classmethod
            def add(cls, obj, is_commit=True):
                """ 参数 obj 可以是对象,也可以字典,如果是后者,会用_process方法对字典进行预处理. """
                new_obj = None
                if isinstance(obj, cls):
                    new_obj = obj
                else:
                    new_obj = cls(**cls._process(obj))
                cls.session.add(new_obj)
                cls.commit(is_commit)

            @classmethod
            def report(cls, filename, fields, rows, encoder=None):
                """ 参数 fields 格式: [(title, attr)...]. """
                titles, attrs = [], []
                for field in fields:
                    titles.append(field[0])
                    attrs.append(field[1])
                with open(filename, 'w', encoding=encoder,errors='ignore') as f:
                    r = csv.writer(f, delimiter=',', lineterminator='\n')
                    r.writerow(titles)
                    for row in rows:
                        r.writerow([getattr(row, attr) for attr in attrs])
                    f.close()
                print('Done!')

            def merge_csv(self, filename, fields, search_field, ignore_fields=[], encoder=None):
                with open(filename, encoding=encoder, errors='ignore') as f:
                    print('Reading %s ...' % filename)
                    r = csv.DictReader(f, fields, delimiter=',', lineterminator='\n')
                    i = 0
                    for row in r:
                        if i:
                            print(row[search_field])
                            exits_obj = self.filter(getattr(self.model, search_field).like('%%%s%%' % row[search_field]))
                            if not exits_obj.count():
                                for ignore_field in ignore_fields:
                                    del row[ignore_field]
                                print(row)
                                self.add_one(row, is_commit=False)
                                print('Update')
                            else:
                                print('Exits')
                        i = 1
                    self.commit()

            @classmethod
            def exists_table(cls):
                return cls.__table__.exists(cls.engine)

            @classmethod
            def drop_table(cls):
                cls.exists_table() and cls.__table__.drop(cls.engine)

            @classmethod
            def create_table(cls):
                cls.exists_table() or cls.__table__.create(cls.engine)

            @classmethod
            def clear_table(cls):
                if cls.exists_table():
                    cls.drop_table()
                    cls.create_table()

            def to_dict(self):
                """ 将返回的记录转换为 dict. """
                return self.__dict__


        cls.__Generators__.append(DatabaseInterface)
        return DatabaseInterface.Base, DatabaseInterface


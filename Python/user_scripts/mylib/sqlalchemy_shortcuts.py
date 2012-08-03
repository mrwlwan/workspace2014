# coding=utf8

from sqlalchemy import create_engine, and_, desc, asc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os, csv, datetime, re


class SimpleProperties(dict):
    """ 简单的属性存储对象. """
    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        del self[name]


class Database:
    """ 调用 generate 生成的DatabaseInterface 类将会追加到 __Generators__ 中. """
    Base = declarative_base()
    __engines__ = {}
    __models__ = SimpleProperties()

    @classmethod
    def create_all(cls):
        """ 调用此方法以建立所有的数据库和表. Model 定义完成后须显式调用此方法. """
        for engine in cls.__engines__.values():
            cls.Base.metadata.create_all(engine)

    @classmethod
    def generate(cls, dialect=None, is_debug=False):
        """ 返回一个全新的 Base 类和与之绑定的 DatabaseInterface 类. """
        class Operation:
            """ Model 可继承的操作接口. """
            #DATABASE_URL = 'sqlite:///%s' % database_url
            @classmethod
            def initial(cls, dialect, is_debug=False):
                cls.dialect = dialect
                cls.engine = Database.__engines__.get(dialect)
                if not cls.engine:
                    cls.engine = create_engine(dialect, echo=is_debug)
                    Database.__engines__[dialect] = cls.engine
                cls.session = sessionmaker(bind=cls.engine)()

            @staticmethod
            def _str2date(date_str, date_reg=r'(?P<year>\d+)-(?P<month>\d+)-(?P<day>\d+)'):
                """ 便捷方法, 将字符串转换成日期. 对于省略年份的, 自动添加当前年份. """
                if not date_str:
                    return None
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
            def _process(cls, obj):
                """ 子类继承方法, 添加记录前进行的处理. """
                return obj

            @classmethod
            def _get_all(cls):
                """ order_by 为排序的字段名. """
                return cls.session.query(cls)

            @classmethod
            def query(cls, *args, **kwargs):
                return cls.session.query(*args, **kwargs)

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
            def delete(cls, *args):
                """ 删除指定记录. """
                query_obj = cls.filter(*args)
                query_obj and query_obj.delete()
                #cls.commit(is_commit)

            @classmethod
            def delete_by(cls, **kargs):
                """ 删除指定记录. """
                query_obj = cls.filter_by(**kargs)
                query_obj and query_obj.delete()
                #cls.commit(is_commit)

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
                """ 参数 fields 格式: [(title, attr)...]. 参数 attr 可以为字符串 format, 将取胜字符串高级格式化{field_name}. """
                titles, value_formats = [], []
                reg = re.compile(r'{.+}')
                for field in fields:
                    titles.append(field[0])
                    value_formats.append(reg.search(field[1]) and field[1] or '{%s}' % field[1])
                print(value_formats)
                with open(filename, 'w', encoding=encoder,errors='ignore') as f:
                    r = csv.writer(f, delimiter=',', lineterminator='\n')
                    r.writerow(titles)
                    for row in rows:
                        r.writerow([value_format.format(**row.to_dict()) for value_format in value_formats])
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

            def remove(self, is_commit=True):
                """ 删除当前记录. """
                self.session.delete(self)
                self.commit(is_commit)

        dialect and Operation.initial(dialect, is_debug)
        return cls.Base, Operation

    @classmethod
    def register(cls, model, verbose_name=None):
        verbose_name = verbose_name or model.__name__
        cls.__models__['verbose_name'] = model

    @classmethod
    def get_models(cls):
        return cls.__models__


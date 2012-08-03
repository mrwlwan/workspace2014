# coding=utf8

from tornado.template import Template, Loader
from copy import deepcopy
import os.path

def get_dict(dict_obj, key, default=''):
    """ dict 的get方法的快捷方式. """
    return dict_obj.get(key, default)

def get_dict_space(dict_obj, key, prefix_text='', subfix_text='', default=''):
    if prefix_text or subfix_text:
        return '{0} {1} {2}'.format(prefix_text, get_dict(dict_obj, key, default), subfix_text).strip()
    return get_dict(dict_obj, key, default)

def get_dict_left_space(dict_obj, key, prefix_text='', subfix_text='', default=''):
    result = get_dict_space(dict_obj, key, prefix_text, subfix_text, default)
    return result and ' {0}'.format(result) or result


class BaseView:
    default_loader = default_loader = Loader(os.path.join(os.path.split(os.path.abspath(__file__))[0], 'templates'))

    def __init__(self, loader=None):
        self.loader = Loader(loader) if isinstance(loader, str) else loader or BaseView.default_loader

    def merge_format(self, column_format1, column_format2={}):
        """ 合并单行的column格式(不带column名). 如果没有进行合并, 返回column_format, 否则返回一个全新的dict. """
        if not column_format2:
            return column_format1
        return dict(column_format1, **column_format2)

    def generate(self, template, **kwargs):
        return self.loader.load(template).generate(**kwargs)



class ColumnView(BaseView):
    def __init__(self, column_name, column_format, column_value=None, loader=None):
        super(ColumnView, self).__init__(loader)
        self.column_name = column_name
        self.column_value = column_value
        self.column_format = column_format
        print(self.column_format)

    def _widget(self, template, column_format={}):
        column_format = self.merge_format(self.column_format, column_format)
        print(column_format)
        return self.generate(template, column_name=self.column_name, column_value=self.column_value, column_format=column_format)

    def input(self, column_format={}):
        return self._widget('form/input.html', column_format=column_format)

    def select(self, column_format={}):
        return self._widget('form/select.html', column_format=column_format)

    def textarea(self, column_format={}):
        return self._widget('form/textarea.html', column_format=column_format)

    def tr(self, column_format={}):
        return self._widget('form/tr.html', column_format=column_format)

    def __str__(self):
        return getattr(self, self.column_format.get('type'), getattr(self, 'tr'))


class ModelView(BaseView):
    def __init__(self, model, global_format={}, columns_format={}, loader=None):
        """ 额外的columns格式, 覆盖model的columns_format, 格式:
            columns_format = {
                field_name: {'verbose_name': verbose name, 'hide': True/False, 'type': input type, 'class': css class, 'attrs': other attr}
                ...
            }
            columns_format 会覆盖global_format.
            如果须要指定输出form类型, 可以设定global_format, {'form_type': 'inline/horizontal'}.
        """
        super(ModelView, self).__init__(loader)
        self.model = model
        self.columns_format = self.merge_columns_format(model.__columns_format__, columns_format, global_format)

    def merge_columns_format(self, columns_format1, columns_format2={}, global_format={}):
        """ 合并多行的columns格式(带column名). """
        if not (columns_format2 or global_format):
            return columns_format1
        columns_format = deepcopy(columns_format1)
        if global_format:
            for key in columns_format:
                columns_format[key].update(global_format)
        if columns_format2:
            for key in columns_format2:
                columns_format[key].update(columns_format2[key])
        return columns_format

    def column(self, column_name, column_format={}):
        if type(self.model).__name__ == 'type':
            return ColumnView(column, column_format=self.merge_format(self.columns_format.get(column_name), column_name), column_format, loader=self.loader)
        return ColumnView(column_name, self.merge_format(self.columns_format.get('column_name'), column_format), getattr(self.model, column_name), self.loader)

    def columns(self, columns=[], exclude=[]):
        """ columns: 按顺序返回ColumnView, list元素是column名).
        如果columns 为空, 则返回model全部columns, exclude设定的除外.
        """
        return (self.column(column) for column in (columns or self.columns_format) if column not in exclude)

    def form(self, action, method='post', attrs='', columns=[]):
        return self.generate('form/form.html', action=action, method=method, form_format={}, columns=self.columns(columns))

    def form_start(self):
        pass

    def form_end(self):
        pass

    def table(self):
        if type(self.model).__name__ == 'type':
            return self.generate('table.html', )
        return ''

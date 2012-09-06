# coding=utf8

from tornado.template import Template, Loader
from tornado.escape import native_str
from copy import deepcopy
import os.path

def t(value, default=''):
    """ 将value转换为字符串, None, False 值转换为 default 值. """
    return default if (value==None or value==False) else str(value)

def join(*args):
    """ 用空格连接多个字符串. 过滤元素值为None或者空字符串"""
    return ' '.join([arg for arg in args if t(arg)!=''])

def fill(value, prefix=' ', subfix=''):
    """ 如果value非空字符串, 在其前后填充空格. """
    value = t(value)
    if value!='':
        return '%s%s%s' % (prefix, value, subfix)
    return ''

def attr(attr_name, arg):
    if arg:
        return ' %s="%s"' % (attr_name, arg)
    return ''


#####################################################################################
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
    __input_types__ = set(['text', 'file', 'hidden', 'password'])
    __check_types__ = set(['checkbox', 'radio'])

    def __init__(self, column_name, column_format, column_value=None, loader=None):
        #super(ColumnView, self).__init__(loader)
        BaseView.__init__(self, loader)
        self.column_name = column_name
        self.column_value = column_value
        self.column_format = column_format

    def _widget(self, template, column_format={}):
        column_format = self.merge_format(self.column_format, column_format)
        return self.generate(template, column_name=self.column_name, column_value=self.column_value, column_format=column_format)

    def input(self, column_format={}):
        return self._widget('form/input.html', column_format=column_format)

    def check(self, column_format={}):
        return self._widget('form/check.html', column_format=column_format)

    def select(self, column_format={}):
        return self._widget('form/select.html', column_format=column_format)

    def textarea(self, column_format={}):
        return self._widget('form/textarea.html', column_format=column_format)

    def tr(self, column_format={}):
        return self._widget('form/tr.html', column_format=column_format)

    def get_widget(self, widget_type):
        if widget_type in self.__input_types__:
            return native_str(self.input())
        elif widget_type in self.__check_types__:
            return native_str(self.check())
        return native_str(getattr(self, widget_type)())

    def __str__(self):
        widget_type = self.column_format.get('type')
        return self.get_widget(widget_type)


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
        #super(ModelView, self).__init__(loader)
        BaseView.__init__(self, loader)
        self.model = model
        self.global_format = global_format
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
                if key in columns_format:
                    columns_format[key].update(columns_format2[key])
                else:
                    columns_format[key] = columns_format2[key]
                    columns_format[key].update(global_format)
        return columns_format

    def column(self, column_name, column_format={}):
        if isinstance(self.model, type):
            column_format=self.merge_format(self.columns_format.get(column_name), column_format)
            return ColumnView(
                column_name,
                column_format=self.merge_format(self.columns_format.get(column_name), column_format),
                column_value=column_format.get('default'),
                loader=self.loader
            )
        return ColumnView(column_name, self.merge_format(self.columns_format.get(column_name), column_format), getattr(self.model, column_name), self.loader)

    def columns(self, columns=[], exclude=[]):
        """ columns: 按顺序返回ColumnView, list元素是column名).
        如果columns 为空, 则返回model全部columns, exclude设定的除外.
        """
        return (self.column(column) for column in (columns or self.columns_format) if column not in exclude)

    def form(self, action, xsrf_form_html, method='post', form_class='', attrs='', default_btns=[], btns=[], columns=[], exclude=[]):
        form_class = join('form-%s' % self.global_format.get('form_type', 'form-vertical'), form_class)
        return self.generate('form/form.html', action=action, xsrf_form_html=xsrf_form_html, method=method.upper(), form_class=form_class, attrs=attrs, default_btns=default_btns, btns=btns, columns=self.columns(columns, exclude))

    def table(self, table_class='', attrs='', caption=None, headers=[], columns=[], exclude=[]):
        table_class = join('table-%s' % self.global_format.get('table_type'), table_class)
        return self.generate('form/table.html', table_class=table_class, attrs=attrs,  caption=caption, headers=headers, columns=self.columns(columns, exclude))


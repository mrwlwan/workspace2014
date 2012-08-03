# coding=utf8

from funcs import coroutine
import xlrd3 as xlrd
import os.path
import re, datetime

@coroutine
def excel_date():
    __date = datetime.date(1899,12,31).toordinal()-1
    date = 0
    while 1:
        date = (yield datetime.date.fromordinal(__date+int(date)))



def get_excel_data(file_path, sheet_name, fields=[], header_rows=1, footer_rows=0):
    book = xlrd.open_workbook(file_path)
    sheet = book.sheet_by_name(sheet_name)
    header_map = {}
    if header_rows>0:
        header_row = sheet.row_values(header_rows-1)
        for index in range(len(header_row)):
            header_map[header_row[index].strip()] = index
    # 转换目标字段集
    target_fields = []
    reg = re.compile(r'^([a-z]?)([a-z])$')
    for field in fields:
        field = field.strip()
        match_obj = reg.match(field.lower())
        if match_obj:
            col1, col2 = match_obj.groups()
            target_fields.append((col1 and (ord(col1)-96)*26 or 0) + ord(col2)-97)
        else:
            target_fields.append(header_map[field])
    for row_index in range(header_rows, sheet.nrows-footer_rows):
        yield [sheet.cell_value(row_index, col_index) for col_index in target_fields]

class Excel2Database():
    excel_map = {
        #'work_book': '测试.xls',
        #'sheet': '生产订单',
        #'header_rows': 1,
        #'footer_rows': 1,
        #'field_map': [
            #{'field': 'sn', 'map_field': '款号', 'methods': [int, str]},
            #{'field': 'custom_sn', 'map_field': '客户款号', 'methods': [int, str]},
            #{'field': 'custom', 'map_field': '客户', 'methods': [str]},
            #{'field': 'spec', 'map_field': '规格', 'methods': [str]},
            #{'field': 'fob', 'map_field': '报价', 'methods': [float]},
            #{'field': 'insert_date', 'map_field': '下单日期', 'methods': [excel_date().send]},
            #{'field': 'insert_month', 'map_field': '下单月份', 'methods': [int]}
        #]
    }

    @classmethod
    def _process_data(cls, data, methods):
        if isinstance(data, str) and not data.strip():
            return None
        for method in methods:
            data = method(data)
        return data

    @classmethod
    def transform(cls, is_initial=True, is_commit=True):
        if not cls.excel_map:
            return
        is_initial and cls.clear_table()
        excel_map = cls.excel_map
        fields = [field['field'] for field in excel_map['field_map']]
        excel_fields = [field['map_field'] for field in excel_map['field_map']]
        for excel_data in get_excel_data(excel_map['work_book'], excel_map['sheet'], excel_fields, excel_map['header_rows'], excel_map['footer_rows']):
            data = {}
            for index in range(len(fields)):
                field = fields[index]
                value = cls._process_data(excel_data[index], excel_map['field_map'][index]['methods'])

                if 'foreign_key' in excel_map['field_map'][index]:
                    foreign_key = excel_map['field_map'][index]['foreign_key']
                    value = foreign_key.class_.filter(foreign_key==value).one().id
                data[field] = value
            cls.add(data, is_commit=False)
        cls.commit()

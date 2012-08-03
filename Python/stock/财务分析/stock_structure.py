# coding=utf8

from mylib import *
from config import *
from models import BaseInterface, StockModel, CorpInfoModel, StockStructureModel
import re, datetime, csv

class StockStructure(BaseInterface):
    model = StockStructureModel

    def __init__(self):
        self.opener = Opener(has_cookie=True)
        # 股本结构抓取页面
        self.stock_structure_url = STOCK_STRUCTURE_URL
        # 流通股东抓取页面
        self.circulate_stock_holder_url = CIRCULATE_STOCK_HOLDER_URL
        self.stock_structure_reg = re.compile('·总股本<a.*?历史记录\)</a></td><td>(?P<total_stock>.*?)万股.*?流通A股<a.*?历史记录\)</a></td><td>(?P<circulate_stock>.*?)万股', re.S)
        self.circulate_stock_holder_reg = re.compile('<td><div align="center">1</div></td>.*?&stockholderid.*?<td><div align="center">(?P<circulate_stock_holder1>.*?)</div>.*?<td><div align="center">(?P<circulate_stock_holder_volumn1>.*?)</div>.*?<td><div align="center">(?P<circulate_stock_holder_percence1>.*?)</div>.*?<td><div align="center">(?P<circulate_stock_holder_character1>.*?)</div>', re.S)
        self.encode = WEB_CHARSET

    def _process(self, stock_structure):
        for key in stock_structure:
            stock_structure[key] = re.sub('<strong>|</strong>|<br>|</br>|&nbsp;|\t|\n', '', str(stock_structure[key]), re.S)
        for key in ('total_stock', 'circulate_stock', 'circulate_stock_holder_volumn1', 'circulate_stock_holder_percence1'):
            if key in stock_structure and stock_structure[key]:
                stock_structure[key] = float(stock_structure[key])
        if 'circulate_stock_holder_volumn1' in stock_structure:
            stock_structure['circulate_stock_holder_volumn1'] = stock_structure['circulate_stock_holder_volumn1'] / 10000
        return stock_structure

    def _fetch(self, url, reg):
        html = self.opener.open(url, encode=self.encode)
        search_obj = re.search(reg, html)
        return search_obj and search_obj.groupdict() or {}

    def fetch(self, stock):
        stock_obj = stock
        if not isinstance(stock, StockModel):
            stock_obj = super()._get(stock, StockModel)
        stock_structure = self._fetch(self.stock_structure_url % stock_obj.no, self.stock_structure_reg)
        stock_structure.update(self._fetch(self.circulate_stock_holder_url % stock_obj.no, self.circulate_stock_holder_reg))
        stock_structure['stock_id'] = stock_obj.id
        return stock_structure

    # 初始化,自动跳过已经存在的条目
    def initial(self):
        is_commit = 0
        for stock in super()._get_all(StockModel, is_valid=self.VALID):
            print(stock.no)
            if self.get(stock):
                print('跳过')
                continue
            stock_structure = self.fetch(stock)
            self.add_one(stock_structure, commit=False)
            is_commit += 1
            if is_commit >= 5:
                self._commit()
                is_commit = 0
        self._commit()

    def report(self):
        f = open('stock_structure_report.csv', 'w')
        r = csv.writer(f, delimiter=',', lineterminator='\n')
        temp = [('代码','名称','收盘价','总股本','流通A股','第一流通股东','第一流通股东股本','百份比','股东性质')]
        for stock, stock_structure in self.session.query(StockModel, StockStructureModel).filter(StockModel.id == StockStructureModel.stock_id).all():
            temp.append((
                stock.no,
                stock.name,
                stock.price,
                stock_structure.total_stock,
                stock_structure.circulate_stock,
                stock_structure.circulate_stock_holder1,
                stock_structure.circulate_stock_holder_volumn1,
                stock_structure.circulate_stock_holder_percence1,
                stock_structure.circulate_stock_holder_character1
            ))
        r.writerows(temp)
        f.close()
        print('Done')


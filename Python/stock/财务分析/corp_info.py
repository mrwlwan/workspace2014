# coding=utf8

from mylib import *
from config import *
from models import BaseInterface, StockModel, CorpInfoModel
import re, datetime, csv

class CorpInfo(BaseInterface):
    model = CorpInfoModel

    def __init__(self):
        self.opener = Opener(has_cookie=True)
        # 公司简介抓取页面地址
        self.corp_info_url = CORP_INFO_URL
        self.reg = re.compile('<td>公司名称：(?P<corp_name>.*?)</td>.*?<td>工商登记号：(?P<business_registration_no>.*?)</td>.*?<td>注册地址：(?P<corp_address>.*?)</td>.*?RegisterMoney=(?P<registered_capital>.*?)".*?<td>联系电话：(?P<corp_tel>.*?)</td>.*?EstablishDate=(?P<established>.*?)".*?经营范围：</strong><br>(?P<business_scope>.*?)</div>.*?PublishDate=(?P<publish_date>.*?)"', re.S)
        self.encode = WEB_CHARSET

    def _process(self, corp_info):
        for key in corp_info:
            corp_info[key] = re.sub('<strong>|</strong>|<br>|</br>|&nbsp;|\t|\n', '', str(corp_info[key]), re.S)
        for key in ('publish_date', 'established'):
            if corp_info[key]:
                corp_info[key] = datetime.date(int(corp_info[key][0:4]), int(corp_info[key][4:]), 1)
            else:
                corp_info[key] = datetime.date(1,1,1)
        return corp_info

    def fetch(self, stock):
        stock_obj = stock
        if not isinstance(stock, StockModel):
            stock_obj = super()._get(stock, StockModel)
        html = self.opener.open(self.corp_info_url % stock_obj.no, encode=self.encode)
        search_obj = re.search(self.reg, html)
        corp_info = search_obj.groupdict()
        corp_info['stock_id'] = stock_obj.id
        return corp_info

    # 初始化,自动跳过已经存在的条目
    def initial(self):
        for stock in super()._get_all(StockModel, is_valid=self.VALID):
            print(stock.no)
            if self.get(stock):
                print('跳过')
                continue
            corp_info = self.fetch(stock)
            self.add_one(corp_info)
        self._commit()

    def report(self):
        f = open('corp_infos.csv', 'w')
        r = csv.writer(f, delimiter=',', lineterminator='\n')
        temp = [('市场', '代码','名称','电话')]
        for stock, corp_info in self.session.query(StockModel, CorpInfoModel).filter(StockModel.id == CorpInfoModel.stock_id).all():
            temp.append((
                stock.market,
                stock.no,
                stock.name,
                corp_info.corp_tel
            ))
        r.writerows(temp)
        f.close()
        print('Done')



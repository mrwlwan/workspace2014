# coding=utf8

from lib.models_others import CorpModel
from lib.corp import Corp
import re

class Job168Corp(Corp):
    def __init__(self):
        config = {
            'info_from': '南方人才网',
            'corplist_url': 'http://www.job168.com/person/searchresult1.jsp?page={page_no}&keyword=%BE%AD%C0%ED',
            'corp_url': 'http://www.job168.com/person/etcpos_{corp_code}.html',
            'corplist_reg': re.compile(r'etcpos_(?P<corp_code>[\d]+).html" target="_blank"><span class="Blue1">\s*(?P<name>[^\n<]+)', re.S),
            'corp_regs': [
                re.compile(r'<span>联系地址：</span>(?P<addr>[^<]+)', re.S),
                re.compile(r'<span>联 系 人：</span>(?P<contact_person>[^<]+)', re.S),
                re.compile(r'<span>联系电话：</span>(?P<contact_tel_no>[^<]+)', re.S),
            ],
            'commit_each_times': 30,
            'has_cookie': True,
            'charset': 'gbk',
            'model': CorpModel,
        }
        super().__init__(**config)

        self.pages = 100

    def get_next_page_url(self):
        return (self.corplist_url.format(page_no=page) for page in range(1, self.pages + 1))

    def report(self):
        fields = (
            ('名称', 'name'),
            ('地址', 'addr'),
            ('联系人', 'contact_person'),
            ('电话号码', 'contact_tel_no'),
            ('单位性质', 'nature'),
            ('行业', 'industry'),
            ('规模', 'scale'),
            ('信息来源', 'info_from'),
            ('更新日期', 'insert_date'),
            ('链接', self.corp_url),
        )
        super().report(fields)

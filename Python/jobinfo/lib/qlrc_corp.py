# coding=utf8

from lib.corp import Corp
import re

class QLRCCorp(Corp):
    def __init__(self):
        config = {
            'info_from': '齐鲁人才网',
            'corplist_url':
            'http://www.qlrc.com/personal/js/ajaxPager?iddcJobTypeID=&iddcIndustryID=&iddcRegionID=32&page={0}',
            'corp_url': 'http://www.qlrc.com/personal/{corp_code}.html',
            'corplist_reg': re.compile(r'/personal/(?P<corp_code>cp\d+)[^>]+>(?P<name>[^<]+)', re.S),
            'corp_regs': [
                re.compile(r"所在地区：</font><font class='ftValue'>(?P<addr>[^<]+)", re.S),
                re.compile(r"街道门牌：</font><font class='ftValue'>(?P<contact_person>[^<]+)", re.S),
                re.compile(r"所属行业：</font><font class='ftValue'>(?P<contact_tel_code>[^<]+)", re.S),
                re.compile(r"单位性质：</font><font class='ftValue'>(?P<contact_tel_no>[^<]+)", re.S),
                re.compile(r"企业规模：</font><font class='ftValue'>(?P<mail>[^<]+)", re.S),
            ],
            'commit_each_times': 30,
            'has_cookie': True,
            'charset': 'gbk',
        }
        super().__init__(**config)

        self.pages = 100

    def get_next_page_url(self):
        return (self.corplist_url.format(page) for page in range(1, self.pages + 1))

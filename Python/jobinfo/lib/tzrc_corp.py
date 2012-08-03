# coding=utf8

from lib.corp import Corp
import re, itertools

class TZRCCorp(Corp):
    def __init__(self):
        config = {
            'info_from': '台州人才网',
            'corplist_url': 'http://www.tzrc.com/job/?PageNo={page_no}&JobType=&JobArea=&PublishDate=&Key=&n=20&s=0',
            'corp_url': 'http://www.tzrc.com/company/company_info.asp?coid={corp_code}',
            'corplist_reg': re.compile(r'/company/company_info\.asp\?frombh=\d+&coid=(?P<corp_code>\d+)[^>]+>(?:<font color="#0033FF">)?(?P<name>[^<]+)', re.S),
            'corp_regs': [
                re.compile(r'联&nbsp;系&nbsp;人：(?P<contact_person>[^<]+)', re.S),
                re.compile(r'电&nbsp;&nbsp;&nbsp;&nbsp;话：(?P<contact_tel_no>[^<]+)', re.S),
                re.compile(r'联系地址：[ ]?(?P<addr>[^<]+)', re.S),
            ],
            'commit_each_times': 30,
            'has_cookie': True,
            'charset': 'gbk',
            'timeout': 30,
        }
        super().__init__(**config)

        self.pages = 50

    def get_next_page_url(self):
        yield 'http://www.tzrc.com/'
        for page in range(1, self.pages+1):
            yield self.corplist_url.format(page_no=page)


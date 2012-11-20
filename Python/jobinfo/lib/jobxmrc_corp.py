# coding=utf8

from lib.corp import Corp
import re

class JobXmrcCorp(Corp):
    def __init__(self):
        config = {
            'info_from': '厦门人才网',
            'corplist_url': 'http://www.xmrc.com.cn/net/info/resultg.aspx?searchtype=1&releasetime=365&pagesize=150&pageindex={0}',
            'corp_url': 'http://www.xmrc.com.cn/net/info/showco.aspx?CompanyID={corp_code}',
            'corplist_reg': re.compile(r'CompanyID=(?P<corp_code>\d+)[^>]+>\s*(?P<name>[^<]+)', re.S),
            'corp_regs': [
                re.compile(r'公司性质：&nbsp;(?P<contact_tel_code>[^\n]+)', re.S),
                re.compile(r'联 系 人：&nbsp;(?P<contact_person>[^\n]+)', re.S),
                re.compile(r'联系电话：&nbsp;(?P<contact_tel_no>[^\n]+)', re.S),
                re.compile(r'联系地址：&nbsp;(?P<addr>[^\n]+)', re.S),
                re.compile(r'公司行业：&nbsp;(?P<mail>[^\n]+)', re.S),
            ],
            'commit_each_times': 30,
            'has_cookie': True,
            'charset': 'gbk',
        }
        super().__init__(**config)

        self.pages = 30

    def get_next_page_url(self):
        return (self.corplist_url.format(page) for page in range(1, self.pages + 1))

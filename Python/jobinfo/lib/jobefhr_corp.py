# coding=utf8

from lib.corp import Corp
import re

class JobefhrCorp(Corp):
    def __init__(self):
        config = {
            'info_from': '服装人才网',
            'corplist_url': 'http://www.efhr.cn/Jobs/Index.aspx?&city=&jobType=&pubDate=&keyword=&province=&page={0}',
            'corp_url': 'http://www.efhr.cn/Jobs/Company.aspx?id={corp_code}',
            'corplist_reg': re.compile(r"<a class='a1' href='Company\.aspx\?id=(?P<corp_code>[^']+)' target='_blank' title='(?P<name>[^']+)", re.S),
            'corp_regs': [
                re.compile(r'<strong>电&nbsp;话：</strong>(?P<contact_tel_no>[^<]+)', re.S),
                re.compile(r'<strong>地&nbsp;址：</strong>(?P<addr>[^<]+)', re.S),
            ],
            'commit_each_times': 30,
            'has_cookie': True,
            'charset': 'utf8',
        }
        super().__init__(**config)

        self.pages = 100

    def get_next_page_url(self):
        return (self.corplist_url.format(page) for page in range(1, self.pages + 1))

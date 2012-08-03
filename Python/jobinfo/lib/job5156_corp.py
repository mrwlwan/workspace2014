# coding=utf8

from lib.corp import Corp
import re

class Job5156Corp(Corp):
    def __init__(self):
        config = {
            'info_from': 'job5156',
            'corplist_url': 'http://s.job5156.com/posSearch/keyword.shtml?selectSearchType=2&sortType=1&listdetail=1&joblocation={0}&pageNumber={1}',
            'corp_url': 'http://www.job5156.com/job/{corp_code}.html',
            'corplist_post_data': None,
            'corp_post_data': None,
            'corplist_reg': re.compile(r'<span class="cenli_1">[^/]+//[^.]+\.job5156\.com/jobs/(?P<corp_code>[^.]+)\.html" target="_blank" class="J_blue_5">(?P<name>[^<]+)', re.S),
            'corp_regs': [
                re.compile('话： *</li>[^>]+?>(?P<contact_tel_no>[^<]+)', re.S),
                re.compile('人： *</li>[^>]+?>(?P<contact_person>[^<]+)', re.S),
                re.compile('联系地址： *</li>[^>]+?>(?P<addr>[^<]+)', re.S),
            ],
            'commit_each_times': 30,
            'has_cookie': True,
            'charset': 'gbk',
        }
        super().__init__(**config)

        self.job_locations = (
            {'city': '东莞', 'code':'1401'},
            {'city': '广州', 'code':'1403'},
            {'city': '深圳', 'code':'1402'},
            {'city': '中山', 'code':'1404'},
            {'city': '江门', 'code':'1408'},
            {'city': '佛山', 'code':'1409'},
            {'city': '惠州', 'code':'1407'},
        )
        self.pages = 50

    def get_next_page_url(self):
        return (self.corplist_url.format(job_location['code'], page) for job_location in self.job_locations for page in range(1, self.pages + 1))

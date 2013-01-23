# coding=utf8

from lib.corp import Corp
import re

class Job51Corp(Corp):
    def __init__(self):
        config = {
            'info_from': '51job',
            'corplist_url':
            'http://search.51job.com/jobsearch/search_result.php?fromJs=1&district=0000&funtype=0000&industrytype=00&issuedate=9&providesalary=99&keyword=&keywordtype=2&curr_page=1&lang=c&stype=1&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=01&lonlat=0%2C0&radius=-1&ord_field=0&list_type=0&fromType=14&curr_page={0}&jobarea={1}',
            'corp_url': 'http://search.51job.com/list/{corp_code}.html',
            'corplist_reg': re.compile(r'<td class="td2"><a href="http://search.51job.com/list/(?P<corp_code>[^.]*?)\.html[^>]*?>(?P<name>[^<]*?)<[^_]*?_[^_]*?_fbrq[^>]*?>(?P<insert_date>[^<]*?)<', re.S),
            'corp_regs': [
                re.compile(r'站：(?P<website>[^<]*?)[< ]', re.S),
                re.compile(r'人：(?P<contact_person>[^<]*?)[< ]', re.S),
                re.compile(r'话：(?P<contact_tel_no>[^<]*?)[< ]', re.S),
                re.compile(r'址：(?P<addr>[^<]*?)[< ]', re.S),
            ],
            'commit_each_times': 30,
            'has_cookie': True,
            'charset': 'gbk',
        }
        super().__init__(**config)
        self.jobareas = [
            ('030800', 50), # 东莞
            ('030200', 20), # 广州
            ('040000', 20), # 深圳
            ('030300', 20), # 惠州
            ('030600', 20), # 佛山
            ('080400', 50), # 温州
        ]

    def get_next_page_url(self):
        for jobarea_code, pages in self.jobareas:
            for page in range(1, pages+1):
                yield self.corplist_url.format(page, jobarea_code)

# coding=utf8

from lib.corp import Corp
import re

class Job58Corp(Corp):
    def __init__(self):
        config = {
            'info_from': '58同城',
            'corplist_url': 'http://{0}.58.com/job/pn{1}/?final=3',
            'corp_url': '{corp_code}',
            'corplist_post_data': None,
            'corp_post_data': None,
            'corplist_reg': re.compile(r"^\s+<a href='(?P<corp_code>[^']+)' target='_blank' class='fl'>(?P<name>[^<]+)</a>", re.M),
            'corp_regs': [
                re.compile(r'^\s+(?:<th>|<li><strong>)联 ?系(?:&nbsp; )?人：(?:</th>\s+<td>|</strong><span>)(?P<contact_person>[^<]*?)<', re.M),
                re.compile(r'^\s+(?:<th>|<li><strong>)联系地址：(?:</th>\s+<td>|</strong><span>)(?P<addr>[^<]*?)<', re.M),
            ],
            'commit_each_times': 30,
            'has_cookie': True,
            'charset': 'utf8',
        }
        super().__init__(**config)

        self.job_locations = (
            {'city': '东莞', 'code':'dg', 'pages': 30},
            #{'city': '广州', 'code':'gz', 'pages': 30},
            #{'city': '深圳', 'code':'sz', 'pages': 30},
            {'city': '惠州', 'code':'huizhou', 'pages': 15},
            {'city': '宁波', 'code':'nb', 'pages': 30},
            {'city': '温州', 'code':'wz', 'pages': 30},
            #{'city': '泉州', 'code':'qz', 'pages': 30},
            #{'city': '漳州', 'code':'zhangzhou', 'pages': 30},
        )
        self.pages = 30

    def get_next_page_url(self):
        return (self.corplist_url.format(job_location['code'], page) for job_location in self.job_locations for page in range(1, job_location['pages']+ 1))

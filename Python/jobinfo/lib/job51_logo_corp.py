# coding=utf8

from lib.corp import Corp
import re

class Job51LogoCorp(Corp):
    def __init__(self):
        config = {
            'info_from': '51job',
            'corplist_url': 'http://www.51job.com',
            'corp_url': 'http://ac.51job.com/phpAD/adtrace.php?ID={corp_code}',
            'corplist_reg': re.compile(r"http://ac\.51job\.com/phpAD/adtrace\.php\?ID=(?P<corp_code>[^'\"]+)['\"] (title=['\"]|class=['\"]font_show['\"][^>]*>)(?P<name>[^'\"<]+)", re.S),
            'corp_regs': [],
            'commit_each_times': 30,
            'has_cookie': True,
            'charset': 'gbk',
        }
        super().__init__(**config)

        self.pages = 1

    def get_next_page_url(self):
        return [self.corplist_url]

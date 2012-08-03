# coding=utf8

from lib.corp import Corp
import re, sys

class JobcfwCorp(Corp):
    def __init__(self):
        config = {
            'info_from': '中国服装人才网',
            'corplist_url':
            'http://www.cfw.cn/search/zhiwei.html?request_edu=0&request_experience=0&keywords=0&zhaopin_bigname=0&edittime=0&hidJobArea=0&hidFuntype=0&province2=0&keywordtype=0&invite_salary=0&mpage=50&page={0}',
            'corp_url': 'http://www.cfw.cn/{corp_code}/',
            'corplist_reg': re.compile(r'class="cname"><A title=\'(?P<name>[^\']+)\' href="http://www\.cfw\.cn/(?P<corp_code>[^/]+)', re.S),
            'corp_regs': [
                re.compile(r'<th width="80">联 系 人：</th>[^>]+>(?P<contact_person>[^<]+)', re.S),
                re.compile(r'<th width="80">联系电话：</th>[^>]+>(?P<contact_tel_no>[^<]+)', re.S),
                re.compile(r'<th width="80">通讯地址：</th>[^>]+>(?P<addr>[^<]+)', re.S),
            ],
            'commit_each_times': 30,
            'has_cookie': True,
            'charset': 'gbk',
        }
        super().__init__(**config)

        self.pages = 100

        if not self.opener.login(
            login_url='http://www.cfw.cn/personal/login.asp',
            login_data='url=&method=loginin&username=gogo88er&password=123456',
            check_url='http://www.cfw.cn/personal/',
            check_data='叶问',
            encoding='gbk'
        ):
            sys.exit()
        print('登录成功!')

    def get_next_page_url(self):
        return (self.corplist_url.format(page) for page in range(1, self.pages + 1))

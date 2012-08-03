# coding=utf8

from lib.corp import Corp
import re, sys

class JobINJCorp(Corp):
    def __init__(self):
        config = {
            'info_from': '中国注塑人才网',
            'corplist_url':
            'http://www.inj.com.cn/search/hire_searchresult.php?trade=&trades=&position=&positions=&workadd=&workadds=&datetime=&datetimes=&keyword=&keywordtype=&page={0}',
            'corp_url': 'http://www.inj.com.cn/html/company/company_{corp_code}.html',
            'corplist_reg': re.compile(r'<td align="left"><a href="/html/company/company_(?P<corp_code>\d+)\.html" target="_blank"><b>(?P<name>[^<]+)</b></a></td>[^>]+>(?P<addr>[^<]+)', re.S),
            'corp_regs': [
                re.compile(r'通信地址：(?P<addr>[^<]+)', re.S),
                re.compile(r'联 系 人：(?P<contact_person>[^<]+)', re.S),
                re.compile(r'联系电话：(?P<contact_tel_no>[^<]+)', re.S),
            ],
            'commit_each_times': 30,
            'has_cookie': True,
            'charset': 'gbk',
        }
        super().__init__(**config)

        self.pages = 100

        self.corp_info_url = 'http://www.inj.com.cn/inc/contacts.php?companyid={corp_code}&issee=1'

        if not self.opener.login(
            login_url='http://www.inj.com.cn/login_inj.php?do=login&typeid=1&goto=/index.php',
            login_data='login=gogo88er&pwd=123456&LoginButton.x=48&LoginButton.y=14',
            check_url='http://www.inj.com.cn/member/',
            check_data='叶问',
            encoding='gbk'
        ):
            sys.exit()
        print('登录成功!')

    def get_next_page_url(self):
        return (self.corplist_url.format(page) for page in range(1, self.pages + 1))

    def get_corp_url(self, corp_info={}):
        return self.corp_info_url.format(**corp_info)

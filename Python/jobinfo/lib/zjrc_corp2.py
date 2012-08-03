# coding=utf8

from lib.models_others import CorpModel
from lib.corp import Corp
import re, urllib.parse, json, time

class ZJRCCorp(Corp):
    def __init__(self):
        config = {
            'info_from': '浙江人才网',
            'corplist_url': 'http://www.zjrc.com/Services/Jobs/GetSearch.ashx',
            'corp_url': 'http://www.zjrc.com/Jobs/Comp/{corp_code}',
            'corplist_post_data': None,
            'corp_post_data': None,
            'corplist_reg': re.compile(r"/Jobs/Comp/(?P<corp_code>[^ ']+)' target='_blank'>(?P<name>[^<]+)<", re.S),
            'corp_regs': (
                re.compile(r'<div class="div_net_comper">电子信箱：<a[^>]+>[^<]*</a><br>单位地址：(?P<addr>[^<]+)<br>联系电话：(?P<contact_tel_no>[^联]+)联系人：(?P<contact_person>[^传<]+)', re.S),
            ),
            'commit_each_times': 30,
            'has_cookie': True,
            'charset': 'utf8',
            'model': CorpModel,
        }
        super().__init__(**config)

        self.opener.headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'http://www.zjrc.com/Jobs/Search?js_keytype=1&js_key=%E7%BB%8F%E7%90%86&js_area=000000',
        }

        self.corplist_post_data_format = 'hs_keytype=1&hs_key=%E7%BB%8F%E7%90%86&hs_keyin=&hs_area=000000&hs_areaname=%E8%AF%B7%E9%80%89%E6%8B%A9%E5%9C%B0%E5%8C%BA&hs_sit=00&hs_sitname=%E8%AF%B7%E9%80%89%E6%8B%A9%E5%B2%97%E4%BD%8D%E7%B1%BB%E5%88%AB&hs_industry=00&hs_industryname=%E8%AF%B7%E9%80%89%E6%8B%A9%E8%A1%8C%E4%B8%9A&hs_expires=0&hs_expiresname=%E4%B8%8D%E9%99%90&hs_edu=00&hs_eduname=%E5%85%A8%E9%83%A8&hs_ctype=00&hs_ctypename=%E5%85%A8%E9%83%A8&hs_sex=A&hs_sexname=%E5%85%A8%E9%83%A8&hs_salary=0&hs_salaryname=%E5%85%A8%E9%83%A8&hs_wtype=0&hs_wtypename=%E5%85%A8%E9%83%A8&hs_st=0&hs_stname=%E5%85%A8%E9%83%A8&hs_page={page_no}&hs_list=0&hs_sorttype=&hs_record=30'

        self.pages = 100

    def get_next_page_url(self):
        for page in range(0, self.pages):
            self.corplist_post_data = self.corplist_post_data_format.format(page_no=page)
            yield self.corplist_url

    def fetch_corp(self, corp_info=None):
        time.sleep(3)
        return super().fetch_corp(corp_info)

    def report(self):
        fields = (
            ('名称', 'name'),
            ('地址', 'addr'),
            ('联系人', 'contact_person'),
            ('电话号码', 'contact_tel_no'),
            ('单位性质', 'nature'),
            ('行业', 'industry'),
            ('规模', 'scale'),
            ('信息来源', 'info_from'),
            ('更新日期', 'insert_date'),
            ('链接', self.corp_url),
        )
        super().report(fields)

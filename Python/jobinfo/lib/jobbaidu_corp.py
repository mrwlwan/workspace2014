# coding=utf8

from lib.corp import Corp
import re, urllib.parse, json

class JobbaiduCorp(Corp):
    def __init__(self):
        #job_locations = '广东;东莞,广东;广州,广东;佛山,广东;珠海,广东;中山,广东;江门,广东;惠州,广东;汕头,广东;肇庆'
        job_locations = '广东;东莞,广东;惠州,福建;泉州,福建;漳州,浙江;温州,浙江;宁波'
        config = {
            'info_from': '富海人才网',
            'corplist_url': 'http://www.jobbaidu.com/Commons/ListPosition!list.shtml',
            'corp_url': 'http://www.jobbaidu.com/Commons/com_{corp_code}.html',
            'corplist_post_data': {
                'searcher.workYear2': '13',
                'searcher.workYear1': '1',
                'searcher.keyWordType': '2',
                'searcher.keyWord': '',
                'searcher.jobSalary': '0',
                'searcher.jobPostDate': '0',
                'searcher.jobOrder': '1',
                'searcher.jobLocation3': '0',
                'searcher.jobLocation2': '0',
                'searcher.jobLocation1': '0',
                'searcher.jobLocation': '',
                'searcher.jobLocal': '',
                'searcher.jobIndustry': '',
                'searcher.jobInd': '',
                'searcher.jobGender': '0',
                'searcher.jobFunction3': '0',
                'searcher.jobFunction2': '0',
                'searcher.jobFunction1': '0',
                'searcher.jobFunction': '',
                'searcher.jobFun': '',
                'searcher.jobCalling3': '0',
                'searcher.jobCalling2': '0',
                'searcher.jobCalling1': '0',
                'searcher.jobAge': '0',
                'searcher.degree2':'6',
                'searcher.degree1': '1',
                'refString': '',
                'page.totalCount': '1000',
                'page.pageSize': '20',
                'page.currentPage': '1',
                'jobKeyWord': '公司',
                '__checkbox_searcher.workNoLimit': 'true',
                '__checkbox_searcher.degNoLimit': 'true'
            },
            'corp_post_data': None,
            'corplist_reg': re.compile(r'<a class="a_font_black" target="_blank" href="/Commons/com_(?P<corp_code>\d+)\.html">\s*(?P<name>[^\s]+)', re.S),
            'corp_regs': (
                re.compile('联系人员：(?P<contact_person>[^<]+)', re.S),
                re.compile('联系电话：(?P<contact_tel_no>[^<]+)', re.S),
                re.compile('电子邮件：<a href="mailto:(?P<mail>[^"]+)', re.S),
                re.compile('网站地址：<a href="(?P<website>[^"]+)', re.S),
                re.compile('通讯地址：(?P<addr>[^\n]+)', re.S),
            ),
            'commit_each_times': 30,
            'has_cookie': True,
            'charset': 'utf8',
        }
        super().__init__(**config)

        self.pages = 50

    def get_next_page_url(self):
        for page in range(1, self.pages+1):
            self.corplist_post_data['page.currentPage'] = page
            yield self.corplist_url

    def fetch_corplist(self, page_url):
        content = self.opener.urlopen(page_url, data=self.corplist_post_data, encoding='utf8')
        return ({} if not search_obj else search_obj.groupdict() for search_obj in self.corplist_reg.finditer(content))

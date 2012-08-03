# coding=utf8

from lib.corp import Corp
import re, urllib.parse, json

class JobcnCorp(Corp):
    def __init__(self):
        #job_locations = '广东;东莞,广东;广州,广东;佛山,广东;珠海,广东;中山,广东;江门,广东;惠州,广东;汕头,广东;肇庆'
        job_locations = '广东;东莞,广东;惠州,福建;泉州,福建;漳州,浙江;温州,浙江;宁波'
        config = {
            'info_from': 'jobcn',
            'corplist_url': 'http://www.jobcn.com/search/result_servlet.ujson',
            'corp_url': 'http://www.jobcn.com/position/company.xhtml?comId={corp_code}',
            'corplist_post_data': {
                'p.keyword': '',
                'p.keyword2': '',
                'p.keywordType': '2',
                'p.pageNo': '1',
                'p.pageSize': '20',
                'p.sortBy': 'postdate',
                'p.statistics': 'false',
            },
            'corp_post_data': None,
            'corplist_reg': None,
            'corp_regs': (
                re.compile('联系人：(?P<contact_person>[^<]*?)<', re.S),
                re.compile('电&nbsp;&nbsp;话：(?P<contact_tel_no>[^<]*?)', re.S),
                re.compile('地&nbsp;&nbsp;址：(?P<addr>[^<]*?)', re.S),
            ),
            'commit_each_times': 30,
            'has_cookie': True,
            'charset': 'gbk',
        }
        super().__init__(**config)

        self.pages = 100

    def get_next_page_url(self):
        for page in range(1, self.pages+1):
            self.corplist_post_data['p.pageNo'] = page
            yield self.corplist_url

    def fetch_corplist(self, page_url):
        content = self.opener.urlopen(page_url, data=self.corplist_post_data, encoding='utf8')
        corp_list = json.loads(content)['rows']
        return ({
            'name': corp_info['comName'],
            'corp_code': str(corp_info['comId']),
            'insert_date': corp_info['postDate'],
        } for corp_info in corp_list)

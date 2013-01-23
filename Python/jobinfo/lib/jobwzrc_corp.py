# coding=utf8

from lib.corp import Corp
import re, urllib.parse, json

class WzrcCorp(Corp):
    def __init__(self):
        config = {
            'info_from': '温州人才网',
            'corplist_url': 'http://www.wzrc.net/Personal/findJob/searchResult.aspx?x=search',
            'corp_url': 'http://www.wzrc.net/Personal/Jobs/JobList.aspx?s={corp_code}',
            'corplist_post_data': {
                'wkregion': '330300',
                'select_sortitem': 'modidt',
                'select_orderby': 'desc',
                'DropDownList_During': '30',
            },
            'corp_post_data': None,
            'corplist_reg': re.compile(r"<a href='/Personal/Jobs/JobList\.aspx\?s=(?P<corp_code>[^&]+)[^>]+>(?P<name>[^<]+)"),
            'corp_regs': [],
            'commit_each_times': 30,
            'has_cookie': True,
            'charset': 'utf8',
        }
        super().__init__(**config)
        self.domain = 'http://www.wzrc.net'
        self.corplist_search_url = 'http://www.wzrc.net/Personal/findJob/searchResult.aspx?x=search'
        self.pages = 50

    def prepare(self):
        viewstate_reg = re.compile(r'id="__VIEWSTATE" value="([^"]+)')
        previouspage_reg = re.compile(r'id="__PREVIOUSPAGE" value="([^"]+)')
        home_content = self.opener.urlopen(self.domain)
        viewstate = viewstate_reg.search(home_content).group(1)
        previouspage = previouspage_reg.search(home_content).group(1)
        search_content = self.opener.urlopen(self.corplist_search_url, data={
            '__VIEWSTATE': viewstate,
            '__PREVIOUSPAGE': previouspage,
            'keys': '职位/单位名称关键字',
            'DropDownList_During': 30,
            'btnSearch': '搜索'
        })
        viewstate = viewstate_reg.search(search_content).group(1)
        previouspage = previouspage_reg.search(search_content).group(1)
        self.corplist_post_data.update({
            '__VIEWSTATE': viewstate,
            '__PREVIOUSPAGE': previouspage,
        })

    def get_next_page_url(self):
        for page in range(self.pages):
            self.corplist_post_data['DropDownList_page'] = page
            yield self.corplist_url

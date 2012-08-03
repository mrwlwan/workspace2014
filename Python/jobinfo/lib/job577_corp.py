# coding=utf8

from lib.corp import Corp
import re, urllib.parse

class Job577Corp(Corp):
    def __init__(self):
        config = {
            'info_from': 'job577',
            'corplist_url': 'http://www.577job.com/personal/findjob/searchResult.aspx',
            'corp_url': 'http://www.577job.com/Personal/Jobs/JobList.aspx?s={corp_code}&dwdm=svaLVOwskhI=',
            'corplist_post_data': None,
            'corp_post_data': None,
            'corplist_reg': re.compile(r'Personal/Jobs/JobList\.aspx\?[us]=(?P<corp_code>[^&"]+)[^>]+>(?P<name>[^<]+)<', re.S),
            'corp_regs': [
                #re.compile('Label_basic">&nbsp;<b>单位性质: </b>(?P<nature>[^&<]*)[^>]+>行业: </b>(?P<industry>[^&<]*)[^>]+', re.S),
                #re.compile(r'<b>规模: </b>(?P<scale>[^<]+)', re.S),
                re.compile('Label_addr">(?P<addr>[^<]+)', re.S),
                re.compile('Label_conn">(?P<contact_person>[^<]+)', re.S),
                re.compile('Label_tel">(?P<contact_tel_no>[^<]+)', re.S),
            ],
            'commit_each_times': 30,
            'has_cookie': True,
            'charset': 'utf8',
        }
        super().__init__(**config)

        self._viewstate_reg = re.compile(r'id="__VIEWSTATE"\s+value="([^"]*)')
        self._previouspage_reg = re.compile(r'id="__PREVIOUSPAGE"\s+value="([^"]*)')
        self._viewstate = ''
        self._corplist_post_data = '__EVENTTARGET=DropDownList_page&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE={viewstate}&TextBox_dwkey_add=%E5%8D%95%E4%BD%8D%E5%90%8D%E7%A7%B0%E5%85%B3%E9%94%AE%E5%AD%97&TextBox_poskey_add=%E8%81%8C%E4%BD%8D%E5%90%8D%E7%A7%B0%E5%85%B3%E9%94%AE%E5%AD%97&select_sortitem=modidt&select_orderby=desc&DropDownList_page={page}&alertmsg='

        self.pages = 80

    def get_next_page_url(self):
        yield 'http://www.577job.com'
        pre_post_data = 'resumeLeft_TreeViewResume_ExpandState=ennnnn&resumeLeft_TreeViewResume_SelectedNode=&__EVENTTARGET=LinkButton_search&__EVENTARGUMENT=&resumeLeft_TreeViewResume_PopulateLog=&__VIEWSTATE={viewstate}&wkregion=&postp=++++&indu=&dwtype=&apply_wkregion=&apply_func=++++&apply_indu=&apply_dwtype=&DropDownList_During=30&DropDownList_Educ=&TextBox_Poskey=&TextBox_Dwkey=&DropDownList_Salary=&CheckBox_faceflag=on&RadioButtonList_Source=1&__PREVIOUSPAGE={previouspage}&DropDownList_page=2'
        # 先打开页面, 取得viewstate和previouspage的值.
        content = self.opener.urlopen(self.corplist_url, times=0)
        viewstate = urllib.parse.quote(self._viewstate_reg.search(content).group(1), safe='')
        previouspage = urllib.parse.quote(self._previouspage_reg.search(content).group(1), safe='')
        # 打开搜索结果的页面, 取得最终想得到的viewstate的值
        pre_post_data = pre_post_data.format(viewstate=viewstate, previouspage=previouspage)
        content = self.opener.urlopen(self.corplist_url, data=pre_post_data, times=0)
        self._viewstate = urllib.parse.quote(self._viewstate_reg.search(content).group(1), safe='')
        for page in range(1, self.pages+1):
            self.corplist_post_data = self._corplist_post_data.format(page=page, viewstate=self._viewstate)
            yield self.corplist_url


    def fetch_corplist(self, page_url):
        content = self.opener.urlopen(page_url, data=self.corplist_post_data, timeout=self.timeout, times=0)
        self._viewstate = urllib.parse.quote(self._viewstate_reg.search(content).group(1), safe='')
        return ({} if not search_obj else search_obj.groupdict() for search_obj in self.corplist_reg.finditer(content))

    #def report(self):
        #fields = (
            #('名称', 'name'),
            #('地址', 'addr'),
            #('联系人', 'contact_person'),
            #('电话号码', 'contact_tel_no'),
            #('单位性质', 'nature'),
            #('行业', 'industry'),
            #('规模', 'scale'),
            #('信息来源', 'info_from'),
            #('更新日期', 'insert_date'),
            #('链接', self.corp_url),
        #)
        #super().report(fields)

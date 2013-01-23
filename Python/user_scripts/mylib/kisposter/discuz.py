# coding=utf8

from .poster import Poster, DatetimeString, Helper
import lxml.html, lxml.etree
import re, urllib.parse


class DiscuzHelper(Helper):
    """ 辅助功能类. """
    URL_REG1 = re.compile(r'(forum-(?P<fid>\d+)|thread-(?P<tid>\d+))-(?P<page>\d+)')
    POST_FLOOR_REG = re.compile(r'><em>(?P<floor>\d+)')
    POST_PUBLISHTIME_REG = re.compile(r'<span title="(?P<published_time>[^"]+)')

    def parse_url_query(self, url, url_type=1, encoding=None):
        """ 分析Url, 返回tid, pid, page等信息. """
        if url_type==1: # thread-xxx-xx-x.html
            path = urllib.parse.unquote(urllib.parse.urlparse(url).path, encoding or self.get_charset())
            return self.URL_REG1.search(path).groupdict()
        elif url_type==2: # tid=xxx&pid=xx
            return super().parse_url_query(url, encoding)
        else:
            raise Exception('不支持的URL类型')

    def generate_url(self, fid=None, tid=None, page=1):
        """ 构建一个forum或者thread链接. """
        if tid:
            path = 'thread-{0}-{1}-1.html'.format(tid, page)
        elif fid:
            path = 'forum-{0}-{1}.html'.format(fid, page)
        else:
            raise Exception('缺少参数!')
        return self.get_absolute_url(path)

    def get_threads(self, url=None, fid=None, pages=[1,], filter=None):
        forum_url_format = url or self.generate_url(fid=fid, page='{0}')
        tbody_id_reg = re.compile(r'(?P<subject>stickthread|normalthread)')
        uid_reg = re.compile(r'uid-(?P<uid>\d+)')
        for page in pages:
            forum_url = forum_url_format.format(page)
            page = self.urlget(forum_url).text
            root = lxml.html.fromstring(page)
            tbodies = root.xpath('//form[@id="moderate"]/table/tbody')
            for tbody in tbodies:
                subject_search = tbody_id_reg.match(tbody.attrib.get('id', ''))
                if not subject_search: continue
                # subject
                thread = subject_search.groupdict()
                by1 = 0
                for td in tbody.find('tr'):
                    if td.attrib.get('class')=='icn':
                        alt = td.find('a/img').attrib.get('alt')
                        # position_type, 如置顶等信息
                        if alt: thread['position_type'] = alt
                    elif td.tag=='th':
                        for item in td:
                            if item.tag=='em':
                                # type
                                thread['type'] = item.find('a').text
                                type_url = item.find('a').attrib.get('href')
                                type_url_query = urllib.parse.urlparse(type_url).query
                                # typeid
                                thread['type_id'] = urllib.parse.parse_qs(type_url_query).get('typeid',[None])[0]
                            elif item.attrib.get('class')=='xst':
                                # title
                                thread['title'] = item.text
                                # tid, page
                                thread.update(self.parse_url_query(item.attrib.get('href', '')))
                            elif item.tag=='img':
                                # heatlevel, disagree, attach_img
                                thread[item.attrib.get('alt')] = item.attrib.get('title', True)
                            elif item.attrib.get('class')=='tps':
                                # pages
                                thread['pages'] = len(item) and int(item[-1].text) or 1
                            elif item.attrib.get('class')=='xi1':
                                # is new
                                thread['is_new'] = True
                    elif td.attrib.get('class')=='by':
                        user_item = td.find('cite/a')
                        published_item = td.find('em')
                        if by1==0:
                            # author
                            thread['author'] = user_item.text
                            # author_uid
                            print(thread)
                            print(user_item.attrib.get('href'))
                            thread['author_uid'] = uid_reg.search(user_item.attrib.get('href')).groupdict().get('uid')
                            # published
                            thread['published'] = DatetimeString(published_item.text_content().strip())
                            by1 = 1
                        elif by1==1:
                            # last_poster
                            thread['last_poster'] = user_item.text
                    elif td.attrib.get('class')=='num':
                        # reply_num
                        thread['reply_num'] = int(td.find('a').text_content())
                        # view_num
                        thread['view_num'] = int(td.find('em').text_content())
                # fid
                thread['fid'] = fid
                yield thread



class DiscuzReply(Poster):
    """ for discuz 2.5. """
    # 必须的传入参数.
    REQUIRE_OPTIONS = set(['username', 'domain', 'fid', 'tid'])

    THREAD_URL_REG2 = re.compile(r'tid=(?P<tid>\d+)&pid=(?P<pid>\d+)')
    POST_FLOOR_REG = re.compile(r'><em>(?P<floor>\d+)')
    POST_PUBLISHTIME_REG = re.compile(r'<span title="(?P<published_time>[^"]+)')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fid = self.options.get('fid')
        self.tid = self.options.get('tid')
        # 重设置helper
        self.helper = DiscuzHelper(self.domain, session=self.session)
        self._formhash = None
        self._check_post_info = True
        self._last_post_info = None

    def get_post_new(self, tid, pid):
        """ 返回最近发表的帖子信息. """
        url = self._url('/forum.php?mod=viewthread&tid={0}&viewpid={1}&from=&inajax=1&ajaxtarget=post_new'.format(tid, pid))
        response = self.urlget(url)
        text = lxml.etree.fromstring(response.content).text
        floor_obj = self.POST_FLOOR_REG.search(text)
        published_time = self.POST_PUBLISHTIME_REG.search(text, floor_obj.start())
        temp = floor_obj.groupdict()
        temp.update([(key, DatetimeString(value)) for key, value in published_time.groupdict().items()])
        return temp

    def get_thread_url(self):
        return self._url(self.options.get('thread_url') or self.helper.generate_url(tid=self.tid))

    def get_post_url(self):
        return self._url(self.options.get('post_url') or '/forum.php?mod=post&action=reply&fid={0}&tid={1}&extra=page%3D1&replysubmit=yes&infloat=yes&handlekey=fastpost&inajax=1'.format(self.fid, self.tid))

    def get_login_page_url(self):
        return self._url(self.options.get('login_page_url') or '/member.php?mod=logging&action=login')

    def get_login_form_url(self):
        return self._url(self.options.get('login_form_url') or '/member.php?mod=logging&action=login')

    def get_check_login_url(self):
        return self._url(self.options.get('check_login_url') or '/member.php?mod=logging&action=login')

    def get_check_login_target(self):
        return '欢迎'

    def get_login_data(self, data=None):
        return super().get_login_data({'cookietime': 99999999})

    def get_post_data(self, data):
        """ 返回post_data. """
        if not self._formhash:
            root = lxml.html.fromstring(self.urlget(self.get_thread_url()).text)
            self._formhash = root.xpath('//input[@name="formhash"]/@value')
        post_data = {
            'formhash': self._formhash,
            'usesig': 1,
            'subject': ''
        }
        post_data.update(data)
        return post_data

    def post(self, message):
        """ 发表帖子. """
        self.msg('回复内容: """%s"""' % message)
        return super().post(data={'message': message.encode('gbk')})

    def get_post_header(self):
        return {'Referer': self.get_thread_url()}

    def after_post(self, response):
        text = response.text
        if(text.find('成功')>=0):
            if self._check_post_info:
                post_info = self.get_post_new(**self.THREAD_URL_REG2.search(text).groupdict())
                self._last_post_info = post_info
                self.msg('成功回复在{floor}楼!'.format(**post_info))
            else:
                self.msg('回复成功!')
        else:
            self.msg('回复失败!')

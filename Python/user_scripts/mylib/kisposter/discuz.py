# coding=utf8

from .poster import Poster, DateTimeString, Helper
import lxml.html, lxml.etree
import re, urllib.parse


class DiscuzHelper(Helper):
    """ 辅助功能类. """
    URL_REG1 = re.compile(r'(forum-(?P<fid>\d+)|thread-(?P<tid>\d+))-(?P<page>\d+)')
    POST_FLOOR_REG = re.compile(r'><em>(?P<floor>\d+)')
    POST_PUBLISHTIME_REG = re.compile(r'<span title="(?P<publish_time>[^"]+)')

    def __init__(self, domain, fid, tid, session=None):
        super().__init__(domain, session)
        self.fid = fid
        self.tid = tid

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
            path = 'forum-{0}-1.html'.format(fid)
        else:
            raise Exception('缺少参数!')
        return self.get_absolute_url(path)

    def get_threads(self, fid, pages=[1,], filter=None):
        pass


class DiscuzReply(Poster):
    """ for discuz 2.5. """
    # 必须的传入参数.
    REQUIRE_OPTIONS = set(['username', 'domain', 'fid', 'tid'])

    THREAD_URL_REG2 = re.compile(r'tid=(?P<tid>\d+)&pid=(?P<pid>\d+)')
    POST_FLOOR_REG = re.compile(r'><em>(?P<floor>\d+)')
    POST_PUBLISHTIME_REG = re.compile(r'<span title="(?P<publish_time>[^"]+)')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fid = self.options.get('fid')
        self.tid = self.options.get('tid')
        self.helper = DiscuzHelper(self.domain, self.fid, self.tid, session=self.session)
        self._formhash = None
        self._check_post_info = True
        self._last_post_info = None

    def get_post_new(self, tid, pid):
        """ 返回最近发表的帖子信息. """
        url = self._url('/forum.php?mod=viewthread&tid={0}&viewpid={1}&from=&inajax=1&ajaxtarget=post_new'.format(tid, pid))
        response = self.urlget(url)
        text = lxml.etree.fromstring(response.content).text
        floor_obj = self.POST_FLOOR_REG.search(text)
        publish_time = self.POST_PUBLISHTIME_REG.search(text, floor_obj.start())
        temp = floor_obj.groupdict()
        temp.update([(key, DateTimeString(value)) for key, value in publish_time.groupdict().items()])
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

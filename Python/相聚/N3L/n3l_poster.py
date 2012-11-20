# coding=utf8

from models import TinfoModel
from funcs import coroutine
from opener import Opener
import time, re, itertools, sys, random

class SkipException(Exception):
    pass

class Poster():
    def __init__(self):
        self.model = TinfoModel
        self.base_url = 'http://www.new-3lunch.net'
        self.opener = Opener(has_cookie=True, cookie_path='cookie.txt', encoding='utf8', headers={'Referer': 'http://www.new-3lunch.net/thread-506713-1-1.html', 'User-agent': 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16'})
        self.thread_field_url = self.base_url + '/forum.php?mod=forumdisplay&fid=%s&page=%s&mobile=yes'
        #self.thread_field_url = self.base_url + '/forum.php?mod=forumdisplay&fid=%s&page=%s&orderby=dateline&filter=author&orderby=dateline&mobile=yes'
        self.pages = 10
        self.thread_fields = [
            {'name': '街头美女搜猎区', 'fid': 93},
            {'name': '成人贴图区', 'fid': 17},
                    #{'name': '中日韩独家精华区', 'fid': 140},
                    #{'name': '日韩独家精华区', 'fid': 141},
                    #{'name': '欧美独家精华区', 'fid': 142},
                    #{'name': '卡通独家精华区', 'fid': 143},
                    #{'name': '杂锦独家精华区', 'fid': 144},
            {'name': '成人电影在线观看', 'fid': 19},
            {'name': 'BT成人电影交流区', 'fid': 86},
            #{'name': '各地少女贴图区', 'fid': 24},
            #{'name': '丝袜美腿分享区', 'fid': 27},
            {'name': '有味文学区', 'fid': 25},
            #{'name': '成人吹水区', 'fid': 26},
            #{'name': '明星贴图区', 'fid': 42},
                    #{'name': 'H漫画CG分享区', 'fid': 20},
        ]

    def urlopen(self, url, data=None, timeout=5, times=0, is_return_content=True):
        return self.opener.urlopen(url, data, timeout=timeout, times=times, is_return_content=is_return_content)

    @coroutine
    def _get_tinfo(self):
        reg = re.compile(r'<a href="forum\.php\?mod=viewthread&amp;tid=(?P<tid>\d+)[^>]*?>\s*(?P<title>[^<]*?)</a>[^>]*?>[^>]*?>[^>]*?>[^>]*?>\s+(?P<published>[^\s]+)\s+回(?P<replied>\d+)', re.S)
        result = []
        while 1:
            content = yield result
            result = []
            for search_obj in reg.finditer(content):
                result.append(search_obj.groupdict())
            for item in result:
                item['published'] = self.model._str2date(item['published'])
                item['replied'] = int(item['replied'])

    def get_tinfos(self, fid):
        get_tinfo = self._get_tinfo()
        result = []
        for page in range(1, self.pages+1):
            print('正在分析第%s页...' % page)
            url = self.thread_field_url % (fid, page)
            content = self.urlopen(url, times=3)
            result.extend(get_tinfo.send(content))
        result.reverse()
        #print('主题列表:\n', result)
        print('分析完毕!\n')
        return result

    @coroutine
    def get_reply(self):
        reg = re.compile(r'class="postmessage">([^<]+)', re.S)
        result = []
        while 1:
            content = (yield result and random.choice(result) or '')
            result = []
            for search_obj in reg.finditer(content):
                temp = search_obj.group(1).strip().lower()
                if temp.startswith('th'):
                    continue
                result.append(temp)

    def login(self):
        check_url = self.base_url + '/home.php?mod=space&do=profile&mobile=yes'
        check_data = 'today412'
        try:
            if self.opener.login(None, None, check_url, check_data, encoding='utf8'):
                return True
        except:
            pass
        login_url = self.base_url + '/member.php?mod=logging&action=login&loginsubmit=yes&loginhash=L7mh9&mobile=yes'
        login_data = {
            'formhash': 'ef4e1524',
            'referer': 'http://www.new-3lunch.net/forum.php?mobile=yes',
            'fastloginfield': 'username',
            'username': 'today412',
            'password': input('请输入密码:\n').strip(),
            'quickforward': 'yes',
            'handlekey': 'ls',
            'cookietime': '999999999999992592000',
            'submit': '提交',
            'questionid': '0',
            'answer': '',
        }
        return self.opener.login(login_url, login_data, check_url, check_data, use_cookie=False, times=5, encoding='utf8')

    def get_param(self, reg, content):
        search_obj = reg.search(content)
        return search_obj and search_obj.groups()[0] or ''

    def _message_format(self):
        strings1 = ['多谢哂','Thanks']
        strings2 = ['...', '..', '....', ' ', ', ']
        strings3 = ['', ' ^_^', ' :P', ' ^V^']
        while 1:
            yield '%s%s%s%s' % ( random.choice(strings1), random.choice(strings2), '%s', random.choice(strings3))


    def post(self, reply_page=3, min_reply=20, sleep=8):
        thread_url = self.base_url + '/forum.php?mod=viewthread&tid=%s&extra=&page=%s&mobile=yes'
        post_url = self.base_url + '/forum.php?mod=post&action=reply&fid=%s&tid=%s&extra=&replysubmit=yes&mobile=yes'
        formhash_reg = re.compile(r'name="formhash" value="([^"]+)"')
        times = itertools.count(1)
        get_reply = self.get_reply()
        message_format = self._message_format()
        for thread_field in self.thread_fields:
            print('\n********************************************')
            print(thread_field['name'])
            print('********************************************')
            fid = thread_field['fid']
            for tinfo in self.get_tinfos(fid):
                try:
                    print('\n正在回帖<<%s>>...' % tinfo['title'].encode('gbk',errors='ignore').decode('gbk'))
                    if tinfo['replied'] < min_reply:
                        raise(SkipException('现有回帖数太少'))
                    if self.model.exists_by(tid=tinfo['tid']):
                        raise(SkipException('此帖已经回复过'))
                    content = self.urlopen(thread_url % (tinfo['tid'], reply_page), times=3)
                    formhash = self.get_param(formhash_reg, content)
                    if not formhash:
                        raise(SkipException('此帖找不到formhash'))
                    message = get_reply.send(content)
                    tinfo['fid'] = fid
                    del tinfo['replied']
                    self.model.add(tinfo, is_commit=False)
                    #self.model.add(tinfo)
                    if message:
                        message = next(message_format) % message
                        print('回复内容: %s' % message.encode('gbk', errors='ignore').decode('gbk'))
                        post_data = {
                            'message': message,
                            'formhash': formhash,
                            'replysubmit': '回復',
                        }
                        self.urlopen(post_url % (fid, tinfo['tid']), data=post_data, times=3, is_return_content=False)
                        print('\n累计得到积分: %s\n' % next(times))
                        time.sleep(sleep)
                    else:
                        raise(SkipException('找不到合适的回复内容'))
                except SkipException as e:
                    print('%s, 将跳过回复此帖!' % e)
                except Exception as e:
                    print('其它异常: %s' % e)
            self.model.commit()
        print('\n\n总共累计所得积分为: %s' % (next(times)-1))

    def action(self):
        if self.login():
            #self.get_tinfos(93)
            self.post(sleep=25)

if __name__ == '__main__':
    poster = Poster()
    poster.action()

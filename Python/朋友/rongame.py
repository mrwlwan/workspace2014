# coding=utf8

import kisopener, config
import urllib.parse, time, sys, traceback, re, itertools, threading, os


class Rongame(threading.Thread):
    def __init__(self, username, password):
        super().__init__()
        self.username = username
        self.password = password
        self._opener = kisopener.Opener(cookie_path='cookies/%s.txt' % self.username)
        self._timeout = 3
        self._encoding = 'utf8'

    def _url(self, url):
        return urllib.parse.urljoin('http://www.rongame.com', url)

    def fetch(self, *args, **kwargs):
        kwargs['timeout'] = self._timeout
        while 1:
            try:
                 return self._opener.urlopen(*args, **kwargs).read().decode(self._encoding, 'ignore')
            except:
                 #traceback.print_exc()
                 print(self.msg('网络超时'))

    def form_dict(self, content, ignore=[]):
        ignore = set(ignore)
        reg = re.compile(r"""<input[^>]*?name=['"]([^'"]*)['"][^>]*value=['"]([^'"]*)""")
        return dict([(key, value) for key, value in reg.findall(content) if key not in ignore])

    def check_logined(self):
        content = self.fetch(self._url('/home.php?mod=space'))
        if content.find(self.username)>=0:
            self._opener.save_cookies()
            return True
        return False

    def login(self):
        if self.check_logined():
            self.msg('Cookie 登录成功!')
            return
        data = {
            'username': self.username,
            'password': self.password,
            'fastloginfield': 'username',
            'quickforward': 'yes',
            'handlekey': 'ls',
            'cookietime': 999999999,
        }
        content = self.fetch(self._url('member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes&inajax=1'), data=data)
        if self.check_logined():
            self.msg('登录成功!')
        else:
            self.msg('登录失败!')
            sys.exit()

    def do_fresh(self, useragents):
        while 1:
            for useragent in useragents:
                self._opener.set_headers({'User-agent': useragent})
                print(self._opener.opener.addheaders)
                content = self.fetch('http://www.rongame.com/home.php?mod=space&uid=211144&do=profile')
                self.msg('刷新成功!')
                time.sleep(self._timeout)

    def do_blog(self):
        url = self._url('/home.php?mod=spacecp&ac=blog')
        content = self.fetch(url)
        form_hash = re.search(r'name="formhash" value="([^"]+)', content).group(1)
        self.msg('Form hash: %s' % form_hash)
        #index = itertools.count(1)
        while 1:
            time.sleep(config.delay)
            #print(next(index))
            post_url = self._url('/home.php?mod=spacecp&ac=blog&blogid=')
            data = {
                    'subject': config.subject,
                    'message': config.message,
                    'classid': '572',
                    'tag': '',
                    'friend': 3,
                    'noreply': 1,
                    'password': '',
                    'selectgroup': '',
                    'target_names': '',
                    'blogsubmit': 'true',
                    'formhash': form_hash,
            }
            content = self.fetch(post_url, data=data)
            if content.find('操作成功'):
                self.msg('操作成功')
            else:
                self.msg('操作失败')
                self.log(content)

    def run(self):
        self.login()
        self.do_blog()

    def msg(self, text):
        print('[%s][%s] %s' % (time.strftime('%Y-%m-%d %H:%M:%S'), self.username, text))

    def log(self, text):
        with open('log.txt', 'w', newline='\n', encoding='utf8') as f:
            f.write(text)


if __name__ == '__main__':
    if not os.path.exists('cookies') or not os.path.isdir('cookies'):
        os.mkdir('cookies')

    useragents = [
        'Mozilla/5.0 (compatible; MSIE 6.0; Windows NT 5.1)',
        'Mozilla/4.0 (compatible; MSIE 6.0; MSIE 5.5; Windows NT 5.1)',
        'Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 5.2)',
        'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.2; Trident/4.0; Media Center PC 4.0; SLCC1; .NET CLR 3.0.04320)',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; Media Center PC 6.0; InfoPath.3; MS-RTC LM 8; Zune 4.7)',
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
        'Mozilla/6.0 (Windows NT 6.2; WOW64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1',
        'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:15.0) Gecko/20120910144328 Firefox/15.0.2',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:14.0) Gecko/20100101 Firefox/14.0.1',
        'Mozilla/5.0 (Windows NT 5.1; rv:15.0) Gecko/20100101 Firefox/13.0.1',
        'Mozilla/5.0 (Windows NT 6.1; rv:12.0) Gecko/20120403211507 Firefox/12.0',
        'Opera/12.80 (Windows NT 5.1; U; en) Presto/2.10.289 Version/12.02',
        'Opera/9.99 (Windows NT 5.1; U; pl) Presto/9.9.9',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_4) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.65 Safari/535.11',
        'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5355d Safari/8536.25',
        'Mozilla/4.0 (compatible; MSIE 6.0; X11; Linux i686; en) Opera 8.02',
        'Opera/8.54 (X11; Linux i686; U; pl)',
        'Opera/7.02 (Windows NT 5.1; U; ja)',
        'Opera/5.21 (X11; Linux i686; U; en)',
        'Opera/6.0 (Windows XP; U)',
    ]

    accounts = [account.split(':') for account in config.accounts.split(';') if account]
    rongames = []
    for account in accounts:
        rongames.append(Rongame(*account))
    for rongame in rongames:
        rongame.start()
    for rongame in rongames:
        rongame.join()
    #rongame = Rongame(config.username, config.password)
    #rongame.login()
    #rongame.do_blog()

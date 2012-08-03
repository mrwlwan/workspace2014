#!/bin/python
# coding=utf-8

import urllib2, cookielib, sys, random, re, time, os.path, threading
#from getmozcookies import getCookies

############ 用户参数设置区 ###################
# 目标地址 (灌水的帖子地址)
TARGET_URL = 'http://www.cheabc.com/bbs/thread-156415-1-1.html'
# 用户账号密码列表文本.以":"分隔用户名和密码,一行一个账户.UTF-8编码.
USER_FILE = 'user.txt'
# 灌水文本,UTF-8 编码
TARGET_FILE = 'cheabc.txt'
# 延时(单位：秒)
DELAY = 10
# 是否重复 (True or False)
IS_REPEAT = True
# 是否按顺序，不按顺序即随机 (True or False)
IS_ORDER = True
# 回复是否需要验证(只支持简单的验证, True or False)
NEED_VALIDATE = True
# 网页编码(打开目标网页,选择Firefox的菜单"Tools"->"Page Info",查看"Encoding"可知当前网页的编码.
CHARSET = 'utf8'

# 网站相关信息
WEBSITE_NAME = 'cheabc'
BASE_URL = 'http://www.cheabc.com/bbs/'
###############################################

def urlopen(url, data=None,timeout=None, opener=None, returnUrl=False):
    while 1:
        try:
            if opener:
                sock = opener.open(url, data, timeout=timeout)
            else:
                sock = urllib2.urlopen(url, data, timeout=timeout)
            if sock.getcode() == 200:
                html = sock.read()
                if returnUrl:
                    return sock.geturl(), html
                else:
                    return html
        except Exception as e:
            print e

def getUserDate(filename):
    try:
        f = open(filename)
        lines = f.readlines()
        f.close()
        return [line.strip().split(':') for line in lines]
    except:
        return None


class FuckBBS(threading.Thread):
    def __init__(self, username, password, option={}):
        threading.Thread.__init__(self)
        self.option = {
            'targetUrl': '',
            'targetFile': '',
            'delay': 1,
            'isRepeat': True,
            'isOrder': True,
            'needValidate': True,
            'baseUrl': '',
            'charset': 'utf8',
        }
        self.option.update(option)
        self.username, self.password = [item.decode('utf8').encode(self.option['charset']) for item in (username, password)]
        self.opener = self._createOpener()

    def urlopen(self, url, data=None, timeout=None, returnUrl=False):
        return urlopen(url, data, timeout, self.opener, returnUrl)

    def _createOpener(self):
#        cookieJar = cookielib.LWPCookieJar(cookieFile)
#        cookieJar.load()
        cookie = urllib2.HTTPCookieProcessor()
        opener = urllib2.build_opener(cookie)
        opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.2.5pre) Gecko/20100505 Firefox/3.6 GTB7.0 (ayakawa PGU)'), ('Content-Type', 'application/x-www-form-urlencoded')]
        return opener

    def _prepare(self):
        html = self.urlopen(self.option['targetUrl'])
        formHash = re.findall(r'"formhash" value="([^"]*)"', html)[0]
        formActionUrl = re.findall(r'post.php\?action=reply[^"]*', html)[0]
        formActionUrl = formActionUrl.replace(r'amp;', '') + '&extra=page%3D1&replysubmit=yes&infloat=yes&handlekey=fastpost&inajax=1'
        return formHash, self.option['baseUrl'] + formActionUrl


    def login(self):
        username, password = [item.decode('utf8').encode(self.option['charset']) for item in (self.username, self.password)]
        loginUrl = self.option['baseUrl'] + 'logging.php?action=login&loginsubmit=true'
        data = 'username=%s&password=%s&cookietime=2592000&loginsubmit=true' % (urllib2.quote(username), urllib2.quote(password))
        self.urlopen(loginUrl, data)
        self.option['formHash'], self.option['formActionUrl'] = self._prepare()

    def isLogin(self):
        html = self.urlopen(self.option['baseUrl'] + 'pm.php')
        if html.find(self.username)>=0:
            return True
        else:
            return False

    def getHackStrings(self):
        try:
            f = open(self.option['targetFile'])
            lines = f.readlines()
            f.close()
            lines1 = [line.decode('utf8') for line in lines if len(line.strip())>2]
            if self.option['charset'].lower().startswith('utf'):
                lines2 = [urllib2.quote(line) for line in lines if len(line.strip())>2]
            else:
                lines2 = [urllib2.quote(line) for line in lines1]
            return (lines2, lines1)
        except:
            return (None, None)

    def getValidateAnswer(self):
        html = self.urlopen(BASE_URL + 'ajax.php?action=updatesecqaa&inajax=1&ajaxtarget=secanswer3_menu')
        reg = '\[CDATA\[([^=]+)='
        ext = re.search(reg, html)
        if ext:
            return str(eval(ext.groups()[0]))
        else:
            return None

    def postContent(self, content):
        answerStr = ''
        if self.option['needValidate']:
            answer = self.getValidateAnswer()
            answerStr = '&secanswer=' + answer
        data = 'formhash=' + self.option['formHash'] + '&message=' + content + answerStr
        self.urlopen(self.option['formActionUrl'], data=data)

    def run(self):
        self.login()
        if self.isLogin():
            print self.username.decode('utf8'), u'登录成功!'
        else:
            print u'登录错误!请检查用户名和密码是否正确...'
            return
        hackStrings, orgStrings = self.getHackStrings()
        if hackStrings:
            print u'读取灌水文本成功!'
        else:
            print u'灌水文本有误,请检查...'
            return
        stringsNum = len(hackStrings)
        index = 0
        while self.option['isRepeat']:
            print '*******************************\n'
            print self.username.decode('utf8')
            print time.asctime()
            if not self.option['isOrder']:
                index = random.randrange(stringsNum)
            print orgStrings[index]
            self.postContent(hackStrings[index])
            print '*******************************\n'
            time.sleep(self.option['delay'])
            index = (index+1)%stringsNum

if __name__ == '__main__':
    users = getUserDate(USER_FILE)
    if not users:
        print u'用户文件列表无效...'
        sys.exit()
    print u'成功读取用户:'
    for user in users:
        print user[0].decode('utf8')
    print '\n\n'
    option = {
        'targetUrl': TARGET_URL,
        'targetFile': TARGET_FILE,
        'delay': DELAY,
        'isRepeat': IS_REPEAT,
        'isOrder': IS_ORDER,
        'needValidate': NEED_VALIDATE,
        'baseUrl': BASE_URL,
        'charset': CHARSET,
    }
    threads = []
    for user in users:
        threads.append(FuckBBS(user[0], user[1], option))
    for thread in threads:
        thread.start()

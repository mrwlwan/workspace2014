#!/bin/python
# coding=utf-8

import urllib2, cookielib, sys, random, re, time, os.path
import cPickle as pickle
from getmozcookies import getCookies

############ 用户参数设置区 ###################
# 目标地址 (灌水的帖子地址)
TARGET_URL = 'http://bbs.cheabc.com/thread-141733-1-1.html'
# 灌水文本的路径,文本必须是 UTF-8 编码
TARGET_FILE = 'cheabc.txt'
# 延时(单位：秒)
DELAY = 1
# 是否重复 (True or False)
IS_REPEAT = True
# 是否按顺序，不按顺序即随机 (True or False)
IS_ORDER = True

WEBSITE_NAME = 'cheabc'
BASE_URL = 'http://bbs.cheabc.com/'
###############################################

def urlopen(url, data=None,timeout=None, opener=None):
    while 1:
        try:
            if opener:
                sock = opener.open(url, data, timeout=timeout)
            else:
                sock = urllib2.urlopen(url, data, timeout=timeout)
            if sock.getcode() == 200:
                html = sock.read()
                sock.close()
                return html
            sock.close()
        except Exception as e:
            print e

def myRawInput(tips, default=None):
    print '\n',tips,': ',
    inputStr = raw_input()
    if inputStr:
        return inputStr.strip()
    elif default!=None:
        return default
    else:
        return None

def login(cookieFile):
    cookieJar = cookielib.LWPCookieJar(cookieFile)
    cookieJar.load()
    cookie = urllib2.HTTPCookieProcessor(cookieJar)
    opener = urllib2.build_opener(cookie)
    opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.3a1pre) Gecko/20090925 Minefield/3.7a1pre GTB5')]
    urllib2.install_opener(opener)
    return cookieJar

def isLogin():
    html = urlopen(BASE_URL + 'pm.php')
    if html.find(USERNAME)>=0:
        return True
    else:
        return False

def prepareParams():
    html = urlopen(TARGET_URL)
    formAction = re.findall(r'post.php\?action=reply[^"]*', html)[0]
    formHash = re.findall(r'"formhash" value="([^"]*)"', html)[0]
    formAction = formAction.replace(r'amp;', '') + '&extra=page%3D1&replysubmit=yes&infloat=yes&handlekey=fastpost&inajax=1'
    return (BASE_URL + formAction, formHash)

def getHackStrings(targetFile):
    try:
        f = open(targetFile)
        lines = f.readlines()
        f.close()
        lines2 = [line.decode('utf8') for line in lines if len(line.strip())>2]
#        return ([urllib2.quote(line.encode('gbk')) for line in lines], lines)
        return (lines, lines2)
    except:
        return (None, None)


def getAnswer():
    html = urlopen(BASE_URL + 'ajax.php?action=updatesecqaa&inajax=1&ajaxtarget=secanswer3_menu')
    reg = '\[CDATA\[([^=]+)='
    ext = re.search(reg, html)
    if ext:
        return str(eval(ext.groups()[0]))
    else:
        return None

def action(url, formHash, content):
    answer = getAnswer()
    print answer
    urlopen(url, data='formhash=' + formHash + '&message=' + content + '&secanswer=' + answer)


if __name__ == '__main__':
    cookieJar = None
    while 1:
        if os.path.exists('cookies.txt'):
            cookieJar = login('cookies.txt')
            if isLogin():
                break;
        print u'复制 Firefox Cookie 文件...'
        getCookies(COOKIE_FILE, 'cookies.txt', WEBSITE_NAME)
        cookieJar = login('cookies.txt')
        if not isLogin():
            print u'Cookie 失效！请在Firefox里重新登录...'
            raw_input()
            sys.exit()
    print u'登录成功！'
    for cookie in cookieJar:
        print cookie
    print pickle.dumps(cookie)


#    formActionUrl, formHash = prepareParams()
#    hackStrings, orgStrings = getHackStrings(TARGET_FILE)
#    if not hackStrings:
#        print u'灌水文本有误...'
#        raw_input()
#        sys.exit()
#    print u'读取灌水文本成功!\n开始灌水...\n'

#    stringLength = len(hackStrings)
#    index = 0
#    while IS_REPEAT:
#        print time.asctime()
#        if not IS_ORDER:
#            index = random.randrange(stringLength)
#        print orgStrings[index]
#        action(formActionUrl, formHash, hackStrings[index])
#        print '*******************************\n'
#        time.sleep(DELAY)
#        index = (index+1)%stringLength

formhash=eba17d1d&username=%E5%88%AB%E9%97%AE%E6%88%91%E6%98%AF%E8%B0%81&password=123456&cookietime=2592000&loginsubmit=true


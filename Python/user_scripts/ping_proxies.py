#!bin/python
# coding=utf-8

import subprocess, re, urllib2

WEB_URL = 'http://www.proxycn.com/html_proxy/socks5-1.html'

def urlopen(url, data=None):
    while 1:
        try:
            sock = urllib2.urlopen(url, data)
            if sock.getcode() == 200:
                html = sock.read()
                return html
        except Exception as e:
            print e
            
def getProxies(url):
    html = urlopen(url)
    reg = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,4})'
    proxies = re.findall(reg, html)
    return list(set(proxies))

def pingProxy(proxy):
    command = 'ping -w 500 ' + proxy[0]
    popen = subprocess.Popen(command, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    stdout = popen.stdout
    if stdout:
        stdoutString = stdout.read()
        reg1 = r'Average = (\d*)ms'
        reg2 = r'Lost = (\d*)'
        lost = re.findall(reg2, stdoutString)
        if not int(lost[0]):
            avgTime = re.findall(reg1, stdoutString)
            if avgTime and int(avgTime[0])<=500:
                return int(avgTime[0])
    return None
    
def getLocal(proxy):
    html = urlopen('http://www.ip.cn/getip.php?action=queryip&ip_url=%s' % proxy[0])
    reg = ur'来自：([^ <]+)'.encode('gbk')
    locales = re.findall(reg, html)
    if locales:
        return locales[0]
    return ''


if __name__ == '__main__':
    print u'提取 proxies 中...'
    proxies = getProxies(WEB_URL)
    print u'一共提取到',len(proxies),u'个 proxies'
    myProxies = []
    for proxy in proxies[:1]:
        print 'ping', proxy[0],
        avgTime = pingProxy(proxy)
        print '/',avgTime,'ms',
        if avgTime:
            local = getLocal(proxy)
            print local
            proxy = list(proxy) + [avgTime, local]
            myProxies.append(proxy)
        else:
            print '\r'
    myProxies.sort(key=lambda x:x[2])
    f = open(u'C:/Documents and Settings/Administrator/桌面/ping_proxy.txt'.encode('gbk'), 'w')
    for proxy in myProxies:
        f.write(' '.join([str(item) for item in proxy]))
        f.write('\n')
    print u'Done!'





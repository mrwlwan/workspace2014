# coding=utf8

import kisopener
import traceback, re, sys, time, getpass, os


# 创建cookide文件夹
if not os.path.exists('cookies'):
    os.mkdir('cookies')


class Taobao:
    def __init__(self, username):
        self.username = username
        cookie_path = 'cookies/%s.txt' % username
        self._opener = kisopener.Opener(cookie_path=cookie_path)
        self._opener.set_headers({'User-agent': 'CECT A706 CECT A706'})
        #self._opener.set_headers({'User-agent': 'Opera/9.8(Android;Opera Mini/7.0.31907/28.2690;U;zh)Presto/2.8.119 Version/11.0'})
        self._encoding = 'utf8'
        self._timeout = 5

    def fetch(self, *args, **kwargs):
        kwargs['timeout'] = self._timeout
        while 1:
            try:
                 return self._opener.urlopen(*args, **kwargs).read().decode(self._encoding, 'ignore')
            except:
                 traceback.print_exc()

    def clean(self, url):
        """ 将"&amp;"转换为"&". """
        return url.replace('&amp;', '&')

    def form_dict(self, content, ignore=[]):
        ignore = set(ignore)
        reg = re.compile(r"""<input[^>]*?name=['"]([^'"]*)['"][^>]*value=['"]([^'"]*)""")
        return dict([(key, value) for key, value in reg.findall(content) if key not in ignore])

    def _login_sms_code(self, content):
        data = self.form_dict(content)
        url = 'http://login.m.taobao.com/send_code.htm?sid={sid}&_input_charset=utf-8'.format(**data)
        content = self.fetch(url, data=data)
        print('已经发送短信, 注意查收...')
        sms_code = input('请输入获得的短信验证码: ').strip()
        data = self.form_dict(content, ignore=['event_submit_do_gen_check_code'])
        data['checkCode'] = sms_code
        url = 'http://login.m.taobao.com/login_check.htm?sid={sid}&_input_charset=utf-8'.format(**data)
        return self.fetch(url, data=data)

    def _login_check_code(self, content):
        self.log(content)
        data = self.form_dict(content)
        data['TPL_username'] = self.username
        img_src = re.search(r'http://regcheckcode[^"]+', content).group()
        img_src = re.sub(r'\n|amp;', '', img_src)
        f = open('code.jpg', 'bw')
        f.write(self._opener.urlopen(img_src).read())
        f.close()
        subprocess.Popen('rundll32.exe   %Systemroot%\System32\shimgvw.dll,ImageView_Fullscreen '+os.path.abspath('code.jpg'))
        code = input('请输入验证码: ')
        data['TPL_checkcode'] = code.strip()
        return self.fetch('http://login.m.taobao.com/login.htm?sid={sid}&_input_charset=utf-8'.format(**data), data=data)

    def check_logined(self):
        content = self.fetch('http://my.m.taobao.com/my_taobao.htm')
        if content.find('我的淘宝')>=0:
            self._opener.save_cookies()
            return True
        return False

    def login(self):
        if self.check_logined():
            print('Cookie 登录成功!')
            return
        login_page = self.fetch('http://login.m.taobao.com/login.htm')
        data = self.form_dict(login_page)
        data.update({
            'TPL_username': self.username,
            'TPL_password': getpass.getpass('请输入密码: ').strip(),
        })
        content = self.fetch('https://login.m.taobao.com/login.htm?_input_charset=utf-8&sid={sid}'.format(**data), data=data)
        if content.find('登录保护')>=0:
            content = self._login_sms_code(content)
        if content.find('验证码')>=0:
            content = self._login_check_code(content)
        if self.check_logined():
            print('登录成功!')
        else:
            print('登录失败!')
            sys.exit()

    def action(self):
        reg = re.compile(r'(?:点击抢红包|红包等你拿!)</a><center><a href="([^"]+)')
        url_reg = re.compile(r'http://msp\.m\.taobao\.com/awd/break\.htm\?sid[^"]+')
        url_reg2 = re.compile(r'(http://msp\.m\.taobao\.com/awd/award\.htm[^"]+)">\s*活动首页')
        msg_reg = re.compile(r'<div class="center">\s+<div class="detail center">\s+<[^>]+>\s*([^<]+)')
        content = self.fetch('http://m.taobao.com')
        url = self.clean(reg.search(content).group(1))
        count =0
        while 1:
            try:
                print('红包数: %s' % count)
                content = self.fetch(url)
                time.sleep(4)
                if content.find('抓蝴蝶')<0:
                    return
                data = self.form_dict(content)
                data['event_submit_do_award'] = '抓蝴蝶'
                url = self.clean(url_reg.search(content).group())
                content = self.fetch(url, data=data)
                url_obj = url_reg2.search(content)
                if not url_obj:
                    self.msg('单击太过频繁!')
                    self.log(content)
                    return
                url = self.clean(url_obj.group(1))
                time.sleep(4)
                msg_search = msg_reg.search(content, url_obj.end())
                self.msg(msg_search.group(1).strip())
                if content.find('再来一次', msg_search.end())<0:
                    self.msg('抢到红包')
            except:
                traceback.print_exc()
                self.log(content)
                return
                self.msg(re.search(r'<span class="red">([^<]+)', content).group(1))
                #count += 1
                #if count >=3:
                    #return


    def log(self, text):
        with open('log.html', 'w', newline='\n', encoding='utf8') as f:
            f.write(text)

    def msg(self, text):
        print('%s %s' % (time.strftime('%Y-%m-%d %H:%M:%S'), text))


if __name__ == '__main__':
    username = input('请输入用户名: ')
    taobao = Taobao(username=username)
    taobao.login()
    taobao.action()

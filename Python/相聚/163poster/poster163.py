# coding=utf8

import mylib
import time, re, random, threading, json, sys, os

class Poster163(threading.Thread):
#class Poster163():
    global_config = {}
    post_contents = {}
    targets = {}

    def __init__(self, auth, global_config, person_config):
        super().__init__()
        self.auth = auth
        self.cookie_file = 'cookies/%s.txt' % auth['username']
        self.is_cookie_exists = self._check_cookie()
        if not Poster163.global_config:
            Poster163.global_config = global_config
        self.person_config = person_config
        self.opener = mylib.Opener(has_cookie=True, cookie_filename=self.cookie_file)
        self.logined = False
        self.login()

        self.post_contents = self._post_contents()
        self.targets = self._targets()

    def _check_cookie(self):
        return os.path.exists(self.cookie_file)

    def _post_contents(self):
        path = self.person_config['target_filename']
        if path in Poster163.post_contents:
            print('读取灌水文本成功.')
            return Poster163.post_contents[path]
        f = open(path)
        contents_list = [line[:-1] for line in f]
        f.close()
        print('读取灌水文本成功.')
        return contents_list

    def _fetch_title(self, url):
        reg = re.compile(br'<title>(.+?)</title>')
        content = self.opener.open(url)
        search_obj = reg.search(content)
        return search_obj and search_obj.groups()[0].decode(Poster163.global_config['charset']) or None

#http://bbs.lady.163.com/bbs/pingming/228165273.html
#http://3g.163.com/bbs/bbs_lady/bbs/pingming/228165273.html
    def _targets(self):
        print('正在分析目标网址...')
        reg = re.compile(r'(?P<bbs>[^\./:]+?)\.(?P<board>[^\.]+?)\.163\.com\/bbs\/(?P<boardid>[^\/]+?)\/(?P<articleid>[^\.]+?)\.html')
        target_urls = self.person_config['target_urls'].split(',')
        targets = []
        for target_url in target_urls:
            target_url = target_url.strip()
            if target_url in Poster163.targets:
                targets.append(Poster163.targets[target_url])
                continue
            search_obj = reg.search(target_url)
            if not search_obj:
                print('网址转换失败')
                sys.exit()
            url = 'http://3g.163.com/bbs/%(bbs)s_%(board)s/bbs/%(boardid)s/%(articleid)s.html' % search_obj.groupdict()
            post_url = 'http://3g.163.com/bbs/%(bbs)s_%(board)s/3g/replydo.do' % search_obj.groupdict()
            title = self._fetch_title(url)
            temp_dict = {
                'url': url,
                'title': title,
                'post_url': post_url,
                'boardid': search_obj.groupdict()['boardid'],
                'articleid': search_obj.groupdict()['articleid']
            }
            targets.append(temp_dict)
            Poster163.targets[target_url] = temp_dict
        print('分析结果: %s' % targets)
        return targets

    def _check_post_success(self, content):
        return content[-100:].find(Poster163.global_config['post_check_data'].encode(Poster163.global_config['charset'])) >=0

    def check_login(self):
        if self.logined:
            print('你已经登录')
            return True
        global_config = Poster163.global_config
        check_url = global_config['check_url']
        charset = global_config['charset']
        check_data = global_config['check_data'].encode(charset)
        content = self.opener.open(check_url)
        if content.find(check_data) >= 0:
            self.logined = True
            self.opener.cookiejar.save()
            return True
        else:
            self.logined = False
            return False

    def login(self):
        if self.logined:
            print('你已经登录')
            return True
        if self.is_cookie_exists and self.check_login():
            pass
        else:
            username, password = (self.auth['username'], self.auth['password'])
            global_config = Poster163.global_config
            login_url = Poster163.global_config['login_url']
            post_data = {
                global_config['login_user_key']: username,
                global_config['login_password_key']: password
            }
            if global_config['pre_login_data']:
                post_data.update(json.loads(global_config['pre_login_data']))
            print('用户: %s 正在登录...' % username)
            content = self.opener.open(login_url, data=post_data)
            self.check_login()
        if self.logined:
            print('登录成功 :)')
            return True
        else:
            print('登录失败, 请检查用户名或者密码是否正确 :(')
            return False

    def post(self, target_index, content_index):
        #post_url = 'http://3g.163.com/bbs/bbs_lady/3g/replydo.do'
        target = self.targets[target_index]
        post_url = target['post_url']
        content = self.post_contents[content_index]
        post_data = {
            'title': target['title'],
            'boardid': target['boardid'],
            'articleid': target['articleid'],
            'content': content
        }
        response_content = self.opener.open(post_url, post_data)
        success = self._check_post_success(response_content)
        success_string = success and '成功' or '失败'
        print('####################################################################')
        print('时间: %s' % time.asctime())
        print('用户: %s' % self.auth['username'])
        print('目标: %s' % target['url'])
        print('内容: %s' % content)
        print('状态: %s' % success_string)
        print('####################################################################')
        return success


    def run(self):
        is_repeat = int(self.person_config['is_repeat'])
        is_random = int(self.person_config['is_random'])
        delay = int(self.person_config['delay'])
        fail_delay = int(Poster163.global_config['fail_delay'])
        contents_length = len(self.post_contents)
        targets_length = len(self.targets)
        content_index = 0
        while 1:
            for target_index in range(targets_length):
                if is_repeat and is_random:
                    content_index = random.randint(0, contents_length-1)
                success = self.post(target_index, content_index)
                if not success:
                    print('用户: %s 回复出错, 将在%s秒后继续...' % (self.auth['username'], fail_delay))
                time.sleep(success and delay or fail_delay)
            if not is_repeat and content_index>=contents_length-1:
                break
            content_index = content_index < contents_length-1 and content_index +1 or 0

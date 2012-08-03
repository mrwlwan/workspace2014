# coding=utf8

from lib import mylib
import time, re, random, threading, json, sys, os

class Poster(threading.Thread):
    global_config = {}
    # 灌水内容, {file_name: [content_lines]}
    post_contents = {}
    # 目标网址, {target_url: {config}}
    targets = {}
    cond = threading.Condition()
    # 控制暂停或者重新开始线程运行
    is_action = True

    @classmethod
    def set_action(cls, value):
        cls.is_action = value

    @classmethod
    def get_action(cls):
        return cls.is_action

    def __init__(self, auth, global_config, person_config, login=True, prepare=True):
        """ 参数 auth: {'username': username, 'password': password} """
        super().__init__()
        self.auth = auth
        self.cookie_file = 'cookies/%s.txt' % auth['username']
        self.is_cookie_exists = self._check_cookie()
        if not Poster.global_config:
            Poster.global_config = global_config
        self.person_config = person_config
        self.opener = mylib.Opener(has_cookie=True, cookie_filename=self.cookie_file)
        self.logined = False
        # 控制当前线程的终止, 当线程开始运行后设置 started = False 即可结束当前线程
        self.started = False

        if login:
            self.login()
        if prepare:
            self.post_contents = self._post_contents()
            self.targets = self._targets()

    def _check_cookie(self):
        return os.path.exists(self.cookie_file)

    def _post_contents(self):
        path = self.person_config['target_filename']
        content_list = []
        if path in Poster.post_contents:
            content_list =  Poster.post_contents[path]
        else:
            f = open(path, encoding='utf8')
            contents_list = [line.rstrip() for line in f]
            f.close()
        print('读取灌水文本成功.')
        return contents_list

    def _targets(self):
        print('正在分析目标网址...')
        target_urls = self.person_config['target_urls'].split(' ')
        targets = []
        for target_url in target_urls:
            target_url = target_url.strip()
            if target_url in Poster.targets:
                targets.append(Poster.targets[target_url])
                continue
            html = self.opener.open(target_url)
            temp_dict = {}
            for reg_string in json.loads(Poster.global_config['post_data_regs'].replace('\\', '\\\\')):
                reg = re.compile(reg_string.encode(Poster.global_config['charset']))
                search_obj = reg.search(html)
                if search_obj:
                    temp_dict['post_data'] = search_obj.groupdict()
            temp_dict.update({
                'url': target_url,
                'post_url': Poster.global_config['post_url'],
            })
            targets.append(temp_dict)
            Poster.targets[target_url] = temp_dict
        print('分析结果: %s' % targets)
        return targets

    def _check_post_success(self, content):
        return content.find(Poster.global_config['post_check_data'].encode(Poster.global_config['charset'])) >=0

    def set_person_config(self, person_config):
        self.person_config = person_config

    def is_logined(self):
        return self.logined

    def check_login(self):
        if self.logined:
            print('你已经登录')
            return True
        global_config = Poster.global_config
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

    def login(self, data={}):
        if self.logined:
            print('你已经登录')
            return True
        if self.is_cookie_exists and self.check_login():
            pass
        else:
            username, password = (self.auth['username'], self.auth['password'])
            global_config = Poster.global_config
            login_url = Poster.global_config['login_url']
            post_data = {
                global_config['login_user_key']: username,
                global_config['login_password_key']: password
            }
            print(global_config['pre_login_data'])
            if global_config['pre_login_data']:
                post_data.update(json.loads(global_config['pre_login_data']))
            post_data.update(data)
            print('用户: %s 正在登录...' % username)
            content = self.opener.open(login_url, data=post_data)
            print(content.decode(global_config['charset']))
            self.check_login()
        self.opener.cookiejar.save()
        if self.logined:
            print('登录成功 :)')
            return True
        else:
            print('登录失败, 请检查用户名或者密码是否正确 :(')
            return False

    def prepare(self):
        """ post 或者 run 之前, 必须先运行 prepare. """
        self.post_contents = self._post_contents()
        self.targets = self._targets()

    def post(self, target_index, content_index):
        target = self.targets[target_index]
        post_url = target['post_url']
        content = self.post_contents[content_index]
        post_data = json.loads(Poster.global_config['pre_post_data'])
        post_data.update(target['post_data'])
        post_data['content'] = content
        response_content = self.opener.open(post_url, post_data)
        print(response_content)
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

    def get_login_code(self):
        if self.global_config['login_code_key']:
            return self.opener.open(self.global_config['login_code_url'])
        return None

    def run(self):
        is_repeat = int(self.person_config['is_repeat'])
        is_random = int(self.person_config['is_random'])
        delay = int(self.person_config['delay'])
        fail_delay = int(Poster.global_config['fail_delay'])
        contents_length = len(self.post_contents)
        targets_length = len(self.targets)
        content_index = 0
        self.started = True
        cond = Poster.cond
        while self.started:
            for target_index in range(targets_length):
                if not Poster.is_action:
                    cond.acquire()
                    cond.notify()
                    cond.wait()
                    cond.release()
                    break
                if is_repeat and is_random:
                    content_index = random.randint(0, contents_length-1)
                success = self.post(target_index, content_index)
                if not success:
                    print('用户: %s 回复出错, 将在%s秒后继续...' % (self.auth['username'], fail_delay))
                time.sleep(success and delay or fail_delay)
            if not is_repeat and content_index>=contents_length-1:
                break
            content_index = content_index < contents_length-1 and content_index +1 or 0

    def stop(self):
        """ 结束当前线程的运行. """
        self.started = False

    @classmethod
    def pause(cls):
        """ 暂停灌水. """
        cls.is_action = False

    @classmethod
    def resume(cls):
        """ 重新开始灌水. """
        cls.cond.acquire()
        cls.cond.notify_all()
        cls.cond.release()
        cls.is_action = True

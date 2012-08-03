# coding=utf8

import mylib
import time, re, random, threading

class Poster(threading.Thread):
    last_cfg_filename = ''
    last_target_filename = ''
    last_text_list = []
    last_post_datas = {}

    def __init__(self, cfg_filename, configs):
        super().__init__()
        if not Poster.last_cfg_filename == cfg_filename:
            global_configs = mylib.get_configs(cfg_filename, encoding='utf8')['global']
            self._init_configs(Poster, global_configs)
            Poster.last_cfg_filename = cfg_filename
        self._init_configs(self, configs)
        self.opener = mylib.Opener(has_cookie=True, cookie_filename=self.cookie_filename)

        self.post_datas = {}
        self.text_list = []
        print('ok')

        self._login()
        self._prepare()

    def _init_configs(self, obj, configs):
        for key in configs:
            if key in ('login_url', 'check_url', 'check_data', 'post_url', 'post_content_key', 'target_filename', 'charset', 'login_data', 'cookie_filename', 'login_user_key', 'login_password_key'):
                setattr(obj, key, configs[key])
            elif key in ('delay', 'is_repeat', 'is_random', 'timeout'):
                setattr(obj, key, int(configs[key]))
            elif key in ('post_data_regs', 'pre_post_data', 'pre_login_data'):
                setattr(obj, key, eval(configs[key]))
            elif key in ('target_urls',):
                temp = configs[key].split(',')
                temp = [item.strip() for item in temp]
                setattr(obj, key, list(set(temp)))
            elif key in ('auth',):
                temp = configs[key].split(':')
                temp = [item.strip() for item in temp]
                temp = {
                    self.login_user_key: temp[0],
                    self.login_password_key: temp[1]
                }
                setattr(obj, 'login_data', temp)
                setattr(obj, 'poster_name', temp[self.login_user_key])


    def _get_text_list(self):
        with open(self.target_filename, encoding='utf8') as f:
            text = f.read().strip()
            f.close()
            temp =  text.split('\n')
            Poster.last_target_filename = self.target_filename
            Poster.last_text_list = temp
            return temp

    def _get_data(self, url, encoding=None):
        if not self.post_data_regs:
            return {}
        encoding = encoding and encoding or self.charset
        html = self.opener.open(url, decoder=encoding)
        temp = {}
        for reg in self.post_data_regs:
            search_obj = re.search(reg, html)
            if search_obj:
                temp.update(search_obj.groupdict())
        return temp

    def _prepare(self):
        if self.target_filename == Poster.last_target_filename:
            self.text_list = Poster.last_text_list
        else:
            self.text_list = self._get_text_list()
        for url in self.target_urls:
            if url in Poster.last_post_datas:
                self.post_datas[url] = Poster.last_post_datas[url]
            else:
                temp = self.pre_post_data.copy()
                temp.update(self._get_data(url))
                self.post_datas.update({
                    url: temp
                })
                Poster.last_post_datas.update({
                    url: temp
                })

    def _login(self):
        temp = self.pre_login_data.copy()
        temp.update(self.login_data)
        print(self.poster_name)
        #print(self.poster_name, end='')
        self.opener.login(self.login_url, data=temp, check_url=self.check_url, check_data=self.check_data, decoder=self.charset)
        print('login')

    def post(self, url, content):
        self.post_datas[url].update({self.post_content_key: content})
        self.opener.open(self.post_url, data=self.post_datas[url], timeout=self.timeout, decoder=self.charset)
        print('#############################')
        print(time.asctime())
        print(self.poster_name, end=':\n')
        print(url)
        print(content)

    def run(self):
        text_list = self.text_list
        text_list_len = len(text_list)
        index = 0
        while 1:
            for url in self.target_urls:
                if self.is_repeat and self.is_random:
                    index = random.randint(0,text_list_len-1)
                self.post(url, text_list[index])
                time.sleep(self.delay)
            if not self.is_repeat and index>=text_list_len-1:
                break
            index += 1

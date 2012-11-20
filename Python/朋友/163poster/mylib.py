# coding=utf8

import os, urllib.request, urllib.parse, http.cookiejar, configparser
from functools import wraps

def coroutine(func):
    @wraps(func)
    def call(*args, **kwargs):
        g = func(*args, **kwargs)
        next(g)
        return g
    return call

##########################################################################
class Config:
    config_file = 'config.cfg'
    parser = None
    sections = {}

    @classmethod
    def create_parser(cls, config_file=None):
        config_file = config_file and config_file or cls.config_file
        cls.parser = configparser.ConfigParser('', dict, True)
        cls.parser.read(config_file, encoding='utf8')
        return cls.parser

    def __init__(self, config_file=None):
        config_file = config_file and config_file or Config.config_file
        Config.create_parser(config_file)

    def get_parser(self):
        return Config.parser

    def get_sections(cls):
        if not Config.sections:
            for section in Config.parser.sections():
                Config.sections[section] = dict(Config.parser.items(section))
        return Config.sections

    def update_section(self, section, dict_values):
        Config.sections[section].update(dict_values)
        for option, value in dict_values.items():
            Config.parser.set(section, *(option, value))

    def update_sections(self, dict_sections):
        for section in dict_sections:
            self.update_section(section, dict_sections[section])

    def save(self):
        f = open(Config.config_file, 'w')
        Config.parser.write(f)
        f.close()


def get_configs(filename, encoding='utf8'):
    configs = {}
    parser = configparser.ConfigParser()
    parser.read(filename, encoding=encoding)
    for section in parser.sections():
        configs[section] = dict(parser.items(section))
    return configs

##########################################################################

class Opener:
    def __init__(self, has_cookie=False, headers=[], cookie_filename=None):
        self.opener = urllib.request.build_opener()
        self.cookiejar = None
        self._cookie_file_exists = False
        if has_cookie:
            if cookie_filename:
                self.cookiejar = http.cookiejar.LWPCookieJar(cookie_filename)
                if os.path.exists(cookie_filename):
                    self.cookiejar.load()
                    self._cookie_file_exists = True
            else:
                self.cookiejar = http.cookiejar.CookieJar()
            cookie_handler = urllib.request.HTTPCookieProcessor(self.cookiejar)
            self.opener.add_handler(cookie_handler)
        #self.opener.addheaders = [('User-agent', 'Mozilla/9.0 (Windows NT 5.1; rv:5.0) Gecko/20121212 Firefox/9.0')] + headers
        self.opener.addheaders = [('User-agent', 'iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us')] + headers

    def open(self, url, data=None, timeout=None, success=True, decoder=None):
        if data and not isinstance(data, bytes):
            data = urllib.parse.urlencode(data).encode('ascii')
        while 1:
            try:
                sock = self.opener.open(url, data, timeout)
                if sock.getcode() == 200:
                    html = sock.read()
                    if decoder:
                        html = html.decode(decoder, 'ignore')
                    sock.close()
                    return html
                sock.close()
            except urllib.request.HTTPError as e:
                if e.code == 404:
                    print('404 http error')
                    return decoder and '' or b''
            except Exception as e:
                print(e)
            if not success:
                return None

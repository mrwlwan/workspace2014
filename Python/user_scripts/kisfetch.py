# coding=utf8

from kisopener import Opener
from urllib.parse import urlparse
from argparse import ArgumentParser, FileType
import json, cmd, shlex, os.path, traceback, sys, re

class Action:
    def __init__(self):
        arg_parser = ArgumentParser(description='Fetch the web page.')
        arg_parser.add_argument('url', type=str, help='目标链接. 如果是"-" 表示上一次的请求结果.')
        arg_parser.add_argument('-t', '--timeout', type=float, help='HTTP request timout.')
        arg_parser.add_argument('-p', '--param', type=self.str_or_json, help='Query string. 如: q=abc&hl=en; 或者{"a": "abc", "hl": "en"}; 又或者[("a", "abc"), ("hl", "en")].')
        arg_parser.add_argument('-d', '--data', type=self.str_or_json, help='Post data. 如: q=abc&hl=en; 或者{"a": "abc", "hl": "en"}; 又或者[("a", "abc"), ("hl", "en")].')
        arg_parser.add_argument('-x', '--proxies', type=json.loads, default={}, help='代理. 如: {"http": "x.x.x.x:xx", "https": "x.x.x.x:xx"}.')
        arg_parser.add_argument('-r', '--headers', type=json.loads, default={}, help='HTTP request headers. 如: {"http": "x.x.x.x:xx", "https": "x.x.x.x:xx"}.')
        arg_parser.add_argument('-e', '--encoding', type=str, default='utf8', help='URL 编码.')
        arg_parser.add_argument('-n', '--contentencoding', type=str, help='Content 编码.')
        arg_parser.add_argument('-c', '--cookies', type=json.loads, help='Cookie.如: {...}, 或者 [{..}, {...}, ...].')
        arg_parser.add_argument('-f', '--cookiefile', type=str, default=None, help='外部cookie文件.')
        arg_parser.add_argument('-o', '--out', nargs='?', const='log.txt', help='输出文件')
        arg_parser.add_argument('-s', '--search', type=str, help='搜索字符串.')
        arg_parser.add_argument('--re', type=str, help='正则搜索字符串.')

        arg_parser.add_argument('-i', '--info', action='store_true', help='显示相关的 HTTP Request 和 Response 信息.')
        arg_parser.add_argument('-w', '--noview', action='store_true', help='不打印网页源码.')
        arg_parser.add_argument('--nocontent', action='store_true', help='不读取网页源码. 设置此参数将默认 --noview, 并且可能使-o参数失效.')
        self.arg_parser = arg_parser
        self.opener = Opener()
        self.last_content = None

    def str_or_json(self, arg):
        if (arg.startswith('[') and arg.endswith(']')) or (arg.startswith('{') and arg.endswith('}')):
            return json.loads(arg)
        return arg

    def do_cookiefile(self, args):
        self.opener.set_cookie_path(args.cookiefile)

    def do_cookies(self, args):
        if isinstance(args.cookies, dict):
            opener.set_cookies(*args.cookies)
        else:
            opener.set_cookies(**args.cookes)

    def do_urlopen(self, args):
        kwargs = dict([(key, getattr(args, key)) for key in ('param', 'data', 'headers', 'proxies', 'timeout', 'encoding')])
        url = args.url
        # 默认http
        if not urlparse(url).scheme:
            url = 'http://%s' % url
        self.last_content = None
        self.opener.clear()
        self.opener.urlopen(url, **kwargs)

    def do_readcontent(self, args):
        self.last_content = self.opener.last_response.read().decode(args.contentencoding or 'utf8')

    def do_printcontent(self, args):
        print(self.last_content)

    def do_search(self, args, *pos):
        print('搜索文本: %s' % args.search)
        position = self.last_content.find(args.search, *pos)
        if position>=0:
            print('首出现位置: %s' % position)
            print('出现次数: %s' % self.last_content.count(args.search, *pos))
        else:
            print('位置: 未找到.')
            print('出现次数: 0')

    def do_re_search(self, args, flag=0, *pos):
        reg = re.compile(args.re, flag)
        print('正则表达式: %s' % args.re)
        pos = []
        group = []
        groups = []
        groupdicts = []
        for search_obj in reg.finditer(self.last_content, *pos):
            pos.append((search_obj.start(), search_obj.end()))
            group.append(search_obj.group())
            groups.append(search_obj.groups())
            groupdicts.append(search_obj.groupdict())
        print('出现次数: %s' % len(pos))
        print('位置: %s' % pos)
        print('Group: %s' % group)
        print('Groups: %s' % groups)
        print('Groupdict: %s' % groupdicts)

    def do_log(self, args, contents, mode='w'):
        filepath = args.out
        f = open(filepath, mode, encoding='utf8')
        'a' in mode and f.write('\n\n')
        for item in contents:
            f.write(item)
        print('成功写入文件 %s.' % filepath)
        f.close()

    def execute(self, argv=None):
        try:
            # 处理argv.
            if argv == None:
                args = self.arg_parser.parse_args()
            else:
                args = self.arg_parser.parse_args(argv)
            #args = self.arg_parser.parse_args(argv)
            # 处理cookie 文件.
            if args.cookiefile:
                self.do_cookiefile(args)
            # 处理 Request cookies.
            if args.cookies:
                self.do_cookies(args)
            # 处理HTTP request 的其它参数.
            if not args.url == '-':
                self.do_urlopen(args)
            if not args.nocontent and self.opener.last_response and not self.last_content:
                self.do_readcontent(args)
            if self.last_content:
                if not args.noview:
                    self.do_printcontent(args)
                if args.search:
                    self.do_search(args)
                if args.re:
                    self.do_re_search(args)
                if args.out:
                    self.do_log(args, [self.last_content])
        except:
            traceback.print_exc()


class Shell(cmd.Cmd):
    intro = 'Welcome...\n'
    prompt ='> '

    def __init__(self, actoin):
        self.action = action
        super().__init__()

    def log(self, arg, contents):
        args, mode = self.parse_args('- -o %s' % arg)
        self.action.do_log(args, contents, mode and mode[0] or 'w')

    def parse_args(self, arg, pos=1):
        """ pos: 附加参数起始位置."""
        argv = shlex.split(arg)
        pos += 2
        return self.action.arg_parser.parse_args(argv[0:pos]), argv[pos:]

    def default(self, arg):
        self.action.execute(shlex.split(arg))

    def do_savecookies(self, cookie_path):
        self.action.opener.save_cookies(cookie_path)
        print('成功保存cookies到 %s' % cookie_path)

    def do_info(self, arg):
        last_response = self.action.opener.last_response
        if last_response:
            infos =  last_response.info()
            for name, value in infos.items():
                print('%s:\t%s' % (name, value))
        else:
            print('No response.')

    def do_log(self, arg):
        if arg and self.action.last_content:
            self.log(arg, [self.action.last_content])
        else:
            print('没内容可写入.')

    def do_loginfo(self, arg):
        last_response = self.action.opener.last_response
        if arg and last_response:
            infos =  last_response.info()
            self.do_log(arg, ('%s:\t%s\n' % (name, value) for name, value in infos.items()), )
        else:
            print('No response.')

    def do_set(self, arg):
        self.action.last_content = arg

    def do_search(self, arg):
        args, pos = self.parse_args('- -s %s' % arg)
        self.action.do_search(args, *pos)

    def do_re(self, arg):
        args, extra = self.parse_args('- --re %s' % arg)
        flag = extra[0] if extra else 0
        pos = extra[1:3]
        self.action.do_re_search(args, flag, *pos)

    def do_help(self, arg):
        if arg == 'usage':
            self.action.arg_parser.print_usage()
        else:
            self.action.arg_parser.print_help()
        print('\n')

    def emptyline(self):
        pass

    def do_exit(self, arg):
        return True

    def do_quit(self, arg):
        return True

if __name__ == '__main__':
    action = Action()
    if len(sys.argv)>1:
        action.execute()
        sys.exit()
    shell = Shell(action)
    shell.cmdloop()
